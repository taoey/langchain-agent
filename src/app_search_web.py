import streamlit as st
from src.utils.tool_web_client import get_web_content


def fetch_url_result(url):
    """异步抓取 URL"""
    try:
        result_markdown = get_web_content(url)
        return {
            "success": True,
            "markdown": result_markdown,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Streamlit 应用入口"""
    st.set_page_config(
        page_title="网页搜索工具",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🌐 网页抓取工具")
    st.markdown("在此输入要抓取的 URL，右侧将显示网页内容。")

    # 创建列布局：左侧 URL 输入，右侧显示结果
    col1, col2 = st.columns([3, 1])

    with col1:
        # URL 输入框
        url = st.text_input(
            "请输入 URL",
            value="https://mp.weixin.qq.com/s/Tms9fKt6rJVb1Lbb6p7AxA"
        )

        # 运行按钮
        if st.button("🚀 抓取网页"):
            if url:
                # 显示加载状态
                with st.status("正在抓取...", expanded=True) as status:
                    result = fetch_url_result(url)
                    
                    if result["success"]:
                        status.update(state="complete")
                        st.success("抓取成功!")
                        st.markdown("---")
                        
                        # 显示结果（Markdown 格式）
                        st.subheader("📄 网页内容")
                        st.markdown(result["markdown"])
                    else:
                        status.update(state="error")
                        st.error("抓取失败!")
                        st.error(f"错误信息：{result['error']}")
                        st.stop()
                    
                    # 更新状态为完成
                    status.update(state="complete")


if __name__ == "__main__":
    main()