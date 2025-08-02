#!/bin/bash
# 启动代理服务

# 加载虚拟环境（如果有）
# source venv/bin/activate

# 使用uvicorn启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
