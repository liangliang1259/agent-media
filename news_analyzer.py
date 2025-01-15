import os
from datetime import datetime
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
import time
import urllib.parse
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# 加载环境变量
load_dotenv()

# 初始化 API client
KIMI_API_KEY = os.getenv('KIMI_API_KEY')

def get_news(keyword, limit=5):
    """从搜狗微信搜索获取文章"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': 'ABTEST=0|1673947200|v1; SNUID=1234567890ABCDEF; IPLOC=CN1100'
    }
    
    articles = []
    try:
        # 使用搜狗微信搜索接口
        encoded_keyword = urllib.parse.quote(keyword)
        search_url = f'https://weixin.sogou.com/weixin?type=2&s_from=input&query={encoded_keyword}&ie=utf8'
        
        print(f"正在访问: {search_url}")
        response = requests.get(search_url, headers=headers)
        response.encoding = 'utf-8'
        
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取搜索结果
            news_items = soup.select('div.txt-box')[:limit]
            print(f"找到 {len(news_items)} 个结果")
            
            for item in news_items:
                try:
                    # 获取标题和链接
                    title_elem = item.select_one('h3 a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    url = title_elem['href']
                    if not url.startswith('http'):
                        url = 'https://weixin.sogou.com' + url
                    
                    # 获取描述
                    desc_elem = item.select_one('p.txt-info')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # 获取来源（公众号名称）和时间
                    source_elem = item.select_one('a.account')
                    time_elem = item.select_one('span.s2')
                    
                    source = source_elem.get_text(strip=True) if source_elem else "未知公众号"
                    pub_time = time_elem.get_text(strip=True) if time_elem else "未知时间"
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'description': description,
                        'source': {'name': source},
                        'publishedAt': pub_time
                    })
                    print(f"成功解析文章: {title}")
                    
                except Exception as e:
                    print(f"解析文章时出错: {str(e)}")
                    continue
        else:
            print(f"请求失败，状态码: {response.status_code}")
                    
    except Exception as e:
        print(f"获取文章时出错: {str(e)}")
    
    return articles

def extract_keywords(text):
    """使用Kimi API提取关键词"""
    if not KIMI_API_KEY:
        print("错误: 未设置 KIMI_API_KEY 环境变量")
        return []
        
    headers = {
        'Authorization': f'Bearer {KIMI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'moonshot-v1-8k',
        'messages': [
            {'role': 'system', 'content': '请从以下文本中提取5个最重要的关键词，直接返回关键词，用逗号分隔。'},
            {'role': 'user', 'content': text}
        ]
    }
    
    try:
        response = requests.post('https://api.moonshot.cn/v1/chat/completions', 
                               headers=headers,
                               json=data,
                               timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].split(',')
    except requests.exceptions.RequestException as e:
        print(f"提取关键词时出错: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"错误详情: {e.response.text}")
        return []

def summarize_text(text):
    """使用Kimi API总结文本"""
    if not KIMI_API_KEY:
        print("错误: 未设置 KIMI_API_KEY 环境变量")
        return "请先设置 KIMI_API_KEY 环境变量"
        
    headers = {
        'Authorization': f'Bearer {KIMI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'moonshot-v1-8k',
        'messages': [
            {'role': 'system', 'content': '请用简洁的语言总结以下文章内容，限制在100字以内。'},
            {'role': 'user', 'content': text}
        ]
    }
    
    try:
        response = requests.post('https://api.moonshot.cn/v1/chat/completions',
                               headers=headers,
                               json=data,
                               timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"生成摘要时出错: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"错误详情: {e.response.text}")
        return "无法生成摘要"

def format_output(article, keywords, summary):
    """格式化输出"""
    output = f"""
{'='*50}
标题: {article['title']}

关键词: {', '.join(keywords)}

文章总结: 
{summary}

公众号: {article['source']['name']}
发布时间: {article['publishedAt']}
原文链接: {article['url']}
{'='*50}
"""
    return output

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({'error': '请提供搜索关键词'}), 400
        
    try:
        articles = get_news(keyword)
        
        if not articles:
            return jsonify({'articles': []})
            
        # 处理每篇文章
        for article in articles:
            content = f"{article['title']} {article['description']}"
            article['keywords'] = extract_keywords(content)
            article['summary'] = summarize_text(content)
            time.sleep(1)  # 避免请求过快
            
        return jsonify({'articles': articles})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
