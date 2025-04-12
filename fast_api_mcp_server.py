from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI()



# @mcp.tool()
# async def get_all_tools() -> str:
#     """获取数据工厂平台集成了的所有工具，不需要传入参数

#     """
#     url = "https://byteqa-boe.bytedance.net/mf/api/getAllTools"
#     response = await make_request(url)
#     return response

# Explicit operation_id (tool will be named "get_user_info")
@app.get("/get_user_info", operation_id="get_user_info")
async def get_all_tools():
    """获取数据工厂平台集成了的所有工具，不需要传入参数
    """
    url = "https://byteqa-boe.bytedance.net/mf/api/getAllTools"
    pass
    # response = await make_request(url)
    # return response
# Mount the MCP server directly to your FastAPI app

mcp = FastApiMCP(
    app,
    name="My API MCP",
    description="My API description",
    base_url="http://localhost:8000",
    include_operations=["get_user_info"],

)
mcp.mount()




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)