"""
株式スイングトレード推奨銘柄スクリーニングアプリ（日本株・米国株対応）
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import base64
import os
from PIL import Image
import utils

# アイコン画像（Base64）の取得
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon_180.png")
icon_base64 = get_base64_image(icon_path)

# アイコンの読み込み
page_icon = "📈"
if os.path.exists(icon_path):
    try:
        page_icon = Image.open(icon_path)
    except Exception as e:
        print(f"Icon load error: {e}")
        page_icon = "📈"

# ページ設定
st.set_page_config(
    page_title="株式スイングトレードスクリーナー",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（スマホ対応のレスポンシブデザイン）+ PWA対応
st.markdown(f"""
    <!-- PWA / iOS ホーム画面対応 -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="株スクリーナー">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#4CAF50">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    
    <!-- Apple Touch Icon (ホーム画面アイコン用) -->
    {f'<link rel="apple-touch-icon" href="data:image/png;base64,{icon_base64}">' if icon_base64 else f"<link rel='apple-touch-icon' href='data:image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\"><rect fill=\"%234CAF50\" width=\"100\" height=\"100\" rx=\"20\"/><text x=\"50\" y=\"65\" font-size=\"50\" text-anchor=\"middle\" fill=\"white\">📈</text></svg>'>"}
    
    <style>
    /* PWA スタンドアローンモード用スタイル */
    @media (display-mode: standalone) {{
        .stApp {{
            padding-top: env(safe-area-inset-top);
            padding-bottom: env(safe-area-inset-bottom);
        }}
    }}
    
    .main {{
        padding: 1rem;
    }}
    .stButton>button {{
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }}
    .stDataFrame {{
        font-size: 0.9rem;
    }}
    @media (max-width: 768px) {{
        .stDataFrame {{
            font-size: 0.7rem;
        }}
    }}
    </style>
