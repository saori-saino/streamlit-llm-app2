import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

try:
    embeddings = OpenAIEmbeddings()
    test_embedding = embeddings.embed_query('test')
    
    print('✅ Embeddings API有効')
    print(f'埋め込みベクトル次元: {len(test_embedding)}')
    
except Exception as e:
    print(f'❌ Embeddings API接続エラー: {e}')
    error_str = str(e).lower()
    if 'api key' in error_str:
        print('   → APIキーの問題です')
    elif 'quota' in error_str or 'billing' in error_str:
        print('   → 使用量制限または課金の問題です')