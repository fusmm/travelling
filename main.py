import streamlit as st
from travel_utils import TravelDeepSeekAPI

# 页面配置
st.set_page_config(
    page_title="文旅智能助手（连续对话版）",
    page_icon="🌍",
    layout="wide"
)

# 初始化会话状态（存储对话历史、当前内容类型）
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # 格式：[{"role": "user/assistant", "content": "..."}]
if "deepseek_api_key" not in st.session_state:
    st.session_state.deepseek_api_key = ""
if "current_content_type" not in st.session_state:
    st.session_state.current_content_type = "景点攻略"

# 页面标题
st.title("🌍 文旅智能助手（连续对话）")
st.markdown("支持基于历史内容继续生成（比如生成榜单后规划行程）")

# 侧边栏：DeepSeek API配置
with st.sidebar:
    st.header("🔑 DeepSeek API 配置")
    deepseek_api_input = st.text_input(
        label="输入DeepSeek API密钥",
        value=st.session_state.deepseek_api_key,
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    )
    st.session_state.deepseek_api_key = deepseek_api_input

# 对话历史展示区
if st.session_state.chat_history:
    st.divider()
    st.subheader("💬 对话历史")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**你**：{msg['content']}")
        else:
            st.markdown(f"**助手**：\n{msg['content']}")
        st.markdown("---")

# 主功能区：内容生成/连续对话输入
st.divider()
col_type, col_input = st.columns([1, 3])

with col_type:
    content_type = st.selectbox(
        label="初始内容类型（首次生成用）",
        options=[
            "景点攻略", "行程规划", "旅游问答", "美食推荐",
            "小众景点推荐", "旅行装备清单生成", "文旅活动文案创作",
            "城市景点榜单"
        ],
        index=0,
        key="content_type_select"
    )
    st.session_state.current_content_type = content_type

with col_input:
    # 首次生成：基于内容类型的提示；连续对话：自定义输入
    if not st.session_state.chat_history:
        placeholder_text = {
            "景点攻略": "例如：北京故宫（核心景点、门票、交通）",
            "行程规划": "例如：成都3日游（亲子游，预算3000元）",
            "旅游问答": "例如：半月板损伤患者去云南旅游，哪些景点适合步行？",
            "美食推荐": "例如：西安回民街周边的特色小吃（不含辣）",
            "小众景点推荐": "例如：浙江周边小众徒步景点（人少、难度低）",
            "旅行装备清单生成": "例如：西藏7日游（9月，户外徒步）",
            "文旅活动文案创作": "例如：杭州西湖秋季摄影活动",
            "城市景点榜单": "例如：上海热门景点榜单（按评分排序）"
        }[content_type]
        user_input = st.text_area(
            label="输入需求（首次生成）",
            placeholder=placeholder_text,
            height=100
        )
    else:
        user_input = st.text_area(
            label="输入后续需求（基于历史内容）",
            placeholder="例如：帮我规划刚才榜单里景点的3日行程",
            height=100
        )

# 参数调节与生成按钮
col_slider, col_btn = st.columns([4, 1])
with col_slider:
    temperature = st.slider(
        label="生成灵活度（0=严谨，1=创意）",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1
    )
with col_btn:
    generate_btn = st.button("生成/继续对话", type="primary", use_container_width=True)

# 生成逻辑（含连续对话）
if generate_btn:
    if not st.session_state.deepseek_api_key:
        st.error("❌ 请先在侧边栏输入DeepSeek API密钥！")
    elif not user_input:
        st.error("❌ 请输入需求内容！")
    else:
        with st.spinner("正在生成内容..."):
            travel_client = TravelDeepSeekAPI(deepseek_api_key=st.session_state.deepseek_api_key)

            # 构建对话消息
            messages = st.session_state.chat_history.copy()

            # 首次生成：添加内容类型的Prompt前缀
            if not messages:
                type_prompt = {
                    "景点攻略": "作为专业文旅顾问，详细介绍以下景点，用Markdown分点：",
                    "行程规划": "为以下需求制定详细行程，按天数分模块（Markdown标题）：",
                    "旅游问答": "解答以下文旅问题，用Markdown分点说明：",
                    "美食推荐": "推荐以下区域的特色美食，用Markdown列表/表格：",
                    "小众景点推荐": "推荐以下区域的小众景点，用Markdown分点：",
                    "旅行装备清单生成": "为以下行程生成装备清单，按类别分类（Markdown二级标题）：",
                    "文旅活动文案创作": "为以下活动创作文案，用Markdown加粗亮点：",
                    "城市景点榜单": "生成以下城市的景点榜单，按热门排序（Markdown三级标题）："
                }[st.session_state.current_content_type]
                user_msg = f"{type_prompt}\n{user_input}"
            else:
                user_msg = user_input

            # 添加当前用户消息
            messages.append({"role": "user", "content": user_msg})

            # 调用API生成
            assistant_msg = travel_client.generate_content(messages, temperature)

            # 更新对话历史
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_msg})

            # 刷新页面显示新内容
            st.rerun()

# 重置对话按钮
if st.session_state.chat_history:
    if st.button("重置对话", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()