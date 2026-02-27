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
from backtest import BacktestEngine
from gemini_analyzer import analyze_stocks

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

# テーマ設定を session_state で初期化
if 'theme' not in st.session_state:
    st.session_state.theme = "ダーク"

def get_theme_css(theme: str) -> str:
    """
    テーマに応じた動的CSSを生成
    """
    if theme == "ダーク":
        bg_color = "#0E1117"
        secondary_bg = "#262730"
        text_color = "#FAFAFA"
        theme_color = "#0E1117"
    else:
        bg_color = "#FFFFFF"
        secondary_bg = "#F0F2F6"
        text_color = "#262730"
        theme_color = "#FFFFFF"
    
    return f"""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="株スクリーナー">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="{theme_color}">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    
    {f'<link rel="apple-touch-icon" href="data:image/png;base64,{icon_base64}">' if icon_base64 else ''}
    
    <style>
    /* ダイナミックテーマ */
    .stApp {{
        background-color: {bg_color} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {secondary_bg} !important;
    }}
    .stMarkdown, .stText, p, span, label, h1, h2, h3, h4, h5, h6 {{
        color: {text_color} !important;
    }}
    
    /* PWA スタンドアローンモード用 */
    @media (display-mode: standalone) {{
        .stApp {{
            padding-top: env(safe-area-inset-top);
            padding-bottom: env(safe-area-inset-bottom);
        }}
    }}
    
    .stButton>button {{
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
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
    """

# 動的CSSを適用
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)



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


def screen_stocks(stock_list: list, progress_bar, period: str = "6mo", calc_win_rate: bool = False) -> pd.DataFrame:
    """
    銘柄をスクリーニングする
    
    Args:
        stock_list: 銘柄リスト
        progress_bar: プログレスバー
        period: データ取得期間
        calc_win_rate: 勝率を計算するかどうか
    
    Returns:
        スクリーニング結果のDataFrame
    """
    results = []
    total = len(stock_list)
    
    # バックテストエンジン初期化用（勝率計算用）
    # 期間などはデフォルトまたは簡易設定を使用
    bt_engine = None
    if calc_win_rate:
        # 過去1年間のパフォーマンスを見るため、終了日は今日
        today = datetime.now()
        start_date = today - timedelta(days=365*2) # 余裕を持って2年前から
        bt_engine = BacktestEngine(
            stock_list=[], # ダミー
            start_date=start_date,
            end_date=today,
            holding_periods=[10], # 代表的な期間で計算
            stop_loss=-0.05,
            take_profit=0.10
        )

    for idx, (ticker, name) in enumerate(stock_list):
        # プログレスバー更新
        progress_bar.progress((idx + 1) / total, text=f"分析中: {name} ({idx + 1}/{total})")
        
        # データ取得（PER・PBRも含む）
        # 勝率計算時は期間を長めにとる必要がある場合があるが、
        # 引数のperiodが短すぎる場合は勝率計算用に別途考慮が必要かも。
        # ここではシンプルに引数のperiodを使用するが、勝率ONなら最低1yは欲しい。
        fetch_period = period
        if calc_win_rate and period in ["3mo", "6mo"]:
            fetch_period = "1y" # 勝率計算時は最低1年分取得
            
        df, per, pbr = fetch_stock_data(ticker, period=fetch_period)
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
            
            # 勝率計算
            win_rate_str = "-"
            if calc_win_rate and bt_engine:
                try:
                    signals = bt_engine.run_backtest_on_data(df, ticker, name)
                    if signals:
                        signals_df = pd.DataFrame(signals)
                        stats = BacktestEngine.calculate_performance(signals_df)
                        win_rate_str = f"{stats['win_rate']}% ({stats['win_count']}/{stats['total_signals']})"
                    else:
                        win_rate_str = "0% (0/0)"
                except Exception as e:
                    print(f"Error calculating win rate for {ticker}: {e}")
                    win_rate_str = "Error"

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
                "勝率(過去1年)": win_rate_str,
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


