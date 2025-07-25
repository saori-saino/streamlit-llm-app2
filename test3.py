# test3.py
import sys
import os

# エンコーディングの強制設定
if sys.platform.startswith("win"):
    import locale
    locale.setlocale(locale.LC_ALL, '')

print(f"システムエンコーディング: {sys.getdefaultencoding()}")
print(f"ファイルシステムエンコーディング: {sys.getfilesystemencoding()}")

try:
    # 段階的テスト
    print("1. dotenv読み込みテスト")
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv読み込み成功")
    
    print("2. constants読み込みテスト")
    import constants as ct
    print("✅ constants読み込み成功")
    
    print("3. streamlitインポートテスト")
    import streamlit as st
    print("✅ streamlitインポート成功")
    
    print("4. セッション状態初期化テスト")
    from initialize import initialize_session_state
    initialize_session_state()
    print("✅ セッション状態初期化成功")
    
    print("5. セッションID初期化テスト")
    from initialize import initialize_session_id
    initialize_session_id()
    print("✅ セッションID初期化成功")
    
    print("6. ログ初期化テスト")
    from initialize import initialize_logger
    initialize_logger()
    print("✅ ログ初期化成功")
    
    print("7. データソース読み込みテスト")
    from initialize import load_data_sources
    docs = load_data_sources()
    print(f"✅ データソース読み込み成功: {len(docs)}件")
    
    print("8. adjust_string関数テスト")
    from initialize import adjust_string
    test_str = "テスト文字列"
    result = adjust_string(test_str)
    print(f"✅ adjust_string成功: {result}")
    
except Exception as e:
    print(f"❌ エラー発生: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()