""", unsafe_allow_html=True)


def fetch_stock_data(ticker: str, period: str = "6mo") -> tuple:
    """
    株価データとPER・PBRを取得する
    
    Args:
        ticker: ティッカーシンボル
        period: データ取得期間
    
    Returns:
        株価データのDataFrame、PER、PBRのタプル
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None, None, None
        
        # PER（株価収益率）とPBR（株価純資産倍率）を取得
        try:
            info = stock.info
            per = info.get('trailingPE', None)
            if per is not None and (per < 0 or per > 1000):
                per = None  # 異常値の場合はNone
            
            pbr = info.get('priceToBook', None)
            if pbr is not None and (pbr < 0 or pbr > 100):
                pbr = None  # 異常値の場合はNone
        except:
            per = None
            pbr = None
        
        return df, per, pbr
    except Exception as e:
        st.warning(f"{ticker} のデータ取得に失敗しました: {str(e)}")
        return None, None, None


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    テクニカル指標を計算する
    
    Args:
        df: 株価データ
    
    Returns:
        テクニカル指標を追加したDataFrame
    """
    if df is None or df.empty:
        return None
    
    try:
        # SMA計算（単純移動平均）
        df['SMA5'] = df['Close'].rolling(window=5).mean()
        df['SMA25'] = df['Close'].rolling(window=25).mean()
        df['SMA75'] = df['Close'].rolling(window=75).mean()
        
        # RSI計算
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD計算
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        return df
    except Exception as e:
        st.warning(f"テクニカル指標の計算に失敗しました: {str(e)}")
        return None


def check_perfect_order(row: pd.Series) -> bool:
    """
    パーフェクトオーダー（順張り）をチェック
    条件A: SMA5 > SMA25 > SMA75 かつ RSI < 70
    
    Args:
        row: データ行
    
    Returns:
        条件を満たすかどうか
    """
    try:
        if pd.isna(row['SMA5']) or pd.isna(row['SMA25']) or pd.isna(row['SMA75']) or pd.isna(row['RSI']):
            return False
        
        return (row['SMA5'] > row['SMA25'] > row['SMA75']) and (row['RSI'] < 70)
    except:
        return False


def check_pullback(row: pd.Series) -> bool:
    """
    押し目買いをチェック
    条件B: 株価がSMA25付近（乖離率 ±2%以内）かつ 上昇トレンド中（SMA25 > SMA75）
    
    Args:
        row: データ行
    
    Returns:
        条件を満たすかどうか
    """
    try:
        if pd.isna(row['Close']) or pd.isna(row['SMA25']) or pd.isna(row['SMA75']):
            return False
        
        # 乖離率計算
        divergence = abs((row['Close'] - row['SMA25']) / row['SMA25'] * 100)
        
        # 上昇トレンド中かつSMA25付近
        return (row['SMA25'] > row['SMA75']) and (divergence <= 2.0)
    except:
        return False


def screen_stocks(stock_list: list, progress_bar) -> pd.DataFrame:
    """
    銘柄をスクリーニングする
    
    Args:
        stock_list: 銘柄リスト
        progress_bar: プログレスバー
    
    Returns:
        スクリーニング結果のDataFrame
    """
    results = []
    total = len(stock_list)
    
    for idx, (ticker, name) in enumerate(stock_list):
        # プログレスバー更新
        progress_bar.progress((idx + 1) / total, text=f"分析中: {name} ({idx + 1}/{total})")
        
        # データ取得（PER・PBRも含む）
        df, per, pbr = fetch_stock_data(ticker)
        if df is None or df.empty:
            continue
        
        # テクニカル指標計算
        df = calculate_technical_indicators(df)
        if df is None or df.empty:
            continue
        
        # 最新データ取得
        latest = df.iloc[-1]
        
        # スクリーニング条件チェック
        is_perfect_order = check_perfect_order(latest)
        is_pullback = check_pullback(latest)
        
        if is_perfect_order or is_pullback:
            # マッチした場合、結果に追加
            signal_type = []
            if is_perfect_order:
                signal_type.append("パーフェクトオーダー")
            if is_pullback:
                signal_type.append("押し目")
            
            results.append({
                "ティッカー": ticker,
                "銘柄名": name,
                "現在値": round(latest['Close'], 2),
                "PER": round(per, 2) if per is not None else "-",
                "PBR": round(pbr, 2) if pbr is not None else "-",
                "SMA5": round(latest['SMA5'], 2) if pd.notna(latest['SMA5']) else "-",
                "SMA25": round(latest['SMA25'], 2) if pd.notna(latest['SMA25']) else "-",
                "SMA75": round(latest['SMA75'], 2) if pd.notna(latest['SMA75']) else "-",
                "RSI": round(latest['RSI'], 2) if pd.notna(latest['RSI']) else "-",
                "シグナル": " / ".join(signal_type),
                "出来高": int(latest['Volume']) if pd.notna(latest['Volume']) else 0,
            })
        
        # API制限を避けるため少し待機
        time.sleep(0.1)
    
    return pd.DataFrame(results)


def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> dict:
    """
    サポートライン（支持線）とレジスタンスライン（抵抗線）を計算する
    
    Args:
        df: 株価データ
        window: ピボットポイント検出のウィンドウサイズ
    
    Returns:
        サポート・レジスタンスレベルの辞書
    """
    if df is None or len(df) < window:
        return {'support': [], 'resistance': []}
    
    supports = []
    resistances = []
    
    # ローリングウィンドウでの最高値・最安値を計算
    df_copy = df.copy()
    df_copy['rolling_high'] = df_copy['High'].rolling(window=window, center=True).max()
    df_copy['rolling_low'] = df_copy['Low'].rolling(window=window, center=True).min()
    
    # 直近30日間のデータでピボットポイントを検出
    recent_data = df_copy.tail(60).dropna()
    
    for i in range(len(recent_data)):
        row = recent_data.iloc[i]
        # レジスタンス（高値がローリング最高値と一致）
        if row['High'] == row['rolling_high']:
            resistances.append(row['High'])
        # サポート（安値がローリング最安値と一致）
        if row['Low'] == row['rolling_low']:
            supports.append(row['Low'])
    
    # 重複を除去し、近い価格をクラスタリング
    def cluster_levels(levels, threshold=0.02):
        if not levels:
            return []
        levels = sorted(set(levels))
        clustered = [levels[0]]
        for level in levels[1:]:
            if abs(level - clustered[-1]) / clustered[-1] > threshold:
                clustered.append(level)
            else:
                # 平均値で更新
                clustered[-1] = (clustered[-1] + level) / 2
        return clustered[-3:]  # 直近3つのレベルのみ返す
    
    current_price = df['Close'].iloc[-1]
    
    # 現在価格より下のサポート、上のレジスタンスをフィルタリング
    supports = [s for s in cluster_levels(supports) if s < current_price]
    resistances = [r for r in cluster_levels(resistances) if r > current_price]
    
    return {
        'support': supports[-2:] if len(supports) > 2 else supports,  # 最大2本
        'resistance': resistances[:2] if len(resistances) > 2 else resistances  # 最大2本
    }


def plot_candlestick_chart(ticker: str, name: str, period: str = "6mo", currency_symbol: str = "¥"):
    """
    ローソク足チャートを描画
    
    Args:
        ticker: ティッカーシンボル
        name: 銘柄名
        period: データ期間
        currency_symbol: 通貨記号（¥ または $）
    """
    df, _, _ = fetch_stock_data(ticker, period)
    if df is None or df.empty:
        st.error(f"{name} ({ticker}) のデータを取得できませんでした")
        return
    
    df = calculate_technical_indicators(df)
    if df is None:
        st.error("テクニカル指標の計算に失敗しました")
        return
    
    # サブプロット作成（チャート + 出来高）
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"{name} ({ticker})", "出来高")
    )
    
    # ローソク足
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="ローソク足"
        ),
        row=1, col=1
    )
    
    # SMA
    colors = {'SMA5': 'red', 'SMA25': 'blue', 'SMA75': 'green'}
    for sma_name, color in colors.items():
        if sma_name in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[sma_name],
                    name=sma_name,
                    line=dict(color=color, width=1.5)
                ),
                row=1, col=1
            )
    
    # サポート・レジスタンスラインを計算・描画
    sr_levels = calculate_support_resistance(df)
    
    # サポートライン（緑の点線）
    for i, support in enumerate(sr_levels['support']):
        fig.add_hline(
            y=support,
            line_dash="dot",
            line_color="green",
            line_width=2,
            annotation_text=f"支持線 {i+1}: {currency_symbol}{support:.0f}",
            annotation_position="bottom right",
            row=1, col=1
        )
    
    # レジスタンスライン（赤の点線）
    for i, resistance in enumerate(sr_levels['resistance']):
        fig.add_hline(
            y=resistance,
            line_dash="dot",
            line_color="red",
            line_width=2,
            annotation_text=f"抵抗線 {i+1}: {currency_symbol}{resistance:.0f}",
            annotation_position="top right",
            row=1, col=1
        )
    
    # 出来高
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name="出来高",
            marker_color='lightblue'
        ),
        row=2, col=1
    )
    
    # レイアウト設定
    fig.update_layout(
        height=700,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig.update_xaxes(title_text="日付", row=2, col=1)
    fig.update_yaxes(title_text=f"株価 ({currency_symbol})", row=1, col=1)
    fig.update_yaxes(title_text="出来高", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # サポート・レジスタンス情報を表示
    if sr_levels['support'] or sr_levels['resistance']:
        st.markdown("#### 📊 価格抵抗線情報")
        col_s, col_r = st.columns(2)
        with col_s:
            st.markdown("**🟢 支持線（サポート）**")
            if sr_levels['support']:
                for i, s in enumerate(sr_levels['support'], 1):
                    st.write(f"支持線 {i}: {currency_symbol}{s:,.0f}")
            else:
                st.write("検出なし")
        with col_r:
            st.markdown("**🔴 抵抗線（レジスタンス）**")
            if sr_levels['resistance']:
                for i, r in enumerate(sr_levels['resistance'], 1):
                    st.write(f"抵抗線 {i}: {currency_symbol}{r:,.0f}")
            else:
                st.write("検出なし")


def main():
    """
    メイン関数
    """
    st.title("📈 株式スイングトレードスクリーナー")
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 市場選択
        st.subheader("🌏 市場選択")
        market = st.radio(
            "市場を選択",
            options=["日本株", "米国株"],
            index=0,
            horizontal=True
        )
        
        # 市場に応じた通貨記号
        currency_symbol = "¥" if market == "日本株" else "$"
        
        st.subheader("対象インデックス")
        if market == "日本株":
            index_options = ["日経225", "TOPIX Core30", "TOPIX 100", "全銘柄"]
        else:
            index_options = ["S&P 500"]
        
        selected_index = st.selectbox(
            "インデックスを選択",
            options=index_options,
            index=0,
            help="スクリーニング対象のインデックスを選択してください"
        )
        
        # 選択されたインデックスに応じて銘柄リストを取得
        STOCK_LIST = utils.get_stocks_by_index(selected_index)
        
        st.subheader("スクリーニング条件")
        st.info("""
        **条件A（順張り）:**  
        SMA5 > SMA25 > SMA75（パーフェクトオーダー）  
        かつ RSI < 70
        
        **条件B（押し目）:**  
        株価がSMA25付近（乖離率 ±2%以内）  
        かつ 上昇トレンド中
        """)
        
        st.subheader("データ期間")
        period = st.selectbox(
            "期間を選択",
            options=["3mo", "6mo", "1y", "2y"],
            index=1,
            format_func=lambda x: {
                "3mo": "3ヶ月",
                "6mo": "6ヶ月",
                "1y": "1年",
                "2y": "2年"
            }[x]
        )
        
        st.markdown("---")
        
        # スクリーニング実行ボタン
        run_screening = st.button("🔍 スクリーニング実行", type="primary")
        
        st.markdown("---")
        st.caption(f"選択インデックス: {selected_index}")
        st.caption(f"対象銘柄数: {len(STOCK_LIST)}銘柄")
        st.caption("データソース: Yahoo Finance")
    
    # session_stateの初期化
    if 'results_df' not in st.session_state:
        st.session_state.results_df = None
    if 'last_market' not in st.session_state:
        st.session_state.last_market = None
    if 'last_index' not in st.session_state:
        st.session_state.last_index = None
    
    # メインコンテンツ
    if run_screening:
        st.subheader("🔍 スクリーニング結果")
        
        # プログレスバー
        progress_bar = st.progress(0, text="スクリーニングを開始します...")
        
        # スクリーニング実行
        results_df = screen_stocks(STOCK_LIST, progress_bar)
        
        # 結果をsession_stateに保存
        st.session_state.results_df = results_df
        st.session_state.last_market = market
        st.session_state.last_index = selected_index
        
        # プログレスバークリア
        progress_bar.empty()
    
    # session_stateに結果がある場合に表示（市場/インデックスが変更されていない場合のみ）
    if st.session_state.results_df is not None:
        # 市場またはインデックスが変更された場合はリセット
        if st.session_state.last_market != market or st.session_state.last_index != selected_index:
            st.session_state.results_df = None
            st.info("👈 市場またはインデックスが変更されました。再度「スクリーニング実行」をクリックしてください。")
        else:
            results_df = st.session_state.results_df
            
            if results_df.empty:
                st.warning("条件に合致する銘柄が見つかりませんでした")
            else:
                st.subheader("🔍 スクリーニング結果")
                st.success(f"✅ {len(results_df)}銘柄が条件に合致しました")
                
                # 結果表示
                st.dataframe(
                    results_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "現在値": st.column_config.NumberColumn(
                            "現在値",
                            format=f"{currency_symbol}%.2f"
                        ),
                        "PER": st.column_config.NumberColumn(
                            "PER",
                            format="%.2f",
                            help="株価収益率（Price Earnings Ratio）"
                        ),
                        "PBR": st.column_config.NumberColumn(
                            "PBR",
                            format="%.2f",
                            help="株価純資産倍率（Price Book-value Ratio）"
                        ),
                        "出来高": st.column_config.NumberColumn(
                            "出来高",
                            format="%d"
                        )
                    }
                )
                
                # 銘柄詳細表示
                st.markdown("---")
                st.subheader("📊 銘柄詳細チャート")
                
                # 銘柄選択（keyを追加してユニークにする）
                selected_stock = st.selectbox(
                    "表示する銘柄を選択",
                    options=results_df["ティッカー"].tolist(),
                    format_func=lambda x: f"{results_df[results_df['ティッカー']==x]['銘柄名'].iloc[0]} ({x})",
                    key="stock_selector"
                )
                
                if selected_stock:
                    stock_name = results_df[results_df['ティッカー']==selected_stock]['銘柄名'].iloc[0]
                    plot_candlestick_chart(selected_stock, stock_name, period, currency_symbol)
                    
                    # 銘柄情報表示
                    stock_info = results_df[results_df['ティッカー']==selected_stock].iloc[0]
                    
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    with col1:
                        st.metric("現在値", f"{currency_symbol}{stock_info['現在値']}")
                    with col2:
                        per_display = stock_info['PER'] if stock_info['PER'] != "-" else "N/A"
                        st.metric("PER", per_display)
                    with col3:
                        pbr_display = stock_info['PBR'] if stock_info['PBR'] != "-" else "N/A"
                        st.metric("PBR", pbr_display)
                    with col4:
                        st.metric("RSI", stock_info['RSI'])
                    with col5:
                        st.metric("シグナル", stock_info['シグナル'])
                    with col6:
                        st.metric("出来高", f"{stock_info['出来高']:,}")
    elif not run_screening:
        # 初期表示
        st.info("👈 サイドバーの「スクリーニング実行」ボタンをクリックして開始してください")
        
        st.subheader("📌 使い方")
        st.markdown("""
        1. **サイドバー**でデータ期間を選択
        2. **スクリーニング実行**ボタンをクリック
        3. 条件に合致した銘柄が一覧表示されます
        4. 詳細を確認したい銘柄を選択してチャートを表示
        
        ### スクリーニング条件
        - **パーフェクトオーダー**: 短期・中期・長期の移動平均線が理想的な配置
        - **押し目**: 上昇トレンド中に一時的に価格が下がっている状態
        
        ### テクニカル指標
        - **SMA**: 単純移動平均線（5日、25日、75日）
        - **RSI**: 相対力指数（買われすぎ・売られすぎを判断）
        - **MACD**: 移動平均収束拡散法（トレンドの強さを判断）
        """)
        
        st.subheader("📋 対象銘柄一覧")
        stock_df = pd.DataFrame(STOCK_LIST, columns=["ティッカー", "銘柄名"])
        st.dataframe(stock_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
