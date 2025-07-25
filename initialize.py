"""
このファイルは、最初の画面読み込み時にのみ実行される初期化処理が記述されたファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from uuid import uuid4
import sys
import unicodedata
from dotenv import load_dotenv
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import constants as ct


############################################################
# 設定関連
############################################################
# 「.env」ファイルで定義した環境変数の読み込み
load_dotenv()

############################################################
# 関数定義
############################################################

def initialize():
    """
    画面読み込み時に実行する初期化処理
    """
    # 初期化データの用意
    initialize_session_state()
    # ログ出力用にセッションIDを生成
    initialize_session_id()
    # ログ出力の設定
    initialize_logger()
    # RAGのRetrieverを作成
    initialize_retriever()


def initialize_logger():
    """
    ログ出力の設定
    """
    # 指定のログフォルダが存在すれば読み込み、存在しなければ新規作成
    os.makedirs(ct.LOG_DIR_PATH, exist_ok=True)
    
    # 引数に指定した名前のロガー（ログを記録するオブジェクト）を取得
    # 再度別の箇所で呼び出した場合、すでに同じ名前のロガーが存在していれば読み込む
    logger = logging.getLogger(ct.LOGGER_NAME)

    # すでにロガーにハンドラー（ログの出力先を制御するもの）が設定されている場合、同じログ出力が複数回行われないよう処理を中断する
    if logger.hasHandlers():
        return

    # 1日単位でログファイルの中身をリセットし、切り替える設定
    log_handler = TimedRotatingFileHandler(
        os.path.join(ct.LOG_DIR_PATH, ct.LOG_FILE),
        when="D",
        encoding="utf8"
    )
    # 出力するログメッセージのフォーマット定義
    # - 「levelname」: ログの重要度（INFO, WARNING, ERRORなど）
    # - 「asctime」: ログのタイムスタンプ（いつ記録されたか）
    # - 「lineno」: ログが出力されたファイルの行番号
    # - 「funcName」: ログが出力された関数名
    # - 「session_id」: セッションID（誰のアプリ操作か分かるように）
    # - 「message」: ログメッセージ
    formatter = logging.Formatter(
        f"[%(levelname)s] %(asctime)s line %(lineno)s, in %(funcName)s, session_id={st.session_state.session_id}: %(message)s"
    )

    # 定義したフォーマッターの適用
    log_handler.setFormatter(formatter)

    # ログレベルを「INFO」に設定
    logger.setLevel(logging.INFO)

    # 作成したハンドラー（ログ出力先を制御するオブジェクト）を、
    # ロガー（ログメッセージを実際に生成するオブジェクト）に追加してログ出力の最終設定
    logger.addHandler(log_handler)


def initialize_session_id():
    """
    セッションIDの作成
    """
    if "session_id" not in st.session_state:
        # ランダムな文字列（セッションID）を、ログ出力用に作成
        st.session_state.session_id = uuid4().hex


def initialize_retriever():
    """
    画面読み込み時にRAGのRetriever（ベクターストアから検索するオブジェクト）を作成
    """
    # ロガーを読み込むことで、後続の処理中に発生したエラーなどがログファイルに記録される
    logger = logging.getLogger(ct.LOGGER_NAME)

    # すでにRetrieverが作成済みの場合、後続の処理を中断
    if "retriever" in st.session_state:
        return
    
    # RAGの参照先となるデータソースの読み込み
    docs_all = load_data_sources()

    # OSがWindowsの場合、Unicode正規化と、cp932（Windows用の文字コード）で表現できない文字を除去
    for doc in docs_all:
        doc.page_content = adjust_string(doc.page_content)
        for key in doc.metadata:
            doc.metadata[key] = adjust_string(doc.metadata[key])
    
    # 埋め込みモデルの用意
    embeddings = OpenAIEmbeddings()
    
    # チャンク分割用のオブジェクトを作成
    text_splitter = CharacterTextSplitter(
# 問題2修正 start--------------------------------------------
        chunk_size=ct.chunk_size_num,
        chunk_overlap=ct.chunk_overlap_num,
        separator="\n"
#         chunk_size=500,
#         chunk_overlap=50,
#         separator="\n"
# 問題2修正 end----------------------------------------------
    )

    # チャンク分割を実施
    splitted_docs = text_splitter.split_documents(docs_all)

    # ベクターストアの作成
    db = Chroma.from_documents(splitted_docs, embedding=embeddings)

    # ベクターストアを検索するRetrieverの作成
# 問題2修正 start--------------------------------------------
    st.session_state.retriever = db.as_retriever(search_kwargs={"k": ct.k_num}) 
#    st.session_state.retriever = db.as_retriever(search_kwargs={"k": 5})    #問題1
#    st.session_state.retriever = db.as_retriever(search_kwargs={"k": 3})    #問題1
# 問題2修正 end----------------------------------------------


def initialize_session_state():
    """
    初期化データの用意
    """
    if "messages" not in st.session_state:
        # 「表示用」の会話ログを順次格納するリストを用意
        st.session_state.messages = []
        # 「LLMとのやりとり用」の会話ログを順次格納するリストを用意
        st.session_state.chat_history = []

def load_data_sources():
    """
    RAGの参照先となるデータソースの読み込み（エンコーディング対応版）
    """
    import logging
    from langchain_community.document_loaders import WebBaseLoader
    import requests
    from bs4 import BeautifulSoup
    
    docs_all = []
    logger = logging.getLogger(ct.LOGGER_NAME) if hasattr(ct, 'LOGGER_NAME') else None
    
    try:
        print("DEBUG: ファイル読み込み開始")
        
        # データフォルダの存在確認
        if not os.path.exists(ct.RAG_TOP_FOLDER_PATH):
            print(f"DEBUG: データフォルダが存在しません: {ct.RAG_TOP_FOLDER_PATH}")
            os.makedirs(ct.RAG_TOP_FOLDER_PATH, exist_ok=True)
            print(f"DEBUG: データフォルダを作成しました")
            return docs_all
            
        print(f"DEBUG: データフォルダ確認完了: {ct.RAG_TOP_FOLDER_PATH}")
        
        # ファイル読み込み処理
        try:
            recursive_file_check(ct.RAG_TOP_FOLDER_PATH, docs_all)
            print(f"DEBUG: ファイル読み込み完了: {len(docs_all)}件")
        except Exception as e:
            print(f"DEBUG: ファイル読み込みエラー: {type(e).__name__}: {str(e)}")
            if logger:
                logger.error(f"ファイル読み込みエラー: {e}")
        
    except Exception as e:
        print(f"DEBUG: データフォルダ処理エラー: {type(e).__name__}: {str(e)}")
        if logger:
            logger.error(f"データフォルダ処理エラー: {e}")

    # Web読み込み処理（エンコーディング対応版）
    try:
        print("DEBUG: Web読み込み開始")
        web_docs_all = []
        
        if hasattr(ct, 'WEB_URL_LOAD_TARGETS') and ct.WEB_URL_LOAD_TARGETS:
            for web_url in ct.WEB_URL_LOAD_TARGETS:
                try:
                    print(f"DEBUG: Web読み込み中: {web_url}")
                    
                    # 安全なWeb読み込み処理
                    web_docs = safe_web_load(web_url)
                    web_docs_all.extend(web_docs)
                    
                    print(f"DEBUG: Web読み込み成功: {web_url} ({len(web_docs)}件)")
                    
                except Exception as e:
                    print(f"DEBUG: Web読み込みエラー {web_url}: {type(e).__name__}: {str(e)}")
                    if logger:
                        logger.warning(f"Web読み込みエラー {web_url}: {e}")
        else:
            print("DEBUG: WEB_URL_LOAD_TARGETSが未定義または空です")
        
        docs_all.extend(web_docs_all)
        print(f"DEBUG: Web読み込み完了: {len(web_docs_all)}件")
        
    except Exception as e:
        print(f"DEBUG: Web読み込み処理エラー: {type(e).__name__}: {str(e)}")
        if logger:
            logger.error(f"Web読み込み処理エラー: {e}")
    
    print(f"DEBUG: 総データソース数: {len(docs_all)}件")
    return docs_all

def safe_web_load(url):
    """
    安全なWeb読み込み処理（エンコーディング対応強化版）
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        from langchain.docstore.document import Document
        
        # requestsを使用して安全にWebページを取得
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        print(f"DEBUG: HTTP リクエスト開始: {url}")
        
        # セッション使用でエンコーディング問題を回避
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        print(f"DEBUG: レスポンス取得成功 (ステータス: {response.status_code})")
        
        # エンコーディングを明示的にUTF-8に設定
        response.encoding = 'utf-8'
        
        # response.textを使用してUnicodeテキストを取得
        html_content = response.text
        
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # テキストを抽出
        text_content = soup.get_text(separator='\n', strip=True)
        
        # エンコーディング調整（強化版）
        text_content = adjust_string_enhanced(text_content)
        
        # タイトル取得（安全に）
        title = "Untitled"
        try:
            if soup.title and soup.title.string:
                title = adjust_string_enhanced(soup.title.string.strip())
        except:
            title = "Untitled"
        
        # ドキュメント作成
        doc = Document(
            page_content=text_content,
            metadata={
                "source": url,
                "title": title,
                "encoding": "utf-8"
            }
        )
        
        print(f"DEBUG: ドキュメント作成成功 (文字数: {len(text_content)})")
        return [doc]
        
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: HTTP リクエストエラー: {str(e)}")
        return []
    except UnicodeError as e:
        print(f"DEBUG: エンコーディングエラー: {str(e)}")
        return []
    except Exception as e:
        print(f"DEBUG: Web読み込み予期しないエラー: {type(e).__name__}: {str(e)}")
        return []
    
