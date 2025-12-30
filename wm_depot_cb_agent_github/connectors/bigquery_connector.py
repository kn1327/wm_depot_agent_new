"""BigQuery connector for WM depot data."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

from config.settings import get_settings

logger = logging.getLogger(__name__)


class BigQueryConnector:
    """Interface for BigQuery operations."""

    def __init__(self, client: Optional[bigquery.Client] = None):
        """Initialize BigQuery connector.

        Args:
            client: Optional pre-configured BigQuery client.
                   If None, creates from settings.
        """
        self.settings = get_settings()
        if client:
            self.client = client
        else:
            kwargs = self.settings.get_bigquery_client_kwargs()
            self.client = bigquery.Client(**kwargs)

        logger.info(
            f"BigQuery connector initialized for project: "
            f"{self.settings.gcp_project_id}"
        )

    def execute_query(
        self, query: str, timeout: int = 300
    ) -> List[Dict[str, Any]]:
        """Execute a BigQuery SQL query.

        Args:
            query: SQL query string
            timeout: Query timeout in seconds

        Returns:
            List of result rows as dictionaries

        Raises:
            GoogleCloudError: If query execution fails
        """
        logger.info("Executing BigQuery query")
        logger.debug(f"Query: {query[:500]}...")

        try:
            query_job = self.client.query(query)
            results = query_job.result(timeout=timeout)

            rows = [dict(row.items()) for row in results]

            logger.info(
                f"Query completed successfully. "
                f"Returned {len(rows)} rows."
            )

            return rows

        except GoogleCloudError as e:
            logger.error(f"BigQuery query failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing query: {str(e)}")
            raise

    def close(self):
        """Close the BigQuery client connection."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("BigQuery client connection closed")
