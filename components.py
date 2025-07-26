# components.py 

"""
Streamlit画面表示コンポーネント集
"""
import streamlit as st
import constants as ct
import utils

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
    「社内文書検索」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """

     # LLMからのレスポンスに参照元情報が入っており、かつ「該当資料なし」が回答として返された場合
    if llm_response["source_documents"] and llm_response["result"] != ct.NO_DOC_MATCH_ANSWER:

        # ==========================================
        # ユーザー入力値と最も関連性が高いメインドキュメントのありかを表示
        # ==========================================
        main_file_path = llm_response["source_documents"][0].metadata["source"]

        # 補足メッセージの表示
        main_message = "入力内容に関する情報は、以下のファイルに含まれている可能性があります。"
        st.markdown(main_message)
        
        # アイコンを直接定義（utils.get_source_icon を使わない）
        if main_file_path.startswith(('http://', 'https://')):
            icon = '🌐'
        elif main_file_path.endswith('.pdf'):
            icon = '📄'
        elif main_file_path.endswith(('.docx', '.doc')):
            icon = '📝'
        elif main_file_path.endswith(('.xlsx', '.xls')):
            icon = '📊'
        elif main_file_path.endswith('.txt'):  # ← この行を追加
            icon = '📃'
        else:
            icon = '📁'
        
        # ページ番号が取得できた場合のみ、ページ番号を表示
        if "page" in llm_response["source_documents"][0].metadata:
            main_page_number = int(llm_response["source_documents"][0].metadata["page"]) 
            st.success(f"{main_file_path} (ページ: {main_page_number + 1})", icon=icon)
        else:
            st.success(f"{main_file_path}", icon=icon)
        
        # ==========================================
        # ユーザー入力値と関連性が高いサブドキュメントのありかを表示
        # ==========================================
        # メインドキュメント以外で、関連性が高いサブドキュメントを格納する用のリストを用意
        sub_choices = []
        # 重複チェック用のリストを用意
        duplicate_check_list = []

        # ドキュメントが2件以上検索できた場合（サブドキュメントが存在する場合）のみ、サブドキュメントのありかを一覧表示
        # 「source_documents」内のリストの2番目以降をスライスで参照（2番目以降がなければfor文内の処理は実行されない）
        for document in llm_response["source_documents"][1:]:
            # ドキュメントのファイルパスを取得
            sub_file_path = document.metadata["source"]

            # メインドキュメントのファイルパスと重複している場合、処理をスキップ（表示しない）
            if sub_file_path == main_file_path:
                continue
            
            # 同じファイル内の異なる箇所を参照した場合、2件目以降のファイルパスに重複が発生する可能性があるため、重複を除去
            if sub_file_path in duplicate_check_list:
                continue

            # 重複チェック用のリストにファイルパスを順次追加
            duplicate_check_list.append(sub_file_path)
            
            # ページ番号が取得できない場合のための分岐処理
            if "page" in document.metadata:
                # ページ番号を取得
                sub_page_number = int(document.metadata["page"])
                # 「サブドキュメントのファイルパス」と「ページ番号」の辞書を作成
                sub_choice = {"source": sub_file_path, "page_number": sub_page_number}
            else:
                # 「サブドキュメントのファイルパス」の辞書を作成
                sub_choice = {"source": sub_file_path}
            
            # 後ほど一覧表示するため、サブドキュメントに関する情報を順次リストに追加
            sub_choices.append(sub_choice)
        
        # サブドキュメントが存在する場合のみの処理
        if sub_choices:
            # 補足メッセージの表示
            sub_message = "その他、ファイルありかの候補を提示します。"
            st.markdown(sub_message)

            # サブドキュメントに対してのループ処理
            for sub_choice in sub_choices:
                # 参照元のありかに応じて、適したアイコンを取得
                icon = utils.get_source_icon(sub_choice['source'])
                # ページ番号が取得できない場合のための分岐処理

                if "page_number" in sub_choice:
                    # 「サブドキュメントのファイルパス」と「ページ番号」を表示
                    sub_choice_page_number = int(sub_choice["page_number"] ) 
#                    st.info(f"{sub_choice['source']} (ページ: {sub_choice['page_number']})", icon=icon)
                    st.info(f"{sub_choice['source']} (ページ: {sub_choice_page_number + 1})", icon=icon)
#                    st.info(f"{sub_choice['source']}", icon=icon)
                else:
                    # 「サブドキュメントのファイルパス」を表示
                    st.info(f"{sub_choice['source']}", icon=icon)
        
        # 表示用の会話ログに格納するためのデータを用意
        # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
        # - 「main_message」: メインドキュメントの補足メッセージ
        # - 「main_file_path」: メインドキュメントのファイルパス
        # - 「main_page_number」: メインドキュメントのページ番号
        # - 「sub_message」: サブドキュメントの補足メッセージ
        # - 「sub_choices」: サブドキュメントの情報リスト
        content = {}
        content["mode"] = ct.ANSWER_MODE_1
        content["main_message"] = main_message
        content["main_file_path"] = main_file_path
        # メインドキュメントのページ番号は、取得できた場合にのみ追加
        if "page" in llm_response["source_documents"][0].metadata:
            content["main_page_number"] = int(main_page_number)
        # サブドキュメントの情報は、取得できた場合にのみ追加
        if sub_choices:
            content["sub_message"] = sub_message
            content["sub_choices"] = sub_choices
    
    # LLMからのレスポンスに、ユーザー入力値と関連性の高いドキュメント情報が入って「いない」場合
    else:
        # 関連ドキュメントが取得できなかった場合のメッセージ表示
        st.markdown(ct.NO_DOC_MATCH_MESSAGE)

        # 表示用の会話ログに格納するためのデータを用意
        # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
        # - 「answer」: LLMからの回答
        # - 「no_file_path_flg」: ファイルパスが取得できなかったことを示すフラグ（画面を再描画時の分岐に使用）
        content = {}
        content["mode"] = ct.ANSWER_MODE_1
        content["result"] = ct.NO_DOC_MATCH_MESSAGE
        content["no_file_path_flg"] = True
    
    return content

def display_contact_llm_response(llm_response):
    """
    「社内問い合わせ」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """
    # LLMからの回答を表示
    st.markdown(llm_response["result"])
    
    print(f"DEBUG: 社内問い合わせモード開始")
    print(f"DEBUG: source_documents count: {len(llm_response.get('source_documents', []))}")
    
    # ユーザーの質問・要望に適切な回答を行うための情報が、社内文書のデータベースに存在しなかった場合
    if llm_response["result"] != ct.INQUIRY_NO_MATCH_ANSWER:
        # 区切り線を表示
        st.divider()

        # 補足メッセージを表示
        message = "情報源"
        st.markdown(f"##### {message}")

        # 参照元のファイルパスの一覧を格納するためのリストを用意
        file_path_list = []
        file_info_list = []
        # LLMが回答生成の参照元として使ったドキュメントの一覧が「context」内のリストの中に入っているため、ループ処理
        for document in llm_response["source_documents"]:
            # ファイルパスを取得
            print("ポイント0")
            file_path = document.metadata["source"]
            # ファイルパスの重複は除去

#            print(f"DEBUG: 文書{i+1}: {file_path}")
            print(f"DEBUG: メタデータ: {document.metadata}")

            if file_path in file_path_list:
                continue

            print("ポイント1")
            # ページ番号が取得できた場合のみ、ページ番号を表示（ドキュメントによっては取得できない場合がある）
            if "page" in document.metadata:
                # ページ番号を取得
                print("ポイント2")
                page_number = int(document.metadata["page"]) + 1
                # 「ファイルパス」と「ページ番号」
                print("ポイント3")
                file_info = f"{file_path} (ページ: {page_number})"
            else:
                # 「ファイルパス」のみ
                file_info = f"{file_path}"

            # 参照元のありかに応じて、適したアイコンを取得
            icon = utils.get_source_icon(file_path)
            # ファイル情報を表示
            st.info(file_info, icon=icon)

            # 重複チェック用に、ファイルパスをリストに順次追加
            file_path_list.append(file_path)
            # ファイル情報をリストに順次追加
            file_info_list.append(file_info)

    # 表示用の会話ログに格納するためのデータを用意
    # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
    # - 「answer」: LLMからの回答
    # - 「message」: 補足メッセージ
    # - 「file_path_list」: ファイルパスの一覧リスト
    content = {}
    content["mode"] = ct.ANSWER_MODE_2
    content["result"] = llm_response["result"]
    # 参照元のドキュメントが取得できた場合のみ
    if llm_response["result"] != ct.INQUIRY_NO_MATCH_ANSWER:
        content["message"] = message
        content["file_info_list"] = file_info_list

    return content

def placeholder_component():
    """
    プレースホルダーコンポーネント
    """
    st.write("コンポーネント読み込み中...")

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
    