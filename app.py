import streamlit as st
import requests
import json
import time
from PIL import Image
import os

# ===================== 讯飞星火配置 =====================
APP_ID = "9c9635e5"
API_KEY = "60792482aeaea33fac508ea5e195a9da"
API_SECRET = "NzAzOWUwYmRlZWY5OTY2YTBhZTg5YTIw"

# ===================== 页面配置 =====================
st.set_page_config(
    page_title="TF AI 智能助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 模型配置
MODEL_CONFIG = {
    "lite": {"model": "lite", "max_tokens": 2048, "url": "https://spark-api-open.xf-yun.com/v1/chat/completions",
             "desc": "⚡ 轻量级 - 快速响应"},
    "pro": {"model": "generalv3", "max_tokens": 4096, "url": "https://spark-api-open.xf-yun.com/v1/chat/completions",
            "desc": "💼 专业版 - 平衡性能"},
    "max": {"model": "generalv3.5", "max_tokens": 8192, "url": "https://spark-api-open.xf-yun.com/v1/chat/completions",
            "desc": "🚀 高性能 - 复杂任务"},
    "x2": {"model": "spark-x", "max_tokens": 4096, "url": "https://spark-api-open.xf-yun.com/x2/chat/completions",
           "desc": "✨ X2版本 - 稳定高效"},
    "ultra": {"model": "4.0Ultra", "max_tokens": 8192, "url": "https://spark-api-open.xf-yun.com/v1/chat/completions",
              "desc": "🌟 4.0 Ultra - 最强能力"}
}

# 初始化 session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_responding" not in st.session_state:
    st.session_state.is_responding = False


def load_logo():
    """加载固定 Logo"""
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            return img
        except Exception as e:
            st.warning(f"加载 Logo 失败: {e}")
    return None


# ===================== 侧边栏 =====================
with st.sidebar:
    # 固定 Logo 区域 - 放大的版本
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_img = load_logo()
        if logo_img is not None:
            # 将宽度从 100 改为 180，让 Logo 更大
            st.image(logo_img, width=280)
        else:
            # 没有图片时，文字也放大
            st.markdown("<h1 style='text-align: center;'>🤖 TF AI</h1>", unsafe_allow_html=True)

    st.markdown("---")

    # 模型选择
    selected_model = st.selectbox(
        "选择模型",
        options=list(MODEL_CONFIG.keys()),
        format_func=lambda x: MODEL_CONFIG[x]['desc'],
        index=4  # 默认选择 x2
    )

    # 显示当前模型详情
    st.info(
        f"**当前模型**: {MODEL_CONFIG[selected_model]['desc']}\n\n**模型ID**: `{MODEL_CONFIG[selected_model]['model']}`")

    st.markdown("---")

    # 新对话按钮
    if st.button("✨ 新对话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.is_responding = False
        st.rerun()

    st.markdown("---")

    # 历史对话列表
    st.markdown("### 📝 历史对话")
    history_items = ["Python编程问题", "机器学习入门", "前端开发技巧", "数据分析方法"]
    for item in history_items:
        st.markdown(f"- {item}")

    st.markdown("---")

    # 用户信息
    st.markdown("### 👤 用户信息")
    st.markdown("**用户**: 访客")
    st.markdown("**状态**: 🟢 在线")

    # 使用说明
    with st.expander("📖 使用说明"):
        st.markdown("""
        - 💡 **Ctrl+Enter** 快速发送消息
        - 🔄 **新对话** 按钮清空聊天记录
        - 🚀 自动重试机制，稳定可靠
        """)

# ===================== 主聊天区域 =====================
st.markdown("# 🤖 TF AI 智能助手")
st.markdown("---")

# 显示聊天记录
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["content"])

# 欢迎消息
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(f"""
        👋 欢迎使用 TF AI 智能助手！

        当前模型：**{MODEL_CONFIG[selected_model]['desc']}**

        我是基于讯飞星火大模型打造的智能助手，可以帮你解决各种问题。

        ✨ 我可以帮你：
        - 💡 解答问题 - 各种知识问答
        - 📝 内容创作 - 写作、翻译、总结
        - 🔧 编程帮助 - 代码调试、算法讲解
        - 💬 日常聊天 - 陪伴式对话

        🚀 **快速开始**：直接在下方输入框提问！
        """)

# ===================== 输入区域 =====================
user_input = st.chat_input("输入你的问题... (Ctrl+Enter 发送)")


def get_response(user_message):
    """调用讯飞星火 API"""
    try:
        config = MODEL_CONFIG[selected_model]
        url = config["url"]
        auth = f"{API_KEY}:{API_SECRET}"
        headers = {"Authorization": f"Bearer {auth}", "Content-Type": "application/json"}

        recent_messages = st.session_state.messages[-10:] if len(
            st.session_state.messages) > 10 else st.session_state.messages
        messages_for_api = recent_messages + [{"role": "user", "content": user_message}]

        payload = {
            "model": config["model"],
            "messages": messages_for_api,
            "temperature": 0.5,
            "max_tokens": config["max_tokens"],
            "stream": False
        }

        response = requests.post(url, headers=headers, json=payload, timeout=90)

        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                return f"❌ API错误: {result['error'].get('message', '未知错误')}"
            else:
                return result["choices"][0]["message"]["content"]
        else:
            return f"❌ HTTP错误: {response.status_code}"

    except requests.exceptions.Timeout:
        return "⏰ 请求超时，请稍后再试"
    except Exception as err:
        return f"❌ 发生错误: {str(err)}"


# 处理用户输入
if user_input and not st.session_state.is_responding:
    st.session_state.is_responding = True

    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 显示用户消息
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # 显示 AI 思考状态
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 思考中...")

        response = get_response(user_input)
        message_placeholder.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    st.session_state.is_responding = False
    st.rerun()
    #streamlit run F:\taifengAI\.venv\app.py //终端输入
