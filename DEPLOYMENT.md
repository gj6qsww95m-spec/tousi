# Streamlit Community Cloud デプロイチェックリスト

## ✅ 準備完了

このリポジトリは、Streamlit Community Cloudにデプロイする準備が整っています。

### 必須ファイル

- [x] `app.py` - メインアプリケーション
- [x] `utils.py` - ユーティリティ関数
- [x] `requirements.txt` - Python依存関係
- [x] `.streamlit/config.toml` - Streamlit設定
- [x] `.gitignore` - Git除外設定
- [x] `README.md` - ドキュメント

## 🚀 デプロイ手順

### ステップ1: GitHubリポジトリの作成とプッシュ

```bash
# 1. Gitリポジトリの初期化（まだの場合）
git init

# 2. すべてのファイルをステージング
git add .

# 3. 初回コミット
git commit -m "Initial commit for Streamlit Community Cloud deployment"

# 4. GitHubで新しいリポジトリを作成してから、以下を実行
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### ステップ2: Streamlit Community Cloudでデプロイ

1. **Streamlit Community Cloudにアクセス**
   - URL: https://share.streamlit.io/
   - GitHubアカウントでサインイン

2. **新しいアプリを作成**
   - 「New app」ボタンをクリック
   - 以下の情報を入力:
     - **Repository**: `YOUR_USERNAME/YOUR_REPO_NAME`
     - **Branch**: `main`
     - **Main file path**: `app.py`
   - 「Deploy!」をクリック

3. **デプロイ完了を待つ**
   - 初回デプロイには数分かかります
   - デプロイログを確認できます
   - 完了すると公開URLが発行されます

### ステップ3: アプリの確認

デプロイが完了したら、以下を確認してください:

- [ ] アプリが正常に起動する
- [ ] サイドバーでインデックスを選択できる
- [ ] スクリーニングが実行できる
- [ ] チャートが表示される
- [ ] スマホでも正常に表示される

## 🔧 トラブルシューティング

### デプロイエラーが発生した場合

1. **依存関係のエラー**
   - `requirements.txt`のバージョンを確認
   - Streamlit Community Cloudのログを確認

2. **メモリエラー**
   - スクリーニング対象の銘柄数を減らす
   - データ取得期間を短くする

3. **タイムアウトエラー**
   - Yahoo Finance APIのレート制限に引っかかっている可能性
   - 少し時間をおいてから再試行

### アプリの更新方法

```bash
# コードを修正後
git add .
git commit -m "Update: 変更内容の説明"
git push

# Streamlit Community Cloudが自動的に再デプロイします
```

## 📱 公開URL

デプロイ後、以下のような形式のURLが発行されます:

```
https://YOUR-APP-NAME.streamlit.app
```

このURLを共有することで、誰でもアプリにアクセスできます。

## 🔒 プライベートアプリにする場合

Streamlit Community Cloudの設定で、アプリへのアクセスを制限できます:

1. アプリの設定画面を開く
2. 「Sharing」タブを選択
3. アクセス権限を設定

## 💡 ヒント

- **無料プラン**: 3つまでのアプリをデプロイ可能
- **自動更新**: GitHubにプッシュすると自動的に再デプロイ
- **ログ確認**: デプロイログでエラーを確認できる
- **スリープ**: 7日間アクセスがないとスリープ状態になる

## 📞 サポート

問題が発生した場合:
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
