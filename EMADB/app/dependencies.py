from __future__ import annotations

from EMADB.app.utils.services.config_service import ConfigurationService
from EMADB.app.utils.services.search_service import SearchService


config_service = ConfigurationService()
search_service = SearchService(configuration_service=config_service)


# -----------------------------------------------------------------------------
def get_config_service() -> ConfigurationService:
    return config_service


# -----------------------------------------------------------------------------
def get_search_service() -> SearchService:
    return search_service
