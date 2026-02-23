"""
MCP Backend Server.

Provides JSON-RPC 2.0 interface for SoulInTheBot to interact with SOC systems.

Endpoints:
- GET /mcp/health - Health check
- GET /mcp/sse - Server-Sent Events for streaming (placeholder)
- POST /mcp/messages - JSON-RPC message handler

Includes rate limiting (100 req/min per session) per TECH-008.
"""

import json
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

import time
from .tools import get_all_tools, get_tool_handlers
from .rate_limiter import get_default_rate_limiter
from .audit_logger import get_audit_logger

router = APIRouter()


# =============================================================================
# Request/Response Models
# =============================================================================

class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 request format."""
    jsonrpc: str = "2.0"
    id: int | str | None = None
    method: str
    params: Dict[str, Any] | None = None


class JsonRpcError(BaseModel):
    """JSON-RPC 2.0 error format."""
    code: int
    message: str
    data: Any | None = None


class JsonRpcResponse(BaseModel):
    """JSON-RPC 2.0 response format."""
    jsonrpc: str = "2.0"
    id: int | str | None = None
    result: Any | None = None
    error: JsonRpcError | None = None


# =============================================================================
# Error Codes
# =============================================================================

ERROR_PARSE = -32700
ERROR_INVALID_REQUEST = -32600
ERROR_METHOD_NOT_FOUND = -32601
ERROR_INVALID_PARAMS = -32602
ERROR_INTERNAL = -32603


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/health")
async def mcp_health():
    """MCP server health check."""
    tools = get_all_tools()
    return {
        "status": "healthy",
        "protocol": "MCP",
        "version": "1.0.0",
        "tools_count": len(tools)
    }


@router.get("/sse")
async def mcp_sse():
    """
    Server-Sent Events endpoint for MCP streaming.

    This is a placeholder - full SSE implementation would use
    asyncio generators for real-time updates.
    """
    async def event_generator():
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.post("/messages")
async def mcp_messages(
    request: JsonRpcRequest,
    raw_request: Request
) -> Response:
    """
    Handle JSON-RPC 2.0 messages.

    Supported methods:
    - tools/list: List available tools
    - tools/call: Execute a tool

    Includes rate limiting headers (TECH-008).
    """
    # Get session ID from header or use client IP as fallback
    session_id = raw_request.headers.get(
        "X-Session-ID",
        raw_request.client.host if raw_request.client else "unknown"
    )

    # Check rate limit
    rate_limiter = get_default_rate_limiter()
    is_allowed = await rate_limiter.check_rate_limit(session_id)

    # Get rate limit stats for headers
    stats = await rate_limiter.get_usage_stats(session_id)

    # Prepare rate limit headers
    rate_limit_headers = {
        "X-RateLimit-Limit": str(stats["limit"]),
        "X-RateLimit-Remaining": str(stats["remaining"]),
        "X-RateLimit-Reset": str(int(stats["reset_in_seconds"] or 0))
    }

    # If rate limited, return 429
    if not is_allowed:
        return JSONResponse(
            status_code=429,
            content={
                "jsonrpc": "2.0",
                "id": request.id,
                "error": {
                    "code": -32000,
                    "message": "Rate limit exceeded. Try again later.",
                    "data": {
                        "retry_after_seconds": stats["reset_in_seconds"]
                    }
                }
            },
            headers=rate_limit_headers
        )

    # Process the request
    try:
        if request.method == "tools/list":
            result = await handle_tools_list(request)
        elif request.method == "tools/call":
            result = await handle_tools_call(request, session_id)
        else:
            result = make_error_response(
                request.id,
                ERROR_METHOD_NOT_FOUND,
                f"Method not found: {request.method}"
            )

        return JSONResponse(content=result, headers=rate_limit_headers)

    except Exception as e:
        return JSONResponse(
            content=make_error_response(request.id, ERROR_INTERNAL, str(e)),
            headers=rate_limit_headers
        )


# =============================================================================
# Method Handlers
# =============================================================================

async def handle_tools_list(request: JsonRpcRequest) -> Dict[str, Any]:
    """Handle tools/list method."""
    tools = get_all_tools()

    return {
        "jsonrpc": "2.0",
        "id": request.id,
        "result": {
            "tools": tools
        }
    }


async def handle_tools_call(
    request: JsonRpcRequest,
    session_id: str = "unknown"
) -> Dict[str, Any]:
    """Handle tools/call method with audit logging (REQ-014)."""
    if not request.params:
        return make_error_response(
            request.id,
            ERROR_INVALID_PARAMS,
            "Missing params"
        )

    tool_name = request.params.get("name")
    arguments = request.params.get("arguments", {})

    if not tool_name:
        return make_error_response(
            request.id,
            ERROR_INVALID_PARAMS,
            "Missing tool name"
        )

    handlers = get_tool_handlers()

    if tool_name not in handlers:
        return make_error_response(
            request.id,
            ERROR_METHOD_NOT_FOUND,
            f"Tool not found: {tool_name}"
        )

    # Get audit logger
    audit_logger = get_audit_logger()
    start_time = time.time()

    try:
        handler = handlers[tool_name]
        result = await handler(arguments)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Log successful invocation
        await audit_logger.log_invocation(
            tool_name=tool_name,
            session_id=session_id,
            arguments=arguments,
            result=result,
            status="success",
            duration_ms=duration_ms
        )

        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result)
                    }
                ]
            }
        }
    except ValueError as e:
        duration_ms = int((time.time() - start_time) * 1000)

        # Log failed invocation
        await audit_logger.log_invocation(
            tool_name=tool_name,
            session_id=session_id,
            arguments=arguments,
            result=None,
            status="error",
            error_message=str(e),
            duration_ms=duration_ms
        )

        return make_error_response(
            request.id,
            ERROR_INVALID_PARAMS,
            str(e)
        )
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)

        # Log failed invocation
        await audit_logger.log_invocation(
            tool_name=tool_name,
            session_id=session_id,
            arguments=arguments,
            result=None,
            status="error",
            error_message=str(e),
            duration_ms=duration_ms
        )

        return make_error_response(
            request.id,
            ERROR_INTERNAL,
            f"Tool execution failed: {str(e)}"
        )


# =============================================================================
# Helpers
# =============================================================================

def make_error_response(
    request_id: int | str | None,
    code: int,
    message: str,
    data: Any = None
) -> Dict[str, Any]:
    """Create a JSON-RPC error response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
            "data": data
        }
    }
