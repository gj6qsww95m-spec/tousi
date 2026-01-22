# 日本株スイングトレードスクリーナー

日本株のスイングトレード（数日〜数週間）に適した銘柄を自動抽出するStreamlitアプリケーションです。

## 機能

### テクニカル指標
- **SMA (単純移動平均線)**: 5日、25日、75日
- **RSI (相対力指数)**: 14日
- **MACD**: トレンドの強さを判断

### スクリーニング条件

#### 条件A（順張り）
- SMA5 > SMA25 > SMA75（パーフェクトオーダー）
- RSI < 70

#### 条件B（押し目）
- 株価がSMA25付近（乖離率 ±2%以内）
- 上昇トレンド中（SMA25 > SMA75）

### UI機能
- 📊 スクリーニング結果の一覧表示
- 📈 Plotlyによるインタラクティブなローソク足チャート
- 📱 スマホ対応のレスポンシブデザイン
- 🎯 銘柄別の詳細情報表示

## 対象銘柄

以下のインデックスから選択してスクリーニングできます：

- **日経225**: 日経平均株価の構成銘柄（約180銘柄）
- **TOPIX Core30**: 時価総額・流動性が特に高い30銘柄
- **TOPIX 100**: TOPIX Core30 + Large70の主要100銘柄
- **全銘柄**: 日経225 + TOPIX主要銘柄を統合（約300銘柄以上）

主要セクター：
- **金融**: 三菱UFJ、三井住友、みずほ、野村HD等
- **テクノロジー・電機**: ソニー、キーエンス、日立、パナソニック等
- **自動車**: トヨタ、ホンダ、日産等
- **情報通信**: NTT、KDDI、ソフトバンクG等
- **医薬品**: 武田薬品、アステラス、第一三共等
- **化学**: 信越化学、富士フイルム、資生堂等
- **商社**: 三菱商事、伊藤忠、三井物産等
- **小売**: ファーストリテイリング、セブン&アイ、イオン等
- **エネルギー**: ENEOSホールディングス等

銘柄リストは `utils.py` で管理されており、容易に更新・拡張が可能です。

## セットアップ

### 1. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. アプリケーションの起動

```bash
streamlit run app.py
```

ブラウザが自動的に開き、アプリケーションが表示されます。

## 使い方

1. **サイドバー**で対象インデックスを選択（日経225、TOPIX Core30、TOPIX 100、全銘柄）
2. **データ期間**を選択（3ヶ月、6ヶ月、1年、2年）
3. **スクリーニング実行**ボタンをクリック
4. 条件に合致した銘柄が一覧表示されます
5. 詳細を確認したい銘柄を選択してチャートを表示

## Streamlit Community Cloudへのデプロイ

### 必要なファイル

このリポジトリには、Streamlit Community Cloudで動作するために必要なファイルがすべて含まれています：

- ✅ `app.py` - メインアプリケーション
- ✅ `utils.py` - ユーティリティ関数
- ✅ `requirements.txt` - Python依存関係
- ✅ `.streamlit/config.toml` - Streamlit設定

### デプロイ手順

#### 1. GitHubリポジトリの準備

```bash
# Gitリポジトリの初期化（まだの場合）
git init
git add .
git commit -m "Initial commit for Streamlit deployment"

# GitHubにプッシュ
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

#### 2. Streamlit Community Cloudでのデプロイ

1. **Streamlit Community Cloudにアクセス**
   - https://share.streamlit.io/ にアクセス
   - GitHubアカウントでサインイン

2. **新しいアプリをデプロイ**
   - 「New app」をクリック
   - リポジトリを選択: `YOUR_USERNAME/YOUR_REPO_NAME`
   - ブランチ: `main`
   - メインファイルパス: `app.py`
   - 「Deploy!」をクリック

3. **デプロイ完了**
   - 数分でアプリが起動します
   - 公開URLが発行されます（例: `https://your-app-name.streamlit.app`）

### その他のデプロイオプション

#### Heroku
- Pythonアプリのホスティングに対応
- https://www.heroku.com/

**手順**:
1. `Procfile` を作成:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Heroku CLIでデプロイ

#### Google Cloud Run
- コンテナベースのデプロイ
- スケーラブル
- Dockerfileが必要

## スマホ対応

このアプリはレスポンシブデザインで作成されており、スマートフォンやタブレットでも快適に利用できます。

## データソース

- **Yahoo Finance** (yfinance): 株価データ、出来高データ

## ライブラリ

- `streamlit`: Webアプリケーションフレームワーク
- `yfinance`: Yahoo Financeからの株価データ取得
- `pandas`: データ処理
- `numpy`: 数値計算（テクニカル指標の計算に使用）
- `plotly`: インタラクティブなチャート表示

## 注意事項

- データ取得にはインターネット接続が必要です
- Yahoo Finance APIの制限により、大量のリクエストを送ると一時的にブロックされる可能性があります
- 本アプリは投資助言を行うものではありません。投資判断は自己責任で行ってください

## ライセンス

MIT License