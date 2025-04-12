from fastapi import FastAPI
import asyncio
import uvicorn
from fastapi_mcp import FastApiMCP

# 创建主应用
main_app = FastAPI()

# 配置参数
NUM_SERVERS = 16  # 定义要创建的MCP服务器数量
BASE_PORT = 8001  # 子服务起始端口
MCP_PORT = 8000  # 主网关端口

# 存储子应用运行函数
sub_servers = []

# 批量创建子应用并配置MCP
for i in range(1, NUM_SERVERS + 1):
    # 创建子应用
    sub_app = FastAPI()
    port = BASE_PORT + i - 1  # 计算子应用端口
    mount_path = f"/mcp{i}"  # 挂载路径


    # 添加测试端点
    @sub_app.get("/")
    async def root_endpoint(server_id=i):  # 使用默认参数捕获当前i值
        return {"message": f"来自服务 {server_id}"}


    # 创建MCP实例并挂载到主应用
    mcp = FastApiMCP(
        sub_app,
        base_url=f"http://localhost:{port}"
    )
    mcp.mount(main_app, mount_path=mount_path)


# 主网关运行函数
def run_gateway():
    uvicorn.run(main_app, host="localhost", port=MCP_PORT)


async def main():
    tasks = [asyncio.to_thread(run_gateway)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())