def plot_candlestick_chart(ticker: str, name: str, period: str = "6mo", currency_symbol: str = "¥", theme: str = "ダーク"):
    """
    ローソク足チャートを描画
    
    Args:
        ticker: ティッカーシンボル
        name: 銘柄名
        period: データ期間
        currency_symbol: 通貨記号（¥ または $）
        theme: テーマ（ダーク または ライト）
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
        template='plotly_dark' if theme == "ダーク" else 'plotly_white'
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
    
    # メインのタブ切替
    main_tab = st.radio(
        "モード選択",
        options=["🔍 スクリーニング", "📊 バックテスト"],
        horizontal=True,
        label_visibility="collapsed"
    )
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
        
        # テーマ選択
        st.subheader("🎨 テーマ")
        theme_selection = st.radio(
            "表示モード",
            options=["ダーク", "ライト"],
            index=0 if st.session_state.theme == "ダーク" else 1,
            horizontal=True,
            key="theme_radio"
        )
        if theme_selection != st.session_state.theme:
            st.session_state.theme = theme_selection
            st.rerun()
        
        # 市場に応じた通貨記号
        currency_symbol = "¥" if market == "日本株" else "$"
        
        st.subheader("対象インデックス")
        if market == "日本株":
            index_options = ["日経225", "TOPIX Core30", "TOPIX 100", "日本インデックスETF", "全銘柄"]
        else:
            index_options = ["S&P 500", "米国インデックスETF"]
        
        selected_index = st.selectbox(
            "インデックスを選択",
            options=index_options,
            index=0,
            help="スクリーニング対象のインデックスを選択してください"
        )
        
        # 選択されたインデックスに応じて銘柄リストを取得
        STOCK_LIST = utils.get_stocks_by_index(selected_index)
        
        # Gemini APIキー設定
        st.subheader("🤖 Gemini AI分析")
        gemini_api_key = st.text_input(
            "Gemini APIキー",
            type="password",
            value=os.environ.get("GEMINI_API_KEY", ""),
            help="Google AI StudioからAPIキーを取得してください。設定するとAIが上位10銘柄を選定します。"
        )
        
        # スクリーニングモード用の設定
        if main_tab == "🔍 スクリーニング":
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
            
            st.subheader("便利機能")
            show_win_rate = st.checkbox(
                "過去の勝率を表示 (計算に時間がかかります)",
                value=False,
                key="show_win_rate",
                help="過去1年のデータを用いて、同戦略での勝率を計算して表示します。"
            )
            
            st.markdown("---")
            
            # スクリーニング実行ボタン
            run_screening = st.button("🔍 スクリーニング実行", type="primary")
        
        # バックテストモード用の設定
        else:
            show_win_rate = False
            st.subheader("📅 バックテスト期間")
            bt_period = st.selectbox(
                "期間を選択",
                options=["1y", "2y", "3y", "max"],
                index=1,
                format_func=lambda x: {
                    "1y": "1年",
                    "2y": "2年",
                    "3y": "3年",
                    "max": "全期間（最大）"
                }[x],
                key="bt_period"
            )
            
            st.subheader("📦 保有期間")
            holding_periods = st.multiselect(
                "保有日数を選択",
                options=[5, 10, 20, 40],
                default=[5, 10, 20],
                key="holding_periods"
            )
            
            st.subheader("🎯 損切り/利確")
            stop_loss = st.slider(
                "損切りライン (%)",
                min_value=-20,
                max_value=-1,
                value=-5,
                key="stop_loss"
            )
            take_profit = st.slider(
                "利確ライン (%)",
                min_value=1,
                max_value=30,
                value=10,
                key="take_profit"
            )
            
            st.subheader("🚀 改善フィルター")
            use_enhanced = st.checkbox(
                "改善フィルターを使用",
                value=False,
                key="use_enhanced",
                help="出来高、RSI範囲、MACD、ATRの追加条件を適用"
            )
            
            if use_enhanced:
                st.info("""
                **改善版の追加条件:**
                - RSI: 30-70（過熱感を回避）
                - 出来高: 20日平均の1.5倍以上
                - MACD: シグナル線より上
                - ATR: 低ボラティリティ時のみ
                - 押し目: 乖離率±1%に厳格化
                """)
            
            pullback_div = st.slider(
                "押し目の乖離率 (%)",
                min_value=0.5,
                max_value=3.0,
                value=1.0 if use_enhanced else 2.0,
                step=0.5,
                key="pullback_div",
                help="SMA25からの乖離率の上限"
            )
            
            st.subheader("📍 トレールストップ")
            use_trailing_stop = st.checkbox(
                "トレールストップを使用",
                value=False,
                key="use_trailing_stop",
                help="株価上昇に合わせてストップラインを自動で引き上げます"
            )
            
            trailing_stop_pct = 3.0
            if use_trailing_stop:
                trailing_stop_pct = st.slider(
                    "トレール幅 (%)",
                    min_value=1.0,
                    max_value=10.0,
                    value=3.0,
                    step=0.5,
                    key="trailing_stop_pct",
                    help="最高値からの下落率でトレールストップを発動"
                )
                st.info("最高値から指定割合下落したら自動決済します")
            
            st.markdown("---")
            
            # バックテスト実行ボタン
            run_backtest = st.button("📊 バックテスト実行", type="primary")
            
            # 変数の初期化（スクリーニングモード用）
            period = "6mo"
            run_screening = False
        
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
    if 'backtest_results' not in st.session_state:
        st.session_state.backtest_results = None
    if 'ai_comment' not in st.session_state:
        st.session_state.ai_comment = ""
    
    # ==========================================
    # スクリーニングモード
    # ==========================================
    if main_tab == "🔍 スクリーニング":
        if run_screening:
            st.subheader("🔍 スクリーニング結果")
            
            # プログレスバー
            progress_bar = st.progress(0, text="スクリーニングを開始します...")
            
            # スクリーニング実行
            results_df = screen_stocks(STOCK_LIST, progress_bar, period=period, calc_win_rate=show_win_rate)
            
            # ==== バックテスト自動実行 ====
            if not results_df.empty:
                progress_bar.progress(0, text="バックテストを実行中...")
                today = datetime.now()
                bt_start = today - timedelta(days=365)
                bt_engine = BacktestEngine(
                    stock_list=[],
                    start_date=bt_start,
                    end_date=today,
                    holding_periods=[10],
                    stop_loss=-0.05,
                    take_profit=0.10
                )
                
                bt_results = []
                total_bt = len(results_df)
                for i, (idx, row) in enumerate(results_df.iterrows()):
                    ticker = row["ティッカー"]
                    name = row["銘柄名"]
                    progress_bar.progress(
                        (i + 1) / total_bt,
                        text=f"バックテスト中: {name} ({i + 1}/{total_bt})"
                    )
                    try:
                        df_bt = bt_engine._fetch_stock_data(ticker)
                        if df_bt is not None and not df_bt.empty:
                            signals = bt_engine.run_backtest_on_data(df_bt, ticker, name)
                            if signals:
                                signals_df_bt = pd.DataFrame(signals)
                                stats = BacktestEngine.calculate_performance(signals_df_bt)
                                bt_results.append({
                                    "ティッカー": ticker,
                                    "勝率(%)": stats["win_rate"],
                                    "平均リターン(%)": stats["avg_return"],
                                    "PF": stats["profit_factor"],
                                    "シグナル数": stats["total_signals"],
                                    "最大利益(%)": stats["max_profit"],
                                    "最大損失(%)": stats["max_loss"],
                                })
                            else:
                                bt_results.append({
                                    "ティッカー": ticker,
                                    "勝率(%)": 0, "平均リターン(%)": 0,
                                    "PF": 0, "シグナル数": 0,
                                    "最大利益(%)": 0, "最大損失(%)": 0,
                                })
                        else:
                            bt_results.append({
                                "ティッカー": ticker,
                                "勝率(%)": "-", "平均リターン(%)": "-",
                                "PF": "-", "シグナル数": "-",
                                "最大利益(%)": "-", "最大損失(%)": "-",
                            })
                    except Exception as e:
                        print(f"Backtest error for {ticker}: {e}")
                        bt_results.append({
                            "ティッカー": ticker,
                            "勝率(%)": "-", "平均リターン(%)": "-",
                            "PF": "-", "シグナル数": "-",
                            "最大利益(%)": "-", "最大損失(%)": "-",
                        })
                    time.sleep(0.05)
                
                # バックテスト結果をメインの結果DFに結合
                if bt_results:
                    bt_df = pd.DataFrame(bt_results)
                    results_df = results_df.merge(bt_df, on="ティッカー", how="left")
            
            # ==== Gemini AI分析 ====
            ai_comment = ""
            if not results_df.empty and gemini_api_key:
                progress_bar.progress(0, text="🤖 Gemini AIが分析中...")
                try:
                    results_df, ai_comment = analyze_stocks(
                        results_df, gemini_api_key, market=market, top_n=10
                    )
                except Exception as e:
                    st.warning(f"Gemini AI分析でエラーが発生しました: {str(e)}")
                    ai_comment = f"AI分析エラー: {str(e)}"
                    results_df = results_df.head(10)
            elif not results_df.empty:
                # APIキー未設定時は上位10件に制限（出来高順）
                results_df = results_df.head(10)
            
            # 結果をsession_stateに保存
            st.session_state.results_df = results_df
            st.session_state.last_market = market
            st.session_state.last_index = selected_index
            st.session_state.ai_comment = ai_comment
            
            # プログレスバークリア
            progress_bar.empty()
        
        # session_stateに結果がある場合に表示
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
                    # AI分析コメントがあれば表示
                    ai_comment = st.session_state.get('ai_comment', '')
                    if ai_comment:
                        st.info(f"🤖 **Gemini AI分析**: {ai_comment}")
                    
                    if "AI推奨順位" in results_df.columns:
                        st.subheader("🏆 AI推奨 上位10銘柄")
                        st.success(f"✅ Gemini AIが{len(results_df)}銘柄を選定しました（バックテスト結果に基づく分析）")
                    else:
                        st.subheader("🔍 スクリーニング結果（上位10件）")
                        st.success(f"✅ {len(results_df)}銘柄を表示中")
                    
                    # 結果表示
                    # カラム設定
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
                    
                    if "勝率(過去1年)" in results_df.columns:
                         column_config["勝率(過去1年)"] = st.column_config.TextColumn(
                            "勝率(過去1年)",
                            help="過去1年間の同戦略（順張り/押し目）での勝率 (勝ち数/全シグナル数)"
                        )
                    
                    if "AI分析コメント" in results_df.columns:
                        column_config["AI分析コメント"] = st.column_config.TextColumn(
                            "AI分析コメント",
                            help="Gemini AIによる推奨理由",
                            width="large"
                        )
                    
                    if "AI推奨順位" in results_df.columns:
                        column_config["AI推奨順位"] = st.column_config.NumberColumn(
                            "AI推奨順位",
                            format="%d"
                        )

                    st.dataframe(
                        results_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config=column_config
                    )
                    
                    # 銘柄詳細表示
                    st.markdown("---")
                    st.subheader("📊 銘柄詳細チャート")
                    
                    selected_stock = st.selectbox(
                        "表示する銘柄を選択",
                        options=results_df["ティッカー"].tolist(),
                        format_func=lambda x: f"{results_df[results_df['ティッカー']==x]['銘柄名'].iloc[0]} ({x})",
                        key="stock_selector"
                    )
                    
                    if selected_stock:
                        stock_name = results_df[results_df['ティッカー']==selected_stock]['銘柄名'].iloc[0]
                        plot_candlestick_chart(selected_stock, stock_name, period, currency_symbol, st.session_state.theme)
                        
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
                        
                        # AI分析コメント表示
                        if "AI分析コメント" in results_df.columns:
                            ai_comment_stock = stock_info.get('AI分析コメント', '')
                            if ai_comment_stock:
                                st.info(f"🤖 **AI分析**: {ai_comment_stock}")
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
    
    # ==========================================
    # バックテストモード
    # ==========================================
    else:
        if run_backtest:
            st.subheader("📊 バックテスト実行中...")
            
            # 期間設定
            end_date = datetime.now()
            if bt_period == "1y":
                start_date = end_date - timedelta(days=365)
            elif bt_period == "2y":
                start_date = end_date - timedelta(days=730)
            elif bt_period == "3y":
                start_date = end_date - timedelta(days=1095)
            else:  # max
                start_date = end_date - timedelta(days=3650)  # 約10年
            
            # プログレスバー
            progress_bar = st.progress(0, text="バックテストを開始します...")
            status_text = st.empty()
            
            def progress_callback(current, total, name):
                progress_bar.progress(current / total, text=f"分析中: {name} ({current}/{total})")
            
            # バックテストエンジン初期化・実行
            engine = BacktestEngine(
                stock_list=STOCK_LIST,
                start_date=start_date,
                end_date=end_date,
                holding_periods=holding_periods if holding_periods else [5, 10, 20],
                stop_loss=stop_loss / 100,
                take_profit=take_profit / 100,
                use_enhanced_filters=use_enhanced,
                pullback_divergence=pullback_div,
                use_trailing_stop=use_trailing_stop,
                trailing_stop_pct=trailing_stop_pct / 100
            )
            
            signals_df = engine.run_backtest(progress_callback=progress_callback)
            
            # 結果を保存
            st.session_state.backtest_results = {
                'signals_df': signals_df,
                'start_date': start_date,
                'end_date': end_date,
                'market': market,
                'index': selected_index,
                'holding_periods': holding_periods,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'use_enhanced': use_enhanced,
                'pullback_div': pullback_div,
                'use_trailing_stop': use_trailing_stop,
                'trailing_stop_pct': trailing_stop_pct
            }
            
            # プログレスバークリア
            progress_bar.empty()
            status_text.empty()
        
        # バックテスト結果表示
        if st.session_state.backtest_results is not None:
            bt_data = st.session_state.backtest_results
            signals_df = bt_data['signals_df']
            
            if signals_df.empty:
                st.warning("シグナルが検出されませんでした。期間や条件を変更してお試しください。")
            else:
                # サマリー統計
                st.subheader("📈 バックテスト結果サマリー")
                
                stats = BacktestEngine.calculate_performance(signals_df)
                
                # メトリクス表示
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("総シグナル数", f"{stats['total_signals']}件")
                with col2:
                    st.metric("勝率", f"{stats['win_rate']}%")
                with col3:
                    st.metric("平均リターン", f"{stats['avg_return']}%")
                with col4:
                    st.metric("最大利益", f"+{stats['max_profit']}%")
                with col5:
                    st.metric("最大損失", f"{stats['max_loss']}%")
                
                col6, col7, col8, col9, col10 = st.columns(5)
                with col6:
                    st.metric("勝ちトレード", stats['win_count'])
                with col7:
                    st.metric("負けトレード", stats['loss_count'])
                with col8:
                    st.metric("平均勝ち", f"+{stats['avg_win']}%")
                with col9:
                    st.metric("平均負け", f"-{stats['avg_loss']}%")
                with col10:
                    st.metric("プロフィットファクター", stats['profit_factor'])
                
                st.markdown("---")
                
                # 保有期間別統計
                st.subheader("📊 保有期間別パフォーマンス")
                period_stats = BacktestEngine.calculate_performance_by_period(signals_df)
                if not period_stats.empty:
                    display_cols = ['保有期間', 'total_signals', 'win_rate', 'avg_return', 'max_profit', 'max_loss', 'profit_factor']
                    display_df = period_stats[display_cols].copy()
                    display_df.columns = ['保有期間（日）', 'シグナル数', '勝率(%)', '平均リターン(%)', '最大利益(%)', '最大損失(%)', 'PF']
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # シグナルタイプ別統計
                st.subheader("📋 シグナルタイプ別パフォーマンス")
                type_stats = BacktestEngine.calculate_performance_by_signal_type(signals_df)
                if not type_stats.empty:
                    display_cols = ['シグナルタイプ', 'total_signals', 'win_rate', 'avg_return', 'profit_factor']
                    display_df = type_stats[display_cols].copy()
                    display_df.columns = ['シグナルタイプ', 'シグナル数', '勝率(%)', '平均リターン(%)', 'PF']
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # 全シグナル一覧
                st.subheader("📝 シグナル一覧")
                
                # フィルター
                filter_cols = st.columns(3)
                with filter_cols[0]:
                    filter_period = st.selectbox(
                        "保有期間でフィルター",
                        options=["全て"] + sorted(signals_df['設定保有期間'].unique().tolist()),
                        key="filter_period"
                    )
                with filter_cols[1]:
                    filter_result = st.selectbox(
                        "結果でフィルター",
                        options=["全て", "勝ち", "負け"],
                        key="filter_result"
                    )
                with filter_cols[2]:
                    filter_signal = st.selectbox(
                        "シグナルでフィルター",
                        options=["全て"] + sorted(signals_df['シグナルタイプ'].unique().tolist()),
                        key="filter_signal"
                    )
                
                # フィルター適用
                filtered_df = signals_df.copy()
                if filter_period != "全て":
                    filtered_df = filtered_df[filtered_df['設定保有期間'] == filter_period]
                if filter_result != "全て":
                    filtered_df = filtered_df[filtered_df['勝敗'] == filter_result]
                if filter_signal != "全て":
                    filtered_df = filtered_df[filtered_df['シグナルタイプ'] == filter_signal]
                
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "シグナル日": st.column_config.DateColumn("シグナル日", format="YYYY-MM-DD"),
                        "エントリー価格": st.column_config.NumberColumn("エントリー", format=f"{currency_symbol}%.2f"),
                        "イグジット価格": st.column_config.NumberColumn("イグジット", format=f"{currency_symbol}%.2f"),
                        "リターン": st.column_config.NumberColumn("リターン(%)", format="%.2f%%"),
                    }
                )
                
                st.caption(f"表示: {len(filtered_df)} / {len(signals_df)} 件")
        
        else:
            # 初期表示
            st.info("👈 サイドバーでバックテスト設定を行い、「バックテスト実行」ボタンをクリックしてください")
            
            st.subheader("📌 バックテストについて")
            st.markdown("""
            バックテストでは、過去のデータでスクリーニング条件を満たしたシグナルの
            パフォーマンスを検証します。
            
            ### 設定項目
            - **バックテスト期間**: 検証する過去の期間
            - **保有期間**: シグナル発生後の保有日数
            - **損切り/利確**: 早期決済の閾値
            - **トレールストップ**: 最高値からの下落率で自動決済（利益を確保しながらトレンドに追従）
            
            ### 評価指標
            - **勝率**: 利益が出たトレードの割合
            - **平均リターン**: 全トレードの平均収益率
            - **プロフィットファクター**: 総利益 ÷ 総損失
            
            ⚠️ **注意**: 過去のパフォーマンスは将来の結果を保証するものではありません。
            """)


if __name__ == "__main__":
    main()

