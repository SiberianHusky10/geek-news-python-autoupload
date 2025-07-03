"""
爬虫配置文件
"""

# 超时配置
TIMEOUT_CONFIG = {
    "page_timeout": 90000,  # 页面加载超时时间（毫秒）
    "delay_before_return_html": 5.0,  # 返回HTML前的延迟时间（秒）
    "js_execution_timeout": 30000,  # JavaScript执行超时时间（毫秒）
}

# 浏览器配置
BROWSER_CONFIG = {
    "headless": True,
    "browser_type": "chromium",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "viewport": {"width": 1920, "height": 1080},
}

# 重试配置
RETRY_CONFIG = {
    "max_retries": 3,
    "base_delay": 10,  # 基础延迟时间（秒）
    "backoff_factor": 1.5,  # 退避因子
}

# 等待条件
WAIT_CONDITIONS = {
    "readhub": {
        "css_selector": ".style_item__CkRvg",
        "timeout": 30000,
    }
}

# JavaScript代码片段
JS_SNIPPETS = {
    "scroll_and_wait": [
        "window.scrollTo(0, document.body.scrollHeight);",
        "await new Promise(resolve => setTimeout(resolve, 3000));",
        "window.scrollTo(0, 0);",
        "await new Promise(resolve => setTimeout(resolve, 1000));"
    ],
    "wait_for_content": [
        "await new Promise(resolve => setTimeout(resolve, 5000));"
    ]
}
