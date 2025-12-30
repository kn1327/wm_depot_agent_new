"""Main Streamlit App for WM Depot CB% Agent."""

import streamlit as st
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from agents.query_generator import QueryGenerator
from agents.item_recommender import ItemRecommender
from agents.root_cause_analyzer import RootCauseAnalyzer
from connectors.bigquery_connector import BigQueryConnector
from config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="WM Depot CB% Agent",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS styling
st.markdown("""
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_clients():
    """Initialize BigQuery and agents (cached)."""
    try:
        settings = get_settings()
        bq_client = BigQueryConnector()
        query_gen = QueryGenerator(project_id=settings.gcp_project_id)
        item_recommender = ItemRecommender()
        root_cause_analyzer = RootCauseAnalyzer()
        return {
            "bq": bq_client,
            "query_gen": query_gen,
            "recommender": item_recommender,
            "analyzer": root_cause_analyzer,
        }
    except Exception as e:
        st.error(f"❌ Failed to initialize clients: {str(e)}")
        logger.error(f"Initialization error: {str(e)}", exc_info=True)
        return None


def safe_format(value, decimals=2):
    """Safely format numeric values."""
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return "0.00"
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return "0.00"


def render_metrics_dashboard(depot: str, clients: dict, days: int = 30):
    """Render the metrics dashboard."""
    try:
        query_gen = clients["query_gen"]
        bq = clients["bq"]

        # Get metrics
        sql = query_gen.generate_cb_trend_query(depot, days)
        results = bq.execute_query(sql)

        if not results or len(results) == 0:
            st.warning(f"No data found for depot {depot} in the last {days} days.")
            return

        # Extract current metrics
        current = results[0]
        cb_values = [r.get("CB_PERCENT", 0) for r in results if r.get("CB_PERCENT")]

        # Calculate statistics
        current_cb = current.get("CB_PERCENT", 0)
        avg_cb = np.mean(cb_values) if cb_values else 0
        max_cb = max(cb_values) if cb_values else 0
        min_cb = min(cb_values) if cb_values else 0

        # Display metric cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current CB%", f"{safe_format(current_cb, 2)}%", 
                     delta=f"{safe_format(current_cb - avg_cb, 2)}pp from avg")
        with col2:
            st.metric("Avg CB%", f"{safe_format(avg_cb, 2)}%", 
                     delta=f"{len(results)} days")
        with col3:
            st.metric("Max CB%", f"{safe_format(max_cb, 2)}%")
        with col4:
            st.metric("Min CB%", f"{safe_format(min_cb, 2)}%")

        # Create DataFrame for visualization
        df = pd.DataFrame(results)
        if "DELIVERY_DATE" in df.columns:
            df["DELIVERY_DATE"] = pd.to_datetime(df["DELIVERY_DATE"])
            df = df.sort_values("DELIVERY_DATE")

        # CB% Trend Chart
        st.subheader("📈 CB% Trend")
        if "DELIVERY_DATE" in df.columns and "CB_PERCENT" in df.columns:
            chart_data = df[["DELIVERY_DATE", "CB_PERCENT"]].copy()
            chart_data.columns = ["Date", "CB%"]
            st.line_chart(chart_data.set_index("Date"))

        # Detailed metrics table
        st.subheader("📊 Detailed Metrics")
        display_cols = [
            "DELIVERY_DATE",
            "CB_PERCENT",
            "FULFILLMENT_RATE",
            "ENTITLEMENT_RATE",
            "CATCHMENT_ORDER_CNT",
            "ENTITLED_ORDER_CNT",
            "ATTAINED_ORDER_CNT",
        ]
        display_df = df[[col for col in display_cols if col in df.columns]].head(20)
        st.dataframe(display_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading metrics: {str(e)}")
        logger.error(f"Metrics error: {str(e)}", exc_info=True)


def render_recommendations(depot: str, clients: dict, days: int = 7):
    """Render item recommendations."""
    try:
        query_gen = clients["query_gen"]
        bq = clients["bq"]
        recommender = clients["recommender"]

        # Get missing items
        missing_items_sql = query_gen.generate_missing_items_query(depot, days)
        missing_items = bq.execute_query(missing_items_sql)

        if not missing_items:
            st.info("No missing items found for this depot.")
            return

        # Get current metrics
        metrics_sql = query_gen.generate_cb_trend_query(depot, 7)
        metrics = bq.execute_query(metrics_sql)

        if not metrics:
            st.warning("No metrics found for this depot.")
            return

        current = metrics[0]
        current_cb = current.get("CB_PERCENT", 0)
        catchment_count = current.get("CATCHMENT_ORDER_CNT", 0)
        entitled_count = current.get("ENTITLED_ORDER_CNT", 0)

        # Convert items for recommender
        converted_items = [
            {
                "catlg_item_id": item.get("CATLG_ITEM_ID"),
                "product_name": item.get("PROD_NM"),
                "category": item.get("CATEGORY"),
                "order_count": item.get("ORDER_CNT", 0),
                "substitution_count": item.get("SUBSTITUTION_CNT", 0),
                "substitution_rate": item.get("SUBSTITUTION_RATE", 0),
                "avg_qty_per_order": item.get("AVG_QTY_PER_ORDER", 1.0),
            }
            for item in missing_items
        ]

        # Get recommendations
        recommendations = recommender.recommend_items(
            missing_items=converted_items,
            current_cb_percent=current_cb,
            current_catchment_count=catchment_count,
            current_entitled_count=entitled_count,
            top_n=10,
        )

        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current CB%", f"{safe_format(current_cb, 2)}%")
        with col2:
            combined_lift = sum(r.cb_lift_percent for r in recommendations)
            st.metric("Combined CB Lift", f"+{safe_format(combined_lift, 2)}pp")
        with col3:
            total_orders = sum(r.estimated_additional_orders for r in recommendations)
            st.metric("Additional Orders", f"{int(total_orders)}")

        # Display recommendations
        st.subheader("⭐ Top Recommendations")
        if recommendations:
            rec_data = []
            for rec in recommendations[:10]:
                rec_data.append({
                    "Product": rec.product_name,
                    "Category": rec.category,
                    "CB Lift": f"+{safe_format(rec.cb_lift_percent, 3)}pp",
                    "Current Orders": int(rec.current_order_count),
                    "Sub Rate": f"{safe_format(rec.substitution_rate, 1)}%",
                    "Confidence": f"{safe_format(rec.confidence_score * 100, 0)}%",
                })
            rec_df = pd.DataFrame(rec_data)
            st.dataframe(rec_df, use_container_width=True)
        else:
            st.info("No recommendations available.")

    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        logger.error(f"Recommendations error: {str(e)}", exc_info=True)


def render_qa_tab(depot: str, clients: dict, days: int = 30):
    """Render Q&A analysis tab."""
    try:
        query_gen = clients["query_gen"]
        bq = clients["bq"]

        st.subheader("💬 Ask a Question")
        st.write("Examples: 'What is the CB% trend?', 'Why did CB% drop?', 'What items are we missing?'")

        question = st.text_area("Your question:", height=100)

        if st.button("🚀 Analyze"):
            if not question.strip():
                st.warning("Please enter a question.")
                return

            with st.spinner("🔍 Analyzing your question..."):
                try:
                    # Generate SQL from question
                    sql, qtype, metadata = query_gen.generate_query_from_question(
                        question=question,
                        depot=depot,
                        days_lookback=days,
                    )

                    st.success(f"✅ Question Type: {qtype.value}")
                    st.info(f"📝 Analysis: {metadata['description']}")

                    # Display generated SQL
                    with st.expander("🔍 Generated SQL"):
                        st.code(sql, language="sql")

                    # Execute and display results
                    st.subheader("📊 Results")
                    results = bq.execute_query(sql)

                    if results:
                        results_df = pd.DataFrame(results)
                        st.dataframe(results_df, use_container_width=True)
                        st.success(f"✅ Found {len(results)} rows")
                    else:
                        st.info("No results found.")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"QA error: {str(e)}", exc_info=True)

    except Exception as e:
        st.error(f"Error in Q&A tab: {str(e)}")
        logger.error(f"Q&A tab error: {str(e)}", exc_info=True)


def main():
    """Main Streamlit app."""
    st.title("🐕 WM Depot CB% Agent")
    st.markdown("*Real-time Complete Basket % Analytics & Recommendations*")

    # Initialize clients
    clients = init_clients()
    if not clients:
        st.error("Failed to initialize. Please check your BigQuery credentials.")
        return

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        depot = st.selectbox(
            "Select Depot",
            ["7634", "7636", "7635"],
            help="Select a depot to analyze",
        )

        days_lookback = st.slider(
            "Days Lookback",
            min_value=1,
            max_value=365,
            value=30,
            help="Historical days to analyze",
        )

        st.divider()
        st.caption("🐕 Built with Streamlit")
        st.caption("📊 Powered by BigQuery")
        st.caption("🤖 AI-Powered Analysis")

    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "⭐ Recommendations", "💬 Q&A"])

    with tab1:
        st.header("📊 Metrics Dashboard")
        render_metrics_dashboard(depot, clients, days_lookback)

    with tab2:
        st.header("⭐ Item Recommendations")
        render_recommendations(depot, clients, 7)

    with tab3:
        st.header("💬 Question & Answer")
        render_qa_tab(depot, clients, days_lookback)

    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🚀 Scalable & Shareable")
    with col2:
        st.caption("🔒 Secure BigQuery Integration")
    with col3:
        st.caption("💡 Real-time AI Agent")


if __name__ == "__main__":
    main()