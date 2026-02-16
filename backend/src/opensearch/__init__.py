"""OpenSearch client and index templates for CyberDemo."""

from .client import (
    get_opensearch_client,
    close_opensearch_client,
    OpenSearchClient,
)
from .templates import INDEX_TEMPLATES, ALL_INDICES

__all__ = [
    "get_opensearch_client",
    "close_opensearch_client",
    "OpenSearchClient",
    "INDEX_TEMPLATES",
    "ALL_INDICES",
]