def recursive_file_check(path, docs_all):
    """
    RAGの参照先となるデータソースの読み込み

    Args:
        path: 読み込み対象のファイル/フォルダのパス
        docs_all: データソースを格納する用のリスト
    """
    # パスがフォルダかどうかを確認
    if os.path.isdir(path):
        # フォルダの場合、フォルダ内のファイル/フォルダ名の一覧を取得
        files = os.listdir(path)
        # 各ファイル/フォルダに対して処理
        for file in files:
            # ファイル/フォルダ名だけでなく、フルパスを取得
            full_path = os.path.join(path, file)
            # フルパスを渡し、再帰的にファイル読み込みの関数を実行
            recursive_file_check(full_path, docs_all)
    else:
        # パスがファイルの場合、ファイル読み込み
        file_load(path, docs_all)


def file_load(path, docs_all):
    """
    ファイル読み込み処理（エラーハンドリング強化版）
    """
    try:
        print(f"DEBUG: ファイル処理開始: {path}")
        
        # ファイル拡張子の取得
        file_extension = os.path.splitext(path)[1].lower()
        print(f"DEBUG: ファイル拡張子: {file_extension}")
        
        # 想定していたファイル形式の場合のみ読み込む
        if file_extension in ct.SUPPORTED_EXTENSIONS:
            print(f"DEBUG: サポート対象ファイル: {file_extension}")
            
            # ファイルの拡張子に合ったdata loaderを使ってデータ読み込み
            try:
                loader = ct.SUPPORTED_EXTENSIONS[file_extension](path)
                docs = loader.load()
                
                # 各ドキュメントに対してエンコーディング処理
                for doc in docs:
                    try:
                        # ページ内容の調整
                        if hasattr(doc, 'page_content') and doc.page_content:
                            doc.page_content = adjust_string(doc.page_content)
                        
                        # メタデータの調整
                        if hasattr(doc, 'metadata') and doc.metadata:
                            for key in doc.metadata:
                                if isinstance(doc.metadata[key], str):
                                    doc.metadata[key] = adjust_string(doc.metadata[key])
                                    
                    except Exception as e:
                        print(f"DEBUG: ドキュメント調整エラー: {type(e).__name__}: {str(e)}")
                        # エラーが発生したドキュメントはスキップ
                        continue
                
                docs_all.extend(docs)
                print(f"DEBUG: ファイル読み込み成功: {path} ({len(docs)}件)")
                
            except Exception as e:
                print(f"DEBUG: ローダーエラー {path}: {type(e).__name__}: {str(e)}")
                
        else:
            print(f"DEBUG: 非サポートファイル: {file_extension}")
            
    except Exception as e:
        print(f"DEBUG: ファイル処理エラー {path}: {type(e).__name__}: {str(e)}")

