# 🐕 WM Depot CB% Agent

**Real-time Complete Basket % Analytics & AI-Powered Recommendations**

A Streamlit-based intelligence agent for Walmart depot managers to analyze Complete Basket (CB%) metrics, identify missing items, and optimize assortment strategies using BigQuery data.

## ✨ Features

- **📊 Real-time Dashboard**: CB% trends, metrics, and historical analysis
- **⭐ Smart Recommendations**: AI-powered suggestions for items to add to assortment
- **💬 Q&A Analysis**: Ask natural language questions about your data
- **🔍 Root Cause Analysis**: Understand why CB% fluctuates
- **📈 Forecasting**: Simulate item impact on CB% metrics
- **🔒 Secure BigQuery Integration**: Direct connection to your data warehouse

## 🚀 Quick Start

### Local Development (5 minutes)

#### 1. Clone the Repository

```bash
git clone https://github.com/kn1327/wm-depot-cb-agent.git
cd wm-depot-cb-agent
```

#### 2. Set Up Python Environment (Walmart Network)

```bash
# Create virtual environment
uv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies using Walmart's PyPI mirror
uv pip install --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
  --allow-insecure-host pypi.ci.artifacts.walmart.com \
  -r requirements.txt
```

#### 3. Set Up GCP Credentials

**Option A: Using Service Account Key**

```bash
# Create .streamlit/secrets.toml
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit secrets.toml and add your GCP service account credentials
vim .streamlit/secrets.toml
```

**Option B: Using Application Default Credentials (ADC)**

```bash
# If using gcloud CLI
gcloud auth application-default login
```

#### 4. Configure Environment Variables

```bash
# Create .env file
cat > .env << 'EOF'
GCP_PROJECT_ID=wmt-instockinventory-datamart
BQ_DATASET=WM_AD_HOC
DEFAULT_DEPOT=7634
DEFAULT_DAYS_LOOKBACK=30
LOG_LEVEL=INFO
EOF
```

#### 5. Run Locally

```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

## 📤 Deploy to Streamlit Cloud

### Step 1: Prepare for Deployment

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Initial commit: WM Depot CB% Agent"
   git push origin main
   ```

2. **Verify these files are in your repo**:
   - `streamlit_app.py` (main app)
   - `requirements.txt` (dependencies)
   - `.streamlit/config.toml` (configuration)
   - `agents/`, `connectors/`, `config/` folders with source code
   - `.gitignore` (to protect secrets)

### Step 2: Create Streamlit Cloud Account

1. Go to https://streamlit.io/cloud
2. Sign in with your GitHub account
3. Click "Create app"

### Step 3: Deploy App

1. **Connect GitHub**:
   - Select your GitHub repo: `wn1327/wm-depot-cb-agent`
   - Select branch: `main`
   - Select file path: `streamlit_app.py`

2. **Configure Secrets** (IMPORTANT!):
   - Click "Advanced settings"
   - Under "Secrets", paste your `.streamlit/secrets.toml` contents:
   
   ```toml
   GCP_PROJECT_ID = "wmt-instockinventory-datamart"
   BQ_DATASET = "WM_AD_HOC"
   
   [gcp_service_account]
   type = "service_account"
   project_id = "wmt-instockinventory-datamart"
   private_key_id = "YOUR_KEY_ID"
   private_key = "YOUR_PRIVATE_KEY"
   client_email = "YOUR_SERVICE_ACCOUNT_EMAIL@gserviceaccount.com"
   client_id = "YOUR_CLIENT_ID"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "YOUR_CERT_URL"
   ```

3. **Deploy**:
   - Click "Deploy!"
   - Wait 2-3 minutes for the app to build and launch

### Step 4: Get Your App URL

Once deployed, your app will be available at:
```
https://wm-depot-cb-agent-RANDOMSTRING.streamlit.app
```

## 🔐 Secrets Management

### Local Development

Create `.streamlit/secrets.toml` with your GCP credentials:

```toml
GCP_PROJECT_ID = "wmt-instockinventory-datamart"
BQ_DATASET = "WM_AD_HOC"

[gcp_service_account]
# Copy entire service account JSON here as TOML
```

