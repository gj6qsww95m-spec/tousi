"""
日本株スイングトレード推奨銘柄スクリーニングアプリ
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# ページ設定
st.set_page_config(
    page_title="日本株スイングトレードスクリーナー",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（スマホ対応のレスポンシブデザイン）
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
    @media (max-width: 768px) {
        .stDataFrame {
            font-size: 0.7rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# デモ用主要銘柄リスト（20銘柄）
STOCK_LIST = [
    ("7203.T", "トヨタ自動車"),
    ("6758.T", "ソニーグループ"),
    ("8306.T", "三菱UFJフィナンシャル・グループ"),
    ("9984.T", "ソフトバンクグループ"),
    ("9983.T", "ファーストリテイリング"),
    ("6861.T", "キーエンス"),
    ("6098.T", "リクルートホールディングス"),
    ("8035.T", "東京エレクトロン"),
    ("9432.T", "日本電信電話"),
    ("4063.T", "信越化学工業"),
    ("6501.T", "日立製作所"),
    ("7974.T", "任天堂"),
    ("8001.T", "伊藤忠商事"),
    ("4502.T", "武田薬品工業"),
    ("6902.T", "デンソー"),
    ("9613.T", "エヌ・ティ・ティ・データ"),
    ("8316.T", "三井住友フィナンシャルグループ"),
    ("2914.T", "JT（日本たばこ産業）"),
    ("4543.T", "テルモ"),
    ("4568.T", "第一三共"),
]


def fetch_stock_data(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """
    株価データを取得する
    
    Args:
        ticker: ティッカーシンボル
        period: データ取得期間
    
    Returns:
        株価データのDataFrame
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None
        
        return df
    except Exception as e:
        st.warning(f"{ticker} のデータ取得に失敗しました: {str(e)}")
        return None


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
        
        # データ取得
        df = fetch_stock_data(ticker)
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


def plot_candlestick_chart(ticker: str, name: str, period: str = "6mo"):
    """
    ローソク足チャートを描画
    
    Args:
        ticker: ティッカーシンボル
        name: 銘柄名
        period: データ期間
    """
    df = fetch_stock_data(ticker, period)
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
    fig.update_yaxes(title_text="株価 (¥)", row=1, col=1)
    fig.update_yaxes(title_text="出来高", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)


def main():
    """
    メイン関数
    """
    st.title("📈 日本株スイングトレードスクリーナー")
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")
        
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
        st.caption(f"対象銘柄数: {len(STOCK_LIST)}銘柄")
        st.caption("データソース: Yahoo Finance")
    
    # メインコンテンツ
    if run_screening:
        st.subheader("🔍 スクリーニング結果")
        
        # プログレスバー
        progress_bar = st.progress(0, text="スクリーニングを開始します...")
        
        # スクリーニング実行
        results_df = screen_stocks(STOCK_LIST, progress_bar)
        
        # プログレスバークリア
        progress_bar.empty()
        
        if results_df.empty:
            st.warning("条件に合致する銘柄が見つかりませんでした")
        else:
            st.success(f"✅ {len(results_df)}銘柄が条件に合致しました")
            
            # 結果表示
            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "現在値": st.column_config.NumberColumn(
                        "現在値",
                        format="¥%.2f"
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
            
            # 銘柄選択
            selected_stock = st.selectbox(
                "表示する銘柄を選択",
                options=results_df["ティッカー"].tolist(),
                format_func=lambda x: f"{results_df[results_df['ティッカー']==x]['銘柄名'].iloc[0]} ({x})"
            )
            
            if selected_stock:
                stock_name = results_df[results_df['ティッカー']==selected_stock]['銘柄名'].iloc[0]
                plot_candlestick_chart(selected_stock, stock_name, period)
                
                # 銘柄情報表示
                stock_info = results_df[results_df['ティッカー']==selected_stock].iloc[0]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("現在値", f"¥{stock_info['現在値']}")
                with col2:
                    st.metric("RSI", stock_info['RSI'])
                with col3:
                    st.metric("シグナル", stock_info['シグナル'])
                with col4:
                    st.metric("出来高", f"{stock_info['出来高']:,}")
    else:
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
