# test_page_numbers.py - ページ番号テスト用スクリプト
import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader

def test_page_numbers():
    """
    各ローダーのページ番号対応状況をテスト
    """
    # テスト用ファイルパス（実際のファイルパスに変更）
    test_files = [
        "data/sample.pdf",
        "data/sample.docx"
    ]
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"ファイルが存在しません: {file_path}")
            continue
            
        print(f"\n=== {file_path} のテスト ===")
        
        try:
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith('.docx'):
                loader = UnstructuredWordDocumentLoader(file_path)
            else:
                print("サポートされていないファイル形式")
                continue
                
            docs = loader.load()
            
            for i, doc in enumerate(docs):
                print(f"文書 {i+1}:")
                print(f"  メタデータ: {doc.metadata}")
                print(f"  ページ情報の有無: {'page' in doc.metadata}")
                if len(doc.page_content) > 100:
                    print(f"  内容: {doc.page_content[:100]}...")
                else:
                    print(f"  内容: {doc.page_content}")
                
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    test_page_numbers()