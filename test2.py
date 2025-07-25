from initialize import initialize
try:
    initialize()
    print('✅ 初期化成功')
except Exception as e:
    print(f'❌ 初期化エラー: {type(e).__name__}: {str(e)}')
    import traceback
    traceback.print_exc()