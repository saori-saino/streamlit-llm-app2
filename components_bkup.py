# components.py 

"""
Streamlit画面表示コンポーネント集
"""
import streamlit as st
import constants as ct

def display_app_title():
    """
    アプリケーションのタイトルを表示
    """
    st.title(ct.APP_NAME)
    if hasattr(ct, 'APP_DESCRIPTION'):
        st.markdown(ct.APP_DESCRIPTION)

def display_initial_ai_message():
    """
    AIの初期メッセージを表示
    """
    initial_message = getattr(ct, 'INITIAL_AI_MESSAGE', 
                             "こんにちは。私は社内文書の情報をもとに回答する生成AIチャットボットです。サイドバーで利用目的を選択し、画面下部のチャット欄からメッセージを送信してください。")
    
    with st.chat_message("assistant"):
        st.markdown(f"""
                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;">
                    <span style="color: #2e7d32;">{initial_message}</span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("""
                    <div style="background-color: #fff9c4; padding: 10px; border-radius: 5px;">
                    <span style="color: #8B4513;">
                    ⚠️ 具体的に入力したほうが期待通りの回答を得やすいです。
                    </span>
                    </div>
                    """, unsafe_allow_html=True)

def display_conversation_log():
    """
    会話ログを表示
    """
    if 'messages' in st.session_state:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def display_search_llm_response(llm_response):
    """
    検索モードのLLM回答を表示
    
    Args:
        llm_response: LLMからの回答
    
    Returns:
        str: 表示されたコンテンツ
    """
    if hasattr(llm_response, 'content'):
        content = llm_response.content
    elif isinstance(llm_response, dict) and 'result' in llm_response:
        content = llm_response['result']
    else:
        content = str(llm_response)
    
    st.markdown(content)
    
    # 参照文書がある場合は表示
    if isinstance(llm_response, dict) and 'source_documents' in llm_response:
        st.markdown("**入力内容に関する情報は、以下のファイルに含まれている可能性があります。**")
        for i, doc in enumerate(llm_response['source_documents'], 1):
            with st.expander(f"参照文書 {i}"):
                st.markdown(doc.page_content)
                if hasattr(doc, 'metadata') and doc.metadata:
                    st.json(doc.metadata)
    
    return content

def display_contact_llm_response(llm_response):
    """
    問い合わせモードのLLM回答を表示
    
    Args:
        llm_response: LLMからの回答
    
    Returns:
        str: 表示されたコンテンツ
    """
    if hasattr(llm_response, 'content'):
        content = llm_response.content
    elif isinstance(llm_response, dict) and 'answer' in llm_response:
        content = llm_response['answer']
    else:
        content = str(llm_response)
    
    st.markdown(content)
    
    # 参照文書がある場合は表示
    if isinstance(llm_response, dict) and 'source_documents' in llm_response:
        st.markdown("**参考にした社内文書:**")
        for i, doc in enumerate(llm_response['source_documents'], 1):
            with st.expander(f"参考文書 {i}"):
                st.markdown(doc.page_content)
                if hasattr(doc, 'metadata') and doc.metadata:
                    st.json(doc.metadata)
    
    return content

def placeholder_component():
    """
    プレースホルダーコンポーネント
    """
    st.write("コンポーネント読み込み中...")

    # ...existing code...

def display_sidebar():
    """
    サイドバーを表示
    """
    with st.sidebar:        
        # モード選択をサイドバーに移動
        display_sidebar_mode_selection()
                
def display_sidebar_mode_selection():
    """
    サイドバーでのモード選択を表示
    """
    st.markdown("# 利用目的")
    
    if not hasattr(st.session_state, 'mode'):
        st.session_state.mode = getattr(ct, 'ANSWER_MODE_1', '社内文書検索')
    
    # モード選択のラジオボタン
    modes = [
        getattr(ct, 'ANSWER_MODE_1', '社内文書検索'),
        getattr(ct, 'ANSWER_MODE_2', '社内問い合わせ')
    ]

    st.session_state.mode = st.radio(
         "",
        modes,
        index=modes.index(st.session_state.mode) if st.session_state.mode in modes else 0,
        help=""
    )

    st.markdown("---")

    st.markdown("## 【「社内文書検索」を選択した場合】")
    st.info("📖 入力内容と関連性が高い社内文書のありかを検索できます。")

    st.markdown("""
                <div style="background-color: white; padding: 10px; border-radius: 5px; border: 1px solid #e6e6e6;">
                <strong>【入力例】</strong><br>
                社員の育成方針に関するMTGの議事録
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("## 【「社内問い合わせ」を選択した場合】")
    st.info("💬 質問・要望に対いて、社内文書の情報をもとに回答を得られます。")

    st.markdown("""
                <div style="background-color: white; padding: 10px; border-radius: 5px; border: 1px solid #e6e6e6;">
                <strong>【入力例】</strong><br>
                人事部に所属している従業員情報を一覧化して
                </div>
                """, unsafe_allow_html=True)
    