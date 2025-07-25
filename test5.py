# test5.py - メッセージ処理テスト
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

print("=== メッセージ処理テスト ===")

try:
    # 1. 初期化処理
    print("1. 初期化テスト")
    from initialize import initialize
    initialize()
    print("✅ 初期化成功")
    
    # 2. セッション状態確認
    print("2. セッション状態確認")
    print(f"retriever存在: {'retriever' in st.session_state}")
    if 'retriever' in st.session_state:
        print(f"retriever型: {type(st.session_state.retriever)}")
    
    # 3. LLM回答テスト
    print("3. LLM回答テスト")
    from utils import get_llm_response
    
    test_message = "テスト質問です"
    response = get_llm_response(test_message)
    print(f"✅ LLM回答成功: {type(response)}")
    
except Exception as e:
    print(f"❌ エラー発生: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()