# utils.py 
import constants as ct

def build_error_message(error_type="初期化処理", additional_info=""):
    """
    エラーメッセージを構築する関数
    
    Args:
        error_type (str): エラーの種類（既に完成されたメッセージまたはエラータイプ）
        additional_info (str): 追加情報
    
    Returns:
        str: 構築されたエラーメッセージ
    """
    # error_typeが既に完成されたメッセージかチェック
    if "失敗しました" in error_type or "エラー" in error_type:
        # 既に完成されたメッセージの場合
        base_message = error_type
    else:
        # エラータイプのみの場合
        base_message = f"{error_type}に失敗しました。"
    
    if additional_info:
        base_message += f" 詳細: {additional_info}"
    
    base_message += " このエラーが繰り返し発生する場合は、管理者にお問い合わせください。"
    return base_message

def get_llm_response(user_message):
    """
    LLMからの回答を取得する関数（サイドバー設定対応版）
    """
    import streamlit as st
    from langchain.chains import RetrievalQA
    from langchain_openai import ChatOpenAI
    
    try:
        # Retrieverが初期化されているかチェック
        if 'retriever' not in st.session_state:
            raise Exception("Retrieverが初期化されていません")
        
        # サイドバーの設定を取得
        search_k = getattr(st.session_state, 'search_k', 15)
#        search_type = getattr(st.session_state, 'search_type', 'similarity')
        
        # Retrieverの設定を更新
        retriever = st.session_state.retriever
        retriever.search_kwargs = {
            "k": search_k,
#            "search_type": search_type
        }
        
        # LLMの設定
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0
        )
        
        # RAGチェーンの作成
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        
        # 選択されたモードに応じたプロンプト調整
        mode = getattr(st.session_state, 'mode', '社内文書検索')
        if mode == '社内問い合わせ':
            user_message = f"以下の質問に、社内文書の情報を参考に丁寧に回答してください：\n{user_message}"
        
        # 質問を実行
        response = qa_chain({"query": user_message})
        return response
        
    except Exception as e:
        raise Exception(f"LLM回答取得エラー: {str(e)}")
    
    # utils.py に以下の関数を追加

def get_source_icon(file_path):
    """
    ファイルパスに応じたアイコンを返す関数
    
    Args:
        file_path (str): ファイルパス
    
    Returns:
        str: アイコン文字列
    """
    import os
    
    # ファイル拡張子を取得
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # 拡張子に応じてアイコンを返す
    icon_map = {
        '.pdf': '📄',
        '.docx': '📝',
        '.doc': '📝',
        '.txt': '📃',
        '.xlsx': '📊',
        '.xls': '📊',
        '.pptx': '📊',
        '.ppt': '📊',
        '.csv': '📋',
        'http': '🌐',  # Web URL用
        'https': '🌐'  # Web URL用
    }
    
    # URLの場合
    if file_path.startswith(('http://', 'https://')):
        return icon_map.get('http', '🌐')
    
    # ファイル拡張子に応じたアイコンを返す
    return icon_map.get(file_extension, '📁')

def get_filename_from_path(file_path):
    """
    ファイルパスからファイル名を取得する関数
    
    Args:
        file_path (str): ファイルパス
    
    Returns:
        str: ファイル名
    """
    import os
    
    # URLの場合
    if file_path.startswith(('http://', 'https://')):
        return file_path
    
    # ローカルファイルの場合
    return os.path.basename(file_path)