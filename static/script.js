document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const clearBtn = document.getElementById('clearBtn');
    const searchBtn = document.getElementById('searchBtn');
    const newsContainer = document.getElementById('newsContainer');

    // 显示/隐藏清除按钮
    searchInput.addEventListener('input', function() {
        clearBtn.style.display = this.value ? 'block' : 'none';
    });

    // 清除搜索框
    clearBtn.addEventListener('click', function() {
        searchInput.value = '';
        clearBtn.style.display = 'none';
        searchInput.focus();
    });

    // 搜索功能
    searchBtn.addEventListener('click', async function() {
        const keyword = searchInput.value.trim();
        if (!keyword) {
            alert('请输入搜索关键词');
            return;
        }

        searchBtn.disabled = true;
        searchBtn.textContent = '搜索中...';

        try {
            const response = await fetch(`/api/search?keyword=${encodeURIComponent(keyword)}`);
            const data = await response.json();
            
            if (data.articles && data.articles.length > 0) {
                displayNews(data.articles);
            } else {
                newsContainer.innerHTML = '<div class="no-results">未找到相关文章</div>';
            }
        } catch (error) {
            console.error('搜索出错:', error);
            newsContainer.innerHTML = '<div class="no-results">搜索出错，请稍后重试</div>';
        } finally {
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<span class="icon">🤖</span>开始智能采集';
        }
    });

    function displayNews(articles) {
        newsContainer.innerHTML = articles.map(article => `
            <div class="news-card">
                <h3>${article.title}</h3>
                <div class="tags">
                    ${article.keywords.map(keyword => `
                        <span class="tag">${keyword}</span>
                    `).join('')}
                </div>
                <p class="news-content">${article.summary}</p>
                <div class="news-meta">
                    <span>${article.source.name} · ${article.publishedAt}</span>
                    <a href="${article.url}" class="read-more" target="_blank">查看原文 →</a>
                </div>
            </div>
        `).join('');
    }

    // 加载一些示例新闻
    const sampleArticles = [
        {
            title: '人工智能技术在医疗领域的最新应用研究',
            keywords: ['AI医疗', '深度学习', '智能诊断'],
            summary: '本研究探讨了人工智能技术在医疗领域的创新应用，包括影像诊断、疾病预测和个性化治疗方案制定等方面。研究表明，AI辅助诊断的准确率已达到 95% 以上，大大提升了医疗效率。',
            source: { name: 'AI医疗周刊' },
            publishedAt: '2024-01-15',
            url: '#'
        },
        {
            title: '智能制造转型：工业4.0时代的机遇与挑战',
            keywords: ['工业4.0', '智能制造', '数字化转型'],
            summary: '随着工业4.0的深入推进，智能制造正在重塑传统制造业。报告指出，采用智能制造解决方案的企业生产效率平均提升了 35%，运营成本降低了 20%。',
            source: { name: '工业前沿' },
            publishedAt: '2024-01-14',
            url: '#'
        }
    ];

    displayNews(sampleArticles);
});