### Streamlit Cloud

1. Never commit `.streamlit/secrets.toml` to Git
2. Use Streamlit Cloud's "Secrets" management UI
3. Paste your secrets there (app will read them automatically)

## 📊 Project Structure

```
wm-depot-cb-agent/
├── streamlit_app.py              # Main Streamlit app
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore file
├── .streamlit/
│   ├── config.toml              # Streamlit configuration
│   └── secrets.toml.example     # Secrets template (NEVER commit secrets.toml)
├── agents/                       # AI agent modules
│   ├── query_generator.py       # SQL query generation from natural language
│   ├── item_recommender.py      # Item impact simulation & recommendations
│   └── root_cause_analyzer.py   # Root cause analysis
├── connectors/                   # Data connectors
│   └── bigquery_connector.py    # BigQuery interface
├── config/                       # Configuration
│   └── settings.py              # Settings management
└── README.md                     # This file
```

## 🎯 Usage

### Dashboard Tab
1. Select a depot from the sidebar
2. Adjust "Days Lookback" slider to change historical period
3. Click "Refresh Metrics" to update data
4. View CB% trends and detailed metrics

### Recommendations Tab
1. Click "Get Recommendations" to generate item suggestions
2. See top items with highest CB% impact
3. Review confidence scores and substitution rates

### Q&A Tab
1. Type a question like:
   - "What is the CB% trend?"
   - "Why did CB% drop?"
   - "What items are we missing?"
2. Click "Analyze"
3. View auto-generated SQL and results

## 🛠 Configuration

### Environment Variables

```bash
GCP_PROJECT_ID          # Your GCP project ID
BQ_DATASET              # BigQuery dataset name
DEFAULT_DEPOT           # Default depot to show (e.g., 7634)
DEFAULT_DAYS_LOOKBACK   # Default historical days (e.g., 30)
LOG_LEVEL               # Logging level (INFO, DEBUG, etc.)
```

### Streamlit Config

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Server settings
- Logger configuration

## 📚 BigQuery Tables

The app connects to these BigQuery tables:

- **Summary Table**: `K0N06DO_WM_DEPOT_ALLSTR_COMBINED_METRICS_MASTER_SUMMARY`
  - Contains: CB%, Catchment, Entitled, Attained metrics by depot/date

- **Detail Table**: `K0N06DO_WM_DEPOT_ALLSTR_COMBINED_METRICS_MASTER_V2`
  - Contains: Order-level data with substitutions

- **Assortment Table**: `K0N06DO_WM_DEPOT_ASSORT_MASTER_COMBINED`
  - Contains: Product assortment by depot

## 🚨 Troubleshooting

### "Authentication failed" Error

```
✅ Solution:
1. Check .streamlit/secrets.toml has correct GCP credentials
2. Verify service account has BigQuery permissions
3. Ensure GCP_PROJECT_ID matches your project
```

### "Table not found" Error

```
✅ Solution:
1. Verify table names in agents/query_generator.py
2. Check you have access to the dataset
3. Test query in BigQuery console first
```

### "No data returned"

```
✅ Solution:
1. Check depot number is valid (e.g., 7634)
2. Ensure data exists in BigQuery for selected dates
3. Try extending "Days Lookback" slider
```

### Streamlit Cloud Deploy Fails

```
✅ Solution:
1. Check requirements.txt has all dependencies
2. Verify .streamlit/secrets.toml is NOT in Git
3. Check Streamlit Cloud "Secrets" section has credentials
4. Review deployment logs in Streamlit Cloud dashboard
```

## 📈 Next Steps

- [ ] Add more depots to sidebar dropdown
- [ ] Implement forecasting models
- [ ] Add data export functionality (CSV, Excel)
- [ ] Create admin dashboard for multi-depot analysis
- [ ] Integrate with Slack for alerts
- [ ] Add refresh schedule for real-time updates

## 🤝 Contributing

To contribute:
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Create Pull Request

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review BigQuery logs for SQL errors
3. Check Streamlit Cloud logs for deployment issues

## 📄 License

Internal Walmart Tool - Proprietary

---

**Built with 🐕 by KIA** | Powered by Streamlit + BigQuery
