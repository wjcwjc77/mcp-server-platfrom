from typing import Any
from fastapi.responses import JSONResponse
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
import logging
logger = logging.getLogger(__name__)
# Initialize FastMCP server for Weather tools (SSE)
mcp = FastMCP("weather")

# Constants


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

import asyncio

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    logger.info("```````````````````````")
    from sse_starlette.sse import AppStatus
    # 强制创建新的事件对象
    AppStatus.should_exit_event = asyncio.Event()  
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        logger.info("hhhhhhhhhhhhhhhhh")
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        try:
            async with sse.connect_sse(
                    request.scope,
                    request.receive,
                    request._send,  # noqa: SLF001
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
        except Exception as e:
            logger.error(f"Error in SSE connection: {e}")
        # 添加请求日志中间件
    # 创建Router替代Starlette实例
    from starlette.routing import Router
    app = Router(routes=[
        Route("/sse", handle_sse, methods=["GET", "POST"]),  # 显式声明方法
        Mount("/messages/", app=sse.handle_post_message)
    ])
        # 添加根路由测试端点
    @app.route("/")
    async def home(request):
        return JSONResponse({"message": "Server is running"})
    return app


if __name__ == "__main__":
    mcp_server = mcp._mcp_server  # noqa: WPS437

    import argparse
    
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)