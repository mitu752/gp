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
