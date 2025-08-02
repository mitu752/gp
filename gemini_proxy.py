import requests
from flask import Response, stream_with_context
import os

GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com'

def handle_gemini_proxy(request, path):
    # 获取API密钥
    api_key = request.headers.get('x-api-key') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return {"error": "缺少API密钥"}, 401

    # 构建目标URL
    target_url = f"{GEMINI_BASE_URL}/{path}"

    # 获取所有查询参数
    params = request.args.to_dict()
    params['key'] = api_key

    # 检查是否明确指定不使用流式传输
    is_stream = True  # 默认启用流式传输
    if 'stream' in params and params['stream'].lower() == 'false':
        is_stream = False
    
    if request.is_json and request.json:
        body_data = request.json
        if 'stream' in body_data and body_data['stream'] == False:
            is_stream = False
    else:
        body_data = request.get_data()

    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        if is_stream:
            # 流式处理
            def generate():
                response = requests.post(
                    target_url,
                    params=params,
                    json=body_data,
                    headers=headers,
                    stream=True
                )
                
                for chunk in response.iter_content(chunk_size=4096):
                    yield chunk
                    
            return Response(
                stream_with_context(generate()),
                content_type='application/json'
            )
        else:
            # 非流式处理
            if request.method == 'POST':
                response = requests.post(
                    target_url,
                    params=params,
                    json=body_data,
                    headers=headers
                )
            else:
                response = requests.get(
                    target_url,
                    params=params,
                    headers=headers
                )
            
            return Response(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'application/json')
            )
    
    except Exception as e:
        return {"error": str(e), "message": "代理请求失败"}, 500
