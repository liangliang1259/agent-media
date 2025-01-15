# Agent Media - 新闻搜索与分析工具

这是一个简单的新闻搜索和分析工具，可以根据关键词搜索最新新闻，并提供关键词提取和内容总结功能。

## 功能特点

- 关键词搜索最新新闻
- 自动提取文章关键词
- AI驱动的内容总结
- 优雅的格式化输出
- 包含新闻来源和原文链接

## 安装说明

1. 克隆项目到本地
2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
3. 在项目根目录创建 `.env` 文件，添加必要的API密钥
4. 运行程序：
   ```
   python news_analyzer.py
   ```

## 环境要求

- Python 3.7+
- NewsAPI 密钥
- OpenAI API 密钥

## 使用说明

1. 运行程序后，输入想要搜索的关键词
2. 程序将自动搜索相关新闻并进行处理
3. 结果将以格式化的方式显示，包含标题、关键词、总结和来源信息
