from fastapi import FastAPI, Request, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
import httpx
import os
import time
import asyncio
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 全局HTTP客户端，使用连接池
http_client: httpx.AsyncClient = None

# 请求计数和性能统计
request_stats = {
    "total_requests": 0,
    "success_requests": 0,
    "error_requests": 0,
    "total_time": 0,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建全局HTTP客户端
    global http_client
    http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        timeout=httpx.Timeout(60.0),
        # 禁用自动解压缩，保持原始响应格式
        decompress=False
    )
    logger.info("API代理服务已启动，HTTP客户端连接池已初始化")
    yield
    # 关闭时清理资源
    await http_client.aclose()
    logger.info("API代理服务已关闭")

app = FastAPI(title="Gemini API代理服务", lifespan=lifespan)

# Gemini API的基础URL
GEMINI_API_BASE = "https://generativelanguage.googleapis.com"

# 信号量限制并发请求数
MAX_CONCURRENT_REQUESTS = 50
request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# 监控端点
@app.get("/status")
async def get_status():
    avg_time = 0
    if request_stats["success_requests"] > 0:
        avg_time = request_stats["total_time"] / request_stats["success_requests"]
    
    return {
        "status": "running",
        "stats": {
            "total_requests": request_stats["total_requests"],
            "success_requests": request_stats["success_requests"],
            "error_requests": request_stats["error_requests"],
            "avg_response_time": f"{avg_time:.4f}s",
        }
    }

@app.api_route("/gemini{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def proxy_gemini(request: Request, path: str, background_tasks: BackgroundTasks):
    # 获取请求内容
    body = await request.body()
    headers = dict(request.headers)
    
    # 只删除技术上必须删除的请求头
    # 'host'头必须删除，否则会导致请求发送到错误的服务器
    if 'host' in headers:
        del headers['host']
    
    # 保留所有客户端提供的参数
    params = dict(request.query_params)
    
    # 构建目标URL
    target_url = f"{GEMINI_API_BASE}{path}"
    
    start_time = time.time()
    request_stats["total_requests"] += 1
    
    # 使用信号量限制并发请求数
    async with request_semaphore:
        try:
            # 构建请求，准备流式转发
            req = http_client.build_request(
                method=request.method,
                url=target_url,
                params=params,
                headers=headers,
                content=body
            )
            # 发送请求并获取流式响应
            resp = await http_client.send(req, stream=True)
            
            # 更新统计信息
            elapsed = time.time() - start_time
            request_stats["success_requests"] += 1
            request_stats["total_time"] += elapsed
            
            # 记录请求信息（异步）
            background_tasks.add_task(
                logger.info,
                f"请求成功: {path} - {resp.status_code} - {elapsed:.4f}s"
            )

            # 保留所有原始响应头
            # 只删除会干扰正常响应的头
            response_headers = dict(resp.headers)
            
            # 返回流式响应
            return StreamingResponse(
                resp.aiter_bytes(),
                status_code=resp.status_code,
                headers=response_headers,
                media_type=resp.headers.get("content-type")
            )
        
        except Exception as e:
            # 记录错误
            request_stats["error_requests"] += 1
            logger.error(f"请求失败: {path} - {str(e)}")
            return Response(
                content=f"代理请求错误: {str(e)}",
                status_code=500
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # 根据CPU核心数调整
        # loop="uvloop",  # 更快的事件循环实现
        # http="httptools",  # 更快的HTTP解析
    )



# curl -X POST "http://40.115.195.78:8000/gemini/v1beta/chat/completions" \
#   -H "Authorization: Bearer AIzaSyAsvOCihOZgSuAEURbBn7F-nAklTAgsmvs" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "model": "gemini-2.5-flash",
#     "messages": [
#       {
#         "role": "user",
#         "content": "hi"
#       }
#     ]
#   }'