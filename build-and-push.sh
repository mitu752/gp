#!/bin/bash

# 定义变量
USERNAME="mitu752"
IMAGE_NAME="gemini-proxy"
TAG="latest"

# 构建镜像
echo "构建镜像: ${USERNAME}/${IMAGE_NAME}:${TAG}"
docker build -t ${USERNAME}/${IMAGE_NAME}:${TAG} .

# 推送到Docker Hub
echo "推送镜像到Docker Hub..."
docker push ${USERNAME}/${IMAGE_NAME}:${TAG}

echo "完成!"
