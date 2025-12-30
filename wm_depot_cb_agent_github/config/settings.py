"""Configuration settings for WM Depot CB% Agent."""

import os
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


class Settings:
    """Application settings."""

    def __init__(self):
        """Initialize settings from environment variables."""
        # GCP Configuration
        self.gcp_project_id = os.getenv(
            "GCP_PROJECT_ID", "wmt-instockinventory-datamart"
        )
        self.gcp_credentials_path = os.getenv("GCP_CREDENTIALS_PATH")

        # BigQuery Configuration
        self.bq_dataset = os.getenv(
            "BQ_DATASET", "WM_AD_HOC"
        )

        # Agent Configuration
        self.default_depot = os.getenv("DEFAULT_DEPOT", "7634")
        self.default_days_lookback = int(os.getenv("DEFAULT_DAYS_LOOKBACK", "30"))
        self.default_add_item_limit = int(os.getenv("DEFAULT_ADD_ITEM_LIMIT", "700"))

        # UI Configuration
        self.auto_recommend = os.getenv("AUTO_RECOMMEND", "true").lower() == "true"
        self.enable_websocket = os.getenv("ENABLE_WEBSOCKET", "false").lower() == "true"

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    def get_bigquery_client_kwargs(self) -> Dict[str, Any]:
        """Get kwargs for BigQuery client initialization.

        Returns:
            Dictionary of kwargs for google.cloud.bigquery.Client
        """
        kwargs = {
            "project": self.gcp_project_id,
        }

        if self.gcp_credentials_path and os.path.exists(self.gcp_credentials_path):
            kwargs["credentials"] = self._load_credentials(self.gcp_credentials_path)

        return kwargs

    @staticmethod
    def _load_credentials(credentials_path: str):
        """Load GCP credentials from file.

        Args:
            credentials_path: Path to credentials JSON file

        Returns:
            Credentials object
        """
        from google.oauth2 import service_account

        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            logger.info(f"Loaded credentials from {credentials_path}")
            return credentials
        except Exception as e:
            logger.warning(
                f"Failed to load credentials from {credentials_path}: {e}"
            )
            return None

    def __repr__(self) -> str:
        """String representation of settings."""
        return (
            f"Settings("
            f"gcp_project={self.gcp_project_id}, "
            f"bq_dataset={self.bq_dataset}, "
            f"default_depot={self.default_depot}"
            f")"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get global settings instance (cached).

    Returns:
        Settings instance
    """
    return Settings()
