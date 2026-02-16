"""
MCP Data Server.

Provides JSON-RPC 2.0 interface for synthetic data generation operations.

Endpoints:
- GET /data-mcp/health - Health check
- POST /data-mcp/messages - JSON-RPC message handler

This server handles data generation tools, separate from the main MCP server
that handles SOC operations (SIEM, EDR, Intel, etc.).
"""

import json
from typing import Any, Dict
from fastapi import APIRouter
from pydantic import BaseModel

from .data_tools import get_all_data_tools, get_data_tool_handlers


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
async def data_mcp_health():
    """MCP Data Server health check."""
    tools = get_all_data_tools()
    return {
        "status": "healthy",
        "protocol": "MCP-Data",
        "version": "1.0.0",
        "tools_count": len(tools)
    }


@router.post("/messages")
async def data_mcp_messages(request: JsonRpcRequest) -> Dict[str, Any]:
    """
    Handle JSON-RPC 2.0 messages for data generation.

    Supported methods:
    - tools/list: List available data tools
    - tools/call: Execute a data tool
    """
    try:
        if request.method == "tools/list":
            return await handle_tools_list(request)
        elif request.method == "tools/call":
            return await handle_tools_call(request)
        else:
            return make_error_response(
                request.id,
                ERROR_METHOD_NOT_FOUND,
                f"Method not found: {request.method}"
            )
    except Exception as e:
        return make_error_response(
            request.id,
            ERROR_INTERNAL,
            str(e)
        )


# =============================================================================
# Method Handlers
# =============================================================================

async def handle_tools_list(request: JsonRpcRequest) -> Dict[str, Any]:
    """Handle tools/list method."""
    tools = get_all_data_tools()

    return {
        "jsonrpc": "2.0",
        "id": request.id,
        "result": {
            "tools": tools
        }
    }


async def handle_tools_call(request: JsonRpcRequest) -> Dict[str, Any]:
    """Handle tools/call method."""
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

    handlers = get_data_tool_handlers()

    if tool_name not in handlers:
        return make_error_response(
            request.id,
            ERROR_METHOD_NOT_FOUND,
            f"Tool not found: {tool_name}"
        )

    try:
        handler = handlers[tool_name]
        result = await handler(arguments)

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
        return make_error_response(
            request.id,
            ERROR_INVALID_PARAMS,
            str(e)
        )
    except Exception as e:
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