def adjust_string(s):
    """
    Windows環境でRAGが正常動作するよう調整（修正版）
    
    Args:
        s: 調整を行う文字列
    
    Returns:
        調整を行った文字列
    """
    if not isinstance(s, str):
        return str(s) if s is not None else ""

    if not s.strip():
        return s

    try:
        # OSがWindowsの場合、Unicode正規化と安全な文字処理
        if sys.platform.startswith("win"):
            # Unicode正規化
            s = unicodedata.normalize('NFC', s)
            
            # 制御文字を除去
            import re
            s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', s)
            
            # UTF-8エンコーディングで安全に処理
            try:
                s = s.encode("utf-8", "ignore").decode("utf-8")
                return s
            except Exception:
                # エラー時はASCII文字のみを残す
                s = ''.join(char for char in s if ord(char) < 128)
                return s
        
        # OSがWindows以外の場合はそのまま返す
        return s
        
    except Exception as e:
        print(f"DEBUG: adjust_string エラー: {type(e).__name__}: {str(e)}")
        try:
            return ''.join(char for char in str(s) if ord(char) < 128)
        except:
            return "encoding_error"

def adjust_string_enhanced(s):
    """
    Windows環境でRAGが正常動作するよう調整（Web対応強化版）
    """
    if not isinstance(s, str):
        return str(s) if s is not None else ""

    if not s.strip():
        return s

    try:
        # まず、文字列をUTF-8で正規化
        import unicodedata
        s = unicodedata.normalize('NFC', s)
        
        # 制御文字・特殊文字を除去
        import re
        # 制御文字を除去（改行・タブは保持）
        s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', s)
        # 不可視文字を除去
        s = re.sub(r'[\u200b-\u200f\u2028-\u202f\u205f-\u206f]', '', s)
        
        # UTF-8での処理を強制
        try:
            # UTF-8でエンコード・デコードして安全な文字列にする
            s_bytes = s.encode("utf-8", "replace")  # replaceでエラー文字を置換
            s = s_bytes.decode("utf-8")
        except Exception:
            # 最終的にはASCII範囲のみ残す
            s = ''.join(char for char in s if ord(char) < 128)
        
        # 連続する空白・改行を整理
        s = re.sub(r'\n\s*\n', '\n\n', s)  # 複数改行を2つまでに
        s = re.sub(r'[ \t]+', ' ', s)      # 複数スペースを1つに
        
        return s.strip()
        
    except Exception as e:
        print(f"DEBUG: adjust_string_enhanced エラー: {type(e).__name__}: {str(e)}")
        # 最後の手段：printable ASCII文字のみ残す
        try:
            import string
            return ''.join(char for char in str(s) if char in string.printable)
        except:
            return "encoding_error"