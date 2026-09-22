Park LIVE ローカル版（開発中）
・SQLiteにメニュー/グッズカタログを端末内保存
・公式公開ページから具体的な個別メニュー/個別グッズを更新
・商品詳細のog:imageを使い、グッズ/料理カードに画像表示
・英語施設名は日本語マスター＋表記揺れ吸収
・最新在庫は推測しません
起動: pip install -r requirements.txt
      uvicorn app:app --host 127.0.0.1 --port 8000
表示: http://127.0.0.1:8000
