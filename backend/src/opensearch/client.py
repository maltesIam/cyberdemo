"""Async OpenSearch client singleton with connection pooling and helpers."""

import logging
from typing import Any, Optional
from opensearchpy import AsyncOpenSearch

from ..core.config import settings
from .templates import INDEX_TEMPLATES, ALL_INDICES

logger = logging.getLogger(__name__)

# Global client instance
_client: Optional[AsyncOpenSearch] = None


async def get_opensearch_client() -> AsyncOpenSearch:
    """
    Get or create the singleton OpenSearch client.
    Uses connection pooling for efficient resource usage.
    """
    global _client
    if _client is None:
        _client = AsyncOpenSearch(
            hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
            ssl_show_warn=False,
            # Connection pooling settings
            pool_maxsize=20,
            timeout=30,
            max_retries=3,
            retry_on_timeout=True,
        )
        logger.info(
            f"OpenSearch client created for {settings.opensearch_host}:{settings.opensearch_port}"
        )
    return _client


async def close_opensearch_client() -> None:
    """Close the OpenSearch client and release resources."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
        logger.info("OpenSearch client closed")


class OpenSearchClient:
    """
    High-level async OpenSearch client wrapper with helper methods
    for index management and document operations.
    """

    def __init__(self, client: AsyncOpenSearch):
        self.client = client

    @classmethod
    async def create(cls) -> "OpenSearchClient":
        """Factory method to create OpenSearchClient with initialized connection."""
        client = await get_opensearch_client()
        return cls(client)

    async def health_check(self) -> dict[str, Any]:
        """Check OpenSearch cluster health."""
        try:
            health = await self.client.cluster.health()
            return {
                "status": "healthy",
                "cluster_name": health.get("cluster_name"),
                "cluster_status": health.get("status"),
                "number_of_nodes": health.get("number_of_nodes"),
                "active_shards": health.get("active_shards"),
            }
        except Exception as e:
            logger.error(f"OpenSearch health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def index_exists(self, index_name: str) -> bool:
        """Check if an index exists."""
        try:
            return await self.client.indices.exists(index=index_name)
        except Exception as e:
            logger.error(f"Error checking index existence for {index_name}: {e}")
            return False

    async def create_index(self, index_name: str, body: Optional[dict] = None) -> bool:
        """
        Create an index with the given settings and mappings.
        If body is None, uses the template from INDEX_TEMPLATES if available.
        """
        try:
            if await self.index_exists(index_name):
                logger.info(f"Index {index_name} already exists")
                return True

            if body is None:
                body = INDEX_TEMPLATES.get(index_name, {})

            await self.client.indices.create(index=index_name, body=body)
            logger.info(f"Created index: {index_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            return False

    async def delete_index(self, index_name: str) -> bool:
        """Delete an index if it exists."""
        try:
            if await self.index_exists(index_name):
                await self.client.indices.delete(index=index_name)
                logger.info(f"Deleted index: {index_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting index {index_name}: {e}")
            return False

    async def create_all_indices(self) -> dict[str, bool]:
        """Create all defined indices using their templates."""
        results = {}
        for index_name in ALL_INDICES:
            results[index_name] = await self.create_index(index_name)
        return results

    async def delete_all_indices(self) -> dict[str, bool]:
        """Delete all defined indices."""
        results = {}
        for index_name in ALL_INDICES:
            results[index_name] = await self.delete_index(index_name)
        return results

    async def reset_all_indices(self) -> dict[str, dict[str, bool]]:
        """Delete and recreate all indices."""
        delete_results = await self.delete_all_indices()
        create_results = await self.create_all_indices()
        return {
            "deleted": delete_results,
            "created": create_results,
        }

    async def index_document(
        self,
        index_name: str,
        document: dict[str, Any],
        doc_id: Optional[str] = None,
        refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Index a single document.

        Args:
            index_name: Name of the index
            document: Document to index
            doc_id: Optional document ID (auto-generated if not provided)
            refresh: Whether to refresh the index after indexing
        """
        try:
            result = await self.client.index(
                index=index_name,
                body=document,
                id=doc_id,
                refresh="true" if refresh else "false",
            )
            return {"success": True, "id": result.get("_id"), "result": result.get("result")}
        except Exception as e:
            logger.error(f"Error indexing document to {index_name}: {e}")
            return {"success": False, "error": str(e)}

    async def bulk_index(
        self,
        index_name: str,
        documents: list[dict[str, Any]],
        id_field: Optional[str] = None,
        refresh: bool = True,
    ) -> dict[str, Any]:
        """
        Bulk index multiple documents.

        Args:
            index_name: Name of the index
            documents: List of documents to index
            id_field: Field name to use as document ID
            refresh: Whether to refresh the index after bulk indexing
        """
        if not documents:
            return {"success": True, "indexed": 0, "errors": []}

        try:
            actions = []
            for doc in documents:
                action = {"index": {"_index": index_name}}
                if id_field and id_field in doc:
                    action["index"]["_id"] = doc[id_field]
                actions.append(action)
                actions.append(doc)

            result = await self.client.bulk(
                body=actions,
                refresh="true" if refresh else "false",
            )

            errors = []
            if result.get("errors"):
                for item in result.get("items", []):
                    if "error" in item.get("index", {}):
                        errors.append(item["index"]["error"])

            return {
                "success": not result.get("errors"),
                "indexed": len(documents) - len(errors),
                "errors": errors,
            }
        except Exception as e:
            logger.error(f"Error bulk indexing to {index_name}: {e}")
            return {"success": False, "indexed": 0, "errors": [str(e)]}

    async def search(
        self,
        index_name: str,
        query: Optional[dict[str, Any]] = None,
        size: int = 100,
        sort: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Search documents in an index.

        Args:
            index_name: Name of the index
            query: OpenSearch query DSL (defaults to match_all)
            size: Maximum number of results
            sort: Sort specification
        """
        try:
            body: dict[str, Any] = {"size": size}
            if query:
                body["query"] = query
            else:
                body["query"] = {"match_all": {}}
            if sort:
                body["sort"] = sort

            result = await self.client.search(index=index_name, body=body)

            hits = result.get("hits", {})
            return {
                "success": True,
                "total": hits.get("total", {}).get("value", 0),
                "hits": [hit.get("_source") for hit in hits.get("hits", [])],
            }
        except Exception as e:
            logger.error(f"Error searching {index_name}: {e}")
            return {"success": False, "total": 0, "hits": [], "error": str(e)}

    async def get_document(
        self, index_name: str, doc_id: str
    ) -> Optional[dict[str, Any]]:
        """Get a single document by ID."""
        try:
            result = await self.client.get(index=index_name, id=doc_id)
            return result.get("_source")
        except Exception as e:
            logger.error(f"Error getting document {doc_id} from {index_name}: {e}")
            return None

    async def count_documents(self, index_name: str) -> int:
        """Count documents in an index."""
        try:
            if not await self.index_exists(index_name):
                return 0
            result = await self.client.count(index=index_name)
            return result.get("count", 0)
        except Exception as e:
            logger.error(f"Error counting documents in {index_name}: {e}")
            return 0

    async def get_all_counts(self) -> dict[str, int]:
        """Get document counts for all defined indices."""
        counts = {}
        for index_name in ALL_INDICES:
            counts[index_name] = await self.count_documents(index_name)
        return counts
