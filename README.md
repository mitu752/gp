# Gemini API 代理服务器 (Python版)

这是一个简单的Python代理服务器，可以转发请求到Gemini API，默认启用流式传输响应。

## 安装

```bash
pip install -r requirements.txt
```

## 启动服务器

```bash
python app.py
```

服务器将在 http://localhost:3000 上运行

## 使用方法

### 配置API密钥
可以通过环境变量设置API密钥：
```bash
export GEMINI_API_KEY=your_api_key_here
```
或者在请求头中添加 `x-api-key` 字段

### 流式请求 (默认)

所有请求默认都会使用流式传输：

```bash
curl -X POST "http://localhost:3000/v1beta/models/gemini-pro:generateContent" \
     -H "Content-Type: application/json" \
     -H "x-api-key: YOUR_API_KEY" \
     -d '{"contents":[{"parts":[{"text":"讲个笑话"}]}]}'
```

### 非流式请求 (可选)

如果需要禁用流式传输，可以添加 `stream=false` 查询参数或在请求体中设置 `stream: false`：

```bash
curl -X POST "http://localhost:3000/v1beta/models/gemini-pro:generateContent?stream=false" \
     -H "Content-Type: application/json" \
     -H "x-api-key: YOUR_API_KEY" \
     -d '{"contents":[{"parts":[{"text":"讲个笑话"}]}]}'
```

或者在JSON请求体中指定：

```bash
curl -X POST "http://localhost:3000/v1beta/models/gemini-pro:generateContent" \
     -H "Content-Type: application/json" \
     -H "x-api-key: YOUR_API_KEY" \
     -d '{"stream": false, "contents":[{"parts":[{"text":"讲个笑话"}]}]}'
```

# Docker 镜像自动构建与推送

本项目使用GitHub Actions自动构建Docker镜像并推送到GitHub Container Registry。

## 工作流程

当代码推送到`main`或`master`分支，或者创建新标签（以`v`开头）时，GitHub Actions将自动构建Docker镜像并推送到GitHub Container Registry。

## 配置说明

1. 默认情况下，工作流使用GitHub内置的`GITHUB_TOKEN`推送到GitHub Container Registry (ghcr.io)。
2. 如需推送到Docker Hub，请取消注释Docker Hub登录步骤，并在GitHub仓库设置中添加以下Secrets：
   - `DOCKERHUB_USERNAME`: Docker Hub 用户名
   - `DOCKERHUB_TOKEN`: Docker Hub 访问令牌

## 镜像标签

- 分支提交: `ghcr.io/{username}/{repo}:{branch}`
- PR提交: `ghcr.io/{username}/{repo}:pr-{number}`
- 版本标签: `ghcr.io/{username}/{repo}:{tag}` 和 `ghcr.io/{username}/{repo}:{major}.{minor}`

## 本地测试

```bash
# 构建镜像
docker build -t myapp .

# 运行容器
docker run -p 3000:3000 myapp
```
