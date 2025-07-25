"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# 1. ライブラリの読み込み
############################################################
# 「.env」ファイルから環境変数を読み込むための関数
from dotenv import load_dotenv
# ログ出力を行うためのモジュール
import logging
# streamlitアプリの表示を担当するモジュール
import streamlit as st
# （自作）画面表示以外の様々な関数が定義されているモジュール
import utils
# （自作）アプリ起動時に実行される初期化処理が記述された関数
from initialize import initialize
# （自作）画面表示系の関数が定義されているモジュール
import components as cn
# （自作）変数（定数）がまとめて定義・管理されているモジュール
import constants as ct


############################################################
# 2. 設定関連
############################################################
# ブラウザタブの表示文言を設定
st.set_page_config(
    page_title=ct.APP_NAME
)

# ログ出力を行うためのロガーの設定
logger = logging.getLogger(ct.LOGGER_NAME)

# ★デバッグコードここから
# main.py の初期化処理前に追加
import sys
import os

# デバッグ情報をStreamlit画面に表示
st.write("🔍 **デバッグ情報**")
st.write(f"- Python version: {sys.version}")
st.write(f"- Current directory: {os.getcwd()}")
st.write(f"- Files in directory: {os.listdir('.')}")
st.write(f"- Streamlit version: {st.__version__}")

# 環境変数の確認
st.write("**環境変数確認:**")
streamlit_env = os.getenv('STREAMLIT_SHARING_MODE', 'ローカル環境')
st.write(f"- 実行環境: {streamlit_env}")

# Secretsの確認
st.write("**Secrets確認:**")
try:
    secrets_check = st.secrets.get("OPENAI_API_KEY", "設定なし")
    if secrets_check != "設定なし":
        st.write("✅ OPENAI_API_KEY: 設定済み")
    else:
        st.write("❌ OPENAI_API_KEY: 未設定")
except Exception as e:
    st.write(f"❌ Secrets確認エラー: {e}")

st.write("---")

st.write("📦 **ライブラリ詳細確認**")

# 重要なライブラリのバージョン確認
libraries_to_check = [
    'streamlit', 'langchain', 'openai', 'chromadb', 
    'langchain_openai', 'langchain_community', 'pandas', 'numpy'
]

for lib_name in libraries_to_check:
    try:
        module = __import__(lib_name)
        version = getattr(module, '__version__', 'バージョン不明')
        st.write(f"✅ {lib_name}: {version}")
    except ImportError as e:
        st.write(f"❌ {lib_name}: インポートエラー - {e}")
    except Exception as e:
        st.write(f"⚠️ {lib_name}: エラー - {e}")

st.write("---")


# OpenAI接続テスト
st.write("🔑 **OpenAI接続テスト**")
try:
    import openai
    # APIキーの設定
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    st.write("✅ OpenAI APIキー設定完了")
    
    # 簡単な接続テスト
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        # モデルリスト取得（軽い処理）
        # models = client.models.list()
        st.write("✅ OpenAI API接続確認完了")
    except Exception as e:
        st.write(f"⚠️ OpenAI API接続テストエラー: {e}")
        
except Exception as e:
    st.write(f"❌ OpenAI設定エラー: {e}")

st.write("---")
# ★デバッグコードここまで

############################################################
# 3. 初期化処理
############################################################
try:
    # 初期化処理（「initialize.py」の「initialize」関数を実行）
    initialize()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()

# アプリ起動時のログファイルへの出力
if not "initialized" in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)


############################################################
# 4. 初期表示
############################################################
# サイドバーの表示
cn.display_sidebar()

# タイトル表示
cn.display_app_title()

## モード表示
# cn.display_select_mode()

# AIメッセージの初期表示
cn.display_initial_ai_message()

############################################################
# 5. 会話ログの表示
############################################################
try:
    # 会話ログの表示
    cn.display_conversation_log()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()


############################################################
# 6. チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)


############################################################
# 7. チャット送信時の処理
############################################################
if chat_message:
    # ==========================================
    # 7-1. ユーザーメッセージの表示
    # ==========================================
    # ユーザーメッセージのログ出力
    logger.info({"message": chat_message, "application_mode": st.session_state.mode})

    # ユーザーメッセージを表示
    with st.chat_message("user"):
        st.markdown(chat_message)

    # ==========================================
    # 7-2. LLMからの回答取得
    # ==========================================
    # 「st.spinner」でグルグル回っている間、表示の不具合が発生しないよう空のエリアを表示
    res_box = st.empty()
    # LLMによる回答生成（回答生成が完了するまでグルグル回す）
    with st.spinner(ct.SPINNER_TEXT):
        try:
            # 画面読み込み時に作成したRetrieverを使い、Chainを実行
            llm_response = utils.get_llm_response(chat_message)
        except Exception as e:
            # エラーログの出力
            logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
            # エラーメッセージの画面表示
            st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            # 後続の処理を中断
            st.stop()
    
    # ==========================================
    # 7-3. LLMからの回答表示
    # ==========================================
    with st.chat_message("assistant"):
        try:
            # ==========================================
            # モードが「社内文書検索」の場合
            # ==========================================
            if st.session_state.mode == ct.ANSWER_MODE_1:
                # 入力内容と関連性が高い社内文書のありかを表示
                content = cn.display_search_llm_response(llm_response)

            # ==========================================
            # モードが「社内問い合わせ」の場合
            # ==========================================
            elif st.session_state.mode == ct.ANSWER_MODE_2:
                # 入力に対しての回答と、参照した文書のありかを表示
                content = cn.display_contact_llm_response(llm_response)
            
            # AIメッセージのログ出力
            logger.info({"message": content, "application_mode": st.session_state.mode})
        except Exception as e:
            # エラーログの出力
            logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{e}")
            # エラーメッセージの画面表示
            st.error(utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            # 後続の処理を中断
            st.stop()

    # ==========================================
    # 7-4. 会話ログへの追加
    # ==========================================
    # 表示用の会話ログにユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": chat_message})
    # 表示用の会話ログにAIメッセージを追加
    st.session_state.messages.append({"role": "assistant", "content": content})