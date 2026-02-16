"""Health check endpoints for CyberDemo backend."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..core.database import get_db
from ..core.config import settings
from ..opensearch.client import OpenSearchClient

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str = "1.0.0"


class OpenSearchHealthResponse(BaseModel):
    """OpenSearch health check response model."""
    status: str
    cluster_name: Optional[str] = None
    cluster_status: Optional[str] = None
    number_of_nodes: Optional[int] = None
    active_shards: Optional[int] = None
    error: Optional[str] = None


class DatabaseHealthResponse(BaseModel):
    """Database health check response model."""
    status: str
    database: str = "postgresql"
    error: Optional[str] = None


@router.get("", response_model=HealthResponse)
@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.
    Returns the service status and name.
    """
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
    )


@router.get("/opensearch", response_model=OpenSearchHealthResponse)
async def opensearch_health_check() -> OpenSearchHealthResponse:
    """
    Check OpenSearch cluster health.
    Returns cluster status and basic metrics.
    """
    try:
        client = await OpenSearchClient.create()
        health = await client.health_check()

        if health.get("status") == "healthy":
            return OpenSearchHealthResponse(
                status="healthy",
                cluster_name=health.get("cluster_name"),
                cluster_status=health.get("cluster_status"),
                number_of_nodes=health.get("number_of_nodes"),
                active_shards=health.get("active_shards"),
            )
        else:
            return OpenSearchHealthResponse(
                status="unhealthy",
                error=health.get("error"),
            )
    except Exception as e:
        return OpenSearchHealthResponse(
            status="unhealthy",
            error=str(e),
        )


@router.get("/database", response_model=DatabaseHealthResponse)
async def database_health_check(
    db: AsyncSession = Depends(get_db),
) -> DatabaseHealthResponse:
    """
    Check PostgreSQL database health.
    Executes a simple query to verify connectivity.
    """
    try:
        # Execute a simple query to test the connection
        result = await db.execute(text("SELECT 1"))
        result.scalar()

        return DatabaseHealthResponse(
            status="healthy",
            database="postgresql",
        )
    except Exception as e:
        return DatabaseHealthResponse(
            status="unhealthy",
            database="postgresql",
            error=str(e),
        )
