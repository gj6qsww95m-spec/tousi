"""
バックテストエンジン
スイングトレードシグナルの過去パフォーマンスを検証
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
import streamlit as st


class BacktestEngine:
    """
    スイングトレードシグナルのバックテストエンジン
    
    パーフェクトオーダーと押し目買いのシグナルを過去データで検出し、
    シグナル発生後のパフォーマンスを検証する
    """
    
    def __init__(
        self,
        stock_list: List[Tuple[str, str]],
        start_date: datetime,
        end_date: datetime,
        holding_periods: List[int] = [5, 10, 20],
        stop_loss: float = -0.05,
        take_profit: float = 0.10,
        use_enhanced_filters: bool = False,
        pullback_divergence: float = 2.0,
        use_trailing_stop: bool = False,
        trailing_stop_pct: float = 0.03
    ):
        """
        バックテストエンジンの初期化
        
        Args:
            stock_list: (ティッカー, 銘柄名) のリスト
            start_date: バックテスト開始日
            end_date: バックテスト終了日
            holding_periods: 保有期間のリスト（日数）
            stop_loss: 損切りライン（例: -0.05 = -5%）
            take_profit: 利確ライン（例: 0.10 = +10%）
            use_enhanced_filters: 改善フィルターを使用するか
            pullback_divergence: 押し目の乖離率閾値（デフォルト2.0%）
            use_trailing_stop: トレールストップを使用するか
            trailing_stop_pct: トレールストップの割合（例: 0.03 = 3%）
        """
        self.stock_list = stock_list
        self.start_date = start_date
        self.end_date = end_date
        self.holding_periods = holding_periods
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.use_enhanced_filters = use_enhanced_filters
        self.pullback_divergence = pullback_divergence
        self.use_trailing_stop = use_trailing_stop
        self.trailing_stop_pct = trailing_stop_pct
    
    def _fetch_stock_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        株価データを取得
        
        Args:
            ticker: ティッカーシンボル
            
        Returns:
            株価データのDataFrame、失敗時はNone
        """
        try:
            # バックテスト期間より前のデータも取得（テクニカル指標計算用）
            fetch_start = self.start_date - timedelta(days=100)
            stock = yf.Ticker(ticker)
            df = stock.history(start=fetch_start, end=self.end_date + timedelta(days=max(self.holding_periods) + 10))
            
            if df.empty or len(df) < 80:
                return None
            
            return df
        except Exception:
            return None
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル指標を計算
        
        Args:
            df: 株価データ
            
        Returns:
            テクニカル指標を追加したDataFrame
        """
        if df is None or df.empty:
            return None
        
        try:
            # SMA計算
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
            exp12 = df['Close'].ewm(span=12, adjust=False).mean()
            exp26 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp12 - exp26
            df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
            
            # ATR計算（14日間）
            high_low = df['High'] - df['Low']
            high_close = abs(df['High'] - df['Close'].shift())
            low_close = abs(df['Low'] - df['Close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['ATR'] = true_range.rolling(window=14).mean()
            df['ATR_MA20'] = df['ATR'].rolling(window=20).mean()
            
            # 出来高の20日移動平均
            df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
            
            return df
        except Exception:
            return None
    
    def _check_perfect_order(self, row: pd.Series) -> bool:
        """
        パーフェクトオーダーをチェック（標準版）
        条件: SMA5 > SMA25 > SMA75 かつ RSI < 70
        """
        try:
            if pd.isna(row['SMA5']) or pd.isna(row['SMA25']) or pd.isna(row['SMA75']) or pd.isna(row['RSI']):
                return False
            return (row['SMA5'] > row['SMA25'] > row['SMA75']) and (row['RSI'] < 70)
        except:
            return False
    
    def _check_perfect_order_enhanced(self, row: pd.Series) -> bool:
        """
        パーフェクトオーダーをチェック（改善版）
        追加条件:
        - RSI下限: 30 < RSI < 70
        - 出来高: 20日平均の1.5倍以上
        - MACD: シグナルラインより上
        """
        try:
            required_cols = ['SMA5', 'SMA25', 'SMA75', 'RSI', 'MACD', 'MACD_signal', 'Volume_Ratio']
            if any(pd.isna(row.get(col)) for col in required_cols):
                return False
            
            # 基本条件: パーフェクトオーダー
            basic = (row['SMA5'] > row['SMA25'] > row['SMA75'])
            
            # RSI: 30-70の適正範囲
            rsi_ok = (30 < row['RSI'] < 70)
            
            # 出来高: 20日平均の1.5倍以上
            volume_ok = (row['Volume_Ratio'] >= 1.5)
            
            # MACD: シグナルラインより上
            macd_ok = (row['MACD'] > row['MACD_signal'])
            
            return basic and rsi_ok and volume_ok and macd_ok
        except:
            return False
    
    def _check_pullback(self, row: pd.Series) -> bool:
        """
        押し目買いをチェック（標準版）
        条件: 株価がSMA25付近（乖離率 ±2%以内）かつ 上昇トレンド中（SMA25 > SMA75）
        """
        try:
            if pd.isna(row['Close']) or pd.isna(row['SMA25']) or pd.isna(row['SMA75']):
                return False
            
            divergence = abs((row['Close'] - row['SMA25']) / row['SMA25'] * 100)
            return (row['SMA25'] > row['SMA75']) and (divergence <= self.pullback_divergence)
        except:
            return False
    
    def _check_pullback_enhanced(self, row: pd.Series) -> bool:
        """
        押し目買いをチェック（改善版）
        追加条件:
        - 乖離率: ±1%以内（より厳格）
        - RSI: 30-60（売られすぎからの反発）
        - ATR: 20日平均以下（低ボラティリティ）
        - MACD: ヒストグラムが正
        """
        try:
            required_cols = ['Close', 'SMA25', 'SMA75', 'RSI', 'ATR', 'ATR_MA20', 'MACD_histogram']
            if any(pd.isna(row.get(col)) for col in required_cols):
                return False
            
            # 乖離率計算（±1%以内）
            divergence = abs((row['Close'] - row['SMA25']) / row['SMA25'] * 100)
            divergence_ok = (divergence <= 1.0)
            
            # 上昇トレンド中
            uptrend = (row['SMA25'] > row['SMA75'])
            
            # RSI: 30-60（売られすぎからの反発）
            rsi_ok = (30 < row['RSI'] < 60)
            
            # ATR: 20日平均以下（低ボラティリティ）
            atr_ok = (row['ATR'] <= row['ATR_MA20'])
            
            # MACD: ヒストグラムが正または上向き
            macd_ok = (row['MACD_histogram'] > 0)
            
            return divergence_ok and uptrend and rsi_ok and atr_ok and macd_ok
        except:
            return False
    
    def _calculate_trade_return(
        self, 
        df: pd.DataFrame, 
        entry_idx: int, 
        holding_period: int
    ) -> Dict:
        """
        トレードのリターンを計算（損切り/利確考慮）
        
        Args:
            df: 株価データ
            entry_idx: エントリー日のインデックス位置
            holding_period: 保有期間
            
        Returns:
            トレード結果の辞書
        """
        try:
            entry_price = df.iloc[entry_idx]['Close']
            exit_idx = min(entry_idx + holding_period, len(df) - 1)
            
            # 損切り/利確/トレールストップチェック
            actual_exit_idx = exit_idx
            exit_reason = "期間満了"
            highest_price = entry_price  # トレールストップ用：最高値追跡
            
            for i in range(entry_idx + 1, exit_idx + 1):
                if i >= len(df):
                    break
                
                # 日中高値で最高値を更新
                high_price = df.iloc[i]['High']
                highest_price = max(highest_price, high_price)
                
                current_return = (df.iloc[i]['Close'] - entry_price) / entry_price
                
                # 損切り
                if current_return <= self.stop_loss:
                    actual_exit_idx = i
                    exit_reason = "損切り"
                    break
                
                # 利確
                if current_return >= self.take_profit:
                    actual_exit_idx = i
                    exit_reason = "利確"
                    break
                
                # トレールストップ
                if self.use_trailing_stop:
                    trail_stop_price = highest_price * (1 - self.trailing_stop_pct)
                    if df.iloc[i]['Close'] <= trail_stop_price:
                        actual_exit_idx = i
                        exit_reason = "トレールストップ"
                        break
            
            exit_price = df.iloc[actual_exit_idx]['Close']
            trade_return = (exit_price - entry_price) / entry_price
            holding_days = actual_exit_idx - entry_idx
            
            return {
                'entry_price': entry_price,
                'exit_price': exit_price,
                'return': trade_return,
                'exit_reason': exit_reason,
                'holding_days': holding_days
            }
        except Exception:
            return None
    
    def run_backtest_on_data(self, df: pd.DataFrame, ticker: str, name: str) -> List[Dict]:
        """
        既存のDataFrameに対してバックテストを実行（単一銘柄用）
        
        Args:
            df: 株価データ
            ticker: ティッカー
            name: 銘柄名
            
        Returns:
            シグナルのリスト
        """
        all_signals = []
        
        # テクニカル指標計算（まだ計算されていない場合用だが、計算済みでも再計算はコスト安）
        # ただし、カラムが存在するかチェックしてスキップも可能だが、
        # ここではBacktestEngine独自の指標があるため念の為計算する
        df = self._calculate_technical_indicators(df)
        if df is None:
            return []
        
        # バックテスト期間内でシグナル検出
        if df.index.tz is not None:
            start_ts = pd.Timestamp(self.start_date).tz_localize(df.index.tz)
            end_ts = pd.Timestamp(self.end_date).tz_localize(df.index.tz)
        else:
            start_ts = pd.Timestamp(self.start_date)
            end_ts = pd.Timestamp(self.end_date)
        
        df_in_period = df[(df.index >= start_ts) & (df.index <= end_ts)]
        
        for i, (date, row) in enumerate(df_in_period.iterrows()):
            # 改善版または標準版のシグナル検出を選択
            if self.use_enhanced_filters:
                is_perfect_order = self._check_perfect_order_enhanced(row)
                is_pullback = self._check_pullback_enhanced(row)
            else:
                is_perfect_order = self._check_perfect_order(row)
                is_pullback = self._check_pullback(row)
            
            if not (is_perfect_order or is_pullback):
                continue
            
            # シグナルタイプ
            signal_types = []
            if is_perfect_order:
                signal_types.append("パーフェクトオーダー")
            if is_pullback:
                signal_types.append("押し目")
            
            # 元のDataFrameでのインデックス位置を取得
            original_idx = df.index.get_loc(date)
            
            # 各保有期間でリターン計算
            for period in self.holding_periods:
                trade_result = self._calculate_trade_return(df, original_idx, period)
                
                if trade_result is None:
                    continue
                
                all_signals.append({
                    'ティッカー': ticker,
                    '銘柄名': name,
                    'シグナル日': date,
                    'シグナルタイプ': " / ".join(signal_types),
                    'エントリー価格': round(trade_result['entry_price'], 2),
                    'イグジット価格': round(trade_result['exit_price'], 2),
                    '設定保有期間': period,
                    '実際保有日数': trade_result['holding_days'],
                    'リターン': round(trade_result['return'] * 100, 2),
                    '決済理由': trade_result['exit_reason'],
                    '勝敗': '勝ち' if trade_result['return'] > 0 else '負け'
                })
        
        return all_signals

    def run_backtest(self, progress_callback=None) -> pd.DataFrame:
        """
        全銘柄のバックテストを実行
        
        Args:
            progress_callback: 進捗コールバック関数 (current, total, ticker_name) -> None
            
        Returns:
            全シグナルの結果DataFrame
        """
        all_signals = []
        total = len(self.stock_list)
        
        for idx, (ticker, name) in enumerate(self.stock_list):
            if progress_callback:
                progress_callback(idx + 1, total, name)
            
            # データ取得
            df = self._fetch_stock_data(ticker)
            if df is None:
                continue
            
            # テクニカル指標計算
            df = self._calculate_technical_indicators(df)
            if df is None:
                continue
            
            # バックテスト期間内でシグナル検出
            # yfinanceのデータはタイムゾーン付きなので、比較用の日付も合わせる
            if df.index.tz is not None:
                start_ts = pd.Timestamp(self.start_date).tz_localize(df.index.tz)
                end_ts = pd.Timestamp(self.end_date).tz_localize(df.index.tz)
            else:
                start_ts = pd.Timestamp(self.start_date)
                end_ts = pd.Timestamp(self.end_date)
            
            df_in_period = df[(df.index >= start_ts) & (df.index <= end_ts)]
            
            for i, (date, row) in enumerate(df_in_period.iterrows()):
                # 改善版または標準版のシグナル検出を選択
                if self.use_enhanced_filters:
                    is_perfect_order = self._check_perfect_order_enhanced(row)
                    is_pullback = self._check_pullback_enhanced(row)
                else:
                    is_perfect_order = self._check_perfect_order(row)
                    is_pullback = self._check_pullback(row)
                
                if not (is_perfect_order or is_pullback):
                    continue
                
                # シグナルタイプ
                signal_types = []
                if is_perfect_order:
                    signal_types.append("パーフェクトオーダー")
                if is_pullback:
                    signal_types.append("押し目")
                
                # 元のDataFrameでのインデックス位置を取得
                original_idx = df.index.get_loc(date)
                
                # 各保有期間でリターン計算
                for period in self.holding_periods:
                    trade_result = self._calculate_trade_return(df, original_idx, period)
                    
                    if trade_result is None:
                        continue
                    
                    all_signals.append({
                        'ティッカー': ticker,
                        '銘柄名': name,
                        'シグナル日': date,
                        'シグナルタイプ': " / ".join(signal_types),
                        'エントリー価格': round(trade_result['entry_price'], 2),
                        'イグジット価格': round(trade_result['exit_price'], 2),
                        '設定保有期間': period,
                        '実際保有日数': trade_result['holding_days'],
                        'リターン': round(trade_result['return'] * 100, 2),
                        '決済理由': trade_result['exit_reason'],
                        '勝敗': '勝ち' if trade_result['return'] > 0 else '負け'
                    })
        
        return pd.DataFrame(all_signals)
    
    @staticmethod
    def calculate_performance(signals_df: pd.DataFrame) -> Dict:
        """
        パフォーマンス指標を計算
        
        Args:
            signals_df: シグナル結果のDataFrame
            
        Returns:
            パフォーマンス統計の辞書
        """
        if signals_df.empty:
            return {
                'total_signals': 0,
                'win_rate': 0,
                'avg_return': 0,
                'max_profit': 0,
                'max_loss': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'total_return': 0
            }
        
        total = len(signals_df)
        wins = signals_df[signals_df['リターン'] > 0]
        losses = signals_df[signals_df['リターン'] <= 0]
        
        win_count = len(wins)
        loss_count = len(losses)
        
        win_rate = (win_count / total * 100) if total > 0 else 0
        avg_return = signals_df['リターン'].mean()
        max_profit = signals_df['リターン'].max()
        max_loss = signals_df['リターン'].min()
        
        avg_win = wins['リターン'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['リターン'].mean()) if len(losses) > 0 else 0
        
        # プロフィットファクター
        total_profit = wins['リターン'].sum() if len(wins) > 0 else 0
        total_loss = abs(losses['リターン'].sum()) if len(losses) > 0 else 1
        profit_factor = total_profit / total_loss if total_loss > 0 else total_profit
        
        # 累積リターン
        total_return = signals_df['リターン'].sum()
        
        return {
            'total_signals': total,
            'win_count': win_count,
            'loss_count': loss_count,
            'win_rate': round(win_rate, 1),
            'avg_return': round(avg_return, 2),
            'max_profit': round(max_profit, 2),
            'max_loss': round(max_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'total_return': round(total_return, 2)
        }
    
    @staticmethod
    def calculate_performance_by_period(signals_df: pd.DataFrame) -> pd.DataFrame:
        """
        保有期間別のパフォーマンスを計算
        
        Args:
            signals_df: シグナル結果のDataFrame
            
        Returns:
            保有期間別統計のDataFrame
        """
        if signals_df.empty:
            return pd.DataFrame()
        
        results = []
        for period in signals_df['設定保有期間'].unique():
            period_df = signals_df[signals_df['設定保有期間'] == period]
            stats = BacktestEngine.calculate_performance(period_df)
            stats['保有期間'] = period
            results.append(stats)
        
        return pd.DataFrame(results)
    
    @staticmethod
    def calculate_performance_by_signal_type(signals_df: pd.DataFrame) -> pd.DataFrame:
        """
        シグナルタイプ別のパフォーマンスを計算
        
        Args:
            signals_df: シグナル結果のDataFrame
            
        Returns:
            シグナルタイプ別統計のDataFrame
        """
        if signals_df.empty:
            return pd.DataFrame()
        
        results = []
        for signal_type in signals_df['シグナルタイプ'].unique():
            type_df = signals_df[signals_df['シグナルタイプ'] == signal_type]
            stats = BacktestEngine.calculate_performance(type_df)
            stats['シグナルタイプ'] = signal_type
            results.append(stats)
        
        return pd.DataFrame(results)
