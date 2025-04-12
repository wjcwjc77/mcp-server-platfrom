from fastapi import FastAPI
import asyncio
import uvicorn
from examples.shared import items
from examples.shared.setup import setup_logging
from fastapi_mcp import FastApiMCP

setup_logging()

# 后端服务端口配置
ITEMS_PORT = 8001
TEST_APP_PORT = 8002
TEST_APP_PORT3 = 8003
MCP_PORT = 8000  # 主MCP应用端口

# 创建主应用
main_app = FastAPI()

# 初始化MCP实例并挂载到主应用
mcp_items = FastApiMCP(
    items.app,
    base_url=f"http://localhost:{ITEMS_PORT}",  # 指向items服务真实端口
)
mcp_items.mount(main_app, mount_path='/mcp1')

test_app = FastAPI()
@test_app.get("/test",description="一个用来打招呼的工具")
async def test_endpoint():
    return {"message": "hello wjc!"}
mcp_test = FastApiMCP(
    test_app,
    base_url=f"http://localhost:{TEST_APP_PORT}",  # 指向test_app服务真实端口
)
mcp_test.mount(main_app, mount_path='/mcp2')

test_app3 = FastAPI()
mcp_test3 = FastApiMCP(
    test_app3,
    base_url=f"http://localhost:{TEST_APP_PORT3}",
)
mcp_test3.mount(main_app, mount_path='/mcp3')

# 运行后端服务的函数
def run_items():
    uvicorn.run(items.app, host="localhost", port=ITEMS_PORT)

def run_test():
    uvicorn.run(test_app, host="localhost", port=TEST_APP_PORT)
def run_test3():
    uvicorn.run(test_app3, host="localhost", port=TEST_APP_PORT3)


def run_mcp():
    """运行主MCP网关"""
    uvicorn.run(main_app, host="localhost", port=MCP_PORT)


async def main():
    await asyncio.gather(
        asyncio.to_thread(run_items),
        asyncio.to_thread(run_test),
        asyncio.to_thread(run_test3),
        asyncio.to_thread(run_mcp)
    )

if __name__ == "__main__":
    asyncio.run(main())