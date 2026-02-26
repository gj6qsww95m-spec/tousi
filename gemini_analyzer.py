"""
Gemini API による銘柄分析モジュール
スクリーニング結果 + バックテスト結果をGeminiに送信し、上位銘柄を選定する
"""

import json
import os
import pandas as pd
from google import genai
from google.genai import types


def analyze_stocks(results_df: pd.DataFrame, api_key: str, market: str = "日本株", top_n: int = 10) -> tuple:
    """
    スクリーニング結果をGemini APIで分析し、推奨上位N銘柄を選定する
    
    Args:
        results_df: スクリーニング結果（バックテスト結果列含む）のDataFrame
        api_key: Gemini APIキー
        market: 市場種別（"日本株" or "米国株"）
        top_n: 上位何件を返すか
    
    Returns:
        (分析済みDataFrame, AI総合コメント) のタプル
        分析済みDataFrameには「AI推奨順位」「AI分析コメント」列が追加される
    """
    if results_df.empty:
        return results_df, "分析対象の銘柄がありません。"
    
    # Gemini クライアント初期化
    client = genai.Client(api_key=api_key)
    
    # 銘柄データをテキストに変換
    stock_data_text = _format_stock_data(results_df)
    
    # プロンプト作成
    prompt = _build_analysis_prompt(stock_data_text, market, top_n, len(results_df))
    
    try:
        # Gemini APIに送信
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,  # 分析の一貫性を重視
                response_mime_type="application/json",
            )
        )
        
        # レスポンスをパース
        result = json.loads(response.text)
        
        # DataFrameに分析結果を追加
        analyzed_df = _apply_analysis_results(results_df, result, top_n)
        overall_comment = result.get("overall_comment", "")
        
        return analyzed_df, overall_comment
        
    except json.JSONDecodeError as e:
        print(f"Gemini応答のJSON解析エラー: {e}")
        # フォールバック: 元のデータをそのまま返す（上位N件に制限）
        fallback_df = results_df.head(top_n).copy()
        fallback_df["AI推奨順位"] = range(1, len(fallback_df) + 1)
        fallback_df["AI分析コメント"] = "（JSON解析エラーのため分析コメントなし）"
        return fallback_df, "AI分析のレスポンス解析に失敗しました。"
    except Exception as e:
        print(f"Gemini API エラー: {e}")
        fallback_df = results_df.head(top_n).copy()
        fallback_df["AI推奨順位"] = range(1, len(fallback_df) + 1)
        fallback_df["AI分析コメント"] = "（APIエラーのため分析コメントなし）"
        return fallback_df, f"Gemini APIエラー: {str(e)}"


def _format_stock_data(df: pd.DataFrame) -> str:
    """
    DataFrameを分析用テキストに変換する
    """
    lines = []
    for idx, row in df.iterrows():
        line_parts = [
            f"ティッカー: {row['ティッカー']}",
            f"銘柄名: {row['銘柄名']}",
            f"現在値: {row['現在値']}",
            f"PER: {row['PER']}",
            f"PBR: {row['PBR']}",
            f"RSI: {row['RSI']}",
            f"シグナル: {row['シグナル']}",
            f"出来高: {row['出来高']}",
        ]
        
        # バックテスト結果が含まれている場合
        if "勝率(%)" in df.columns:
            line_parts.append(f"勝率: {row.get('勝率(%)', '-')}%")
        if "平均リターン(%)" in df.columns:
            line_parts.append(f"平均リターン: {row.get('平均リターン(%)', '-')}%")
        if "PF" in df.columns:
            line_parts.append(f"プロフィットファクター: {row.get('PF', '-')}")
        if "シグナル数" in df.columns:
            line_parts.append(f"シグナル数: {row.get('シグナル数', '-')}")
        if "最大利益(%)" in df.columns:
            line_parts.append(f"最大利益: {row.get('最大利益(%)', '-')}%")
        if "最大損失(%)" in df.columns:
            line_parts.append(f"最大損失: {row.get('最大損失(%)', '-')}%")
        
        lines.append(" | ".join(line_parts))
    
    return "\n".join(lines)


def _build_analysis_prompt(stock_data: str, market: str, top_n: int, total_count: int) -> str:
    """
    Gemini APIに送信するプロンプトを構築する
    """
    return f"""あなたは株式投資の専門アナリストです。以下のスクリーニング結果とバックテスト結果を分析し、
スイングトレード（数日〜数週間の短期取引）に最も適した上位{top_n}銘柄を選定してください。

## 市場
{market}

## 分析対象銘柄（全{total_count}銘柄）
{stock_data}

## 評価基準
以下の基準で総合的に評価してください：
1. **テクニカル指標の強さ**: RSIが適度な範囲（30-65が理想）、パーフェクトオーダーは強いシグナル
2. **バリュエーション**: PER/PBRが業界平均と比較して割安か
3. **バックテスト実績**: 過去の勝率が高い銘柄を優先（勝率50%以上が望ましい）
4. **リスク/リターン比**: プロフィットファクターが高く、最大損失が限定的
5. **出来高**: 流動性が十分にある銘柄を優先
6. **シグナルの質**: パーフェクトオーダーは押し目より信頼性が高い場合が多い

## 出力形式（JSON）
以下のJSON形式で回答してください。必ずこの形式を守ってください。

{{
  "rankings": [
    {{
      "rank": 1,
      "ticker": "ティッカーシンボル",
      "comment": "この銘柄を推奨する理由（50文字以内）"
    }},
    ...最大{top_n}件
  ],
  "overall_comment": "全体の市場分析コメント（100文字以内）"
}}

重要: rankingsには必ず上位{top_n}件（または全銘柄数が{top_n}未満の場合はその全数）を含めてください。
tickerは入力データのティッカーと完全に一致させてください。"""


def _apply_analysis_results(original_df: pd.DataFrame, analysis_result: dict, top_n: int) -> pd.DataFrame:
    """
    Gemini分析結果をDataFrameに適用する
    """
    rankings = analysis_result.get("rankings", [])
    
    if not rankings:
        # ランキングが空の場合はフォールバック
        result_df = original_df.head(top_n).copy()
        result_df["AI推奨順位"] = range(1, len(result_df) + 1)
        result_df["AI分析コメント"] = "（分析結果なし）"
        return result_df
    
    # ランキング辞書を作成
    rank_dict = {}
    comment_dict = {}
    for item in rankings:
        ticker = item.get("ticker", "")
        rank = item.get("rank", 999)
        comment = item.get("comment", "")
        rank_dict[ticker] = rank
        comment_dict[ticker] = comment
    
    # ランキングに含まれる銘柄だけをフィルタ
    ranked_tickers = [item["ticker"] for item in rankings if item.get("ticker") in original_df["ティッカー"].values]
    
    if ranked_tickers:
        # ランキング順に並べたDataFrameを作成
        result_rows = []
        for ticker in ranked_tickers[:top_n]:
            row = original_df[original_df["ティッカー"] == ticker]
            if not row.empty:
                result_rows.append(row.iloc[0])
        
        if result_rows:
            result_df = pd.DataFrame(result_rows)
            result_df["AI推奨順位"] = [rank_dict.get(t, 999) for t in result_df["ティッカー"]]
            result_df["AI分析コメント"] = [comment_dict.get(t, "") for t in result_df["ティッカー"]]
            result_df = result_df.sort_values("AI推奨順位").reset_index(drop=True)
            return result_df
    
    # フォールバック
    result_df = original_df.head(top_n).copy()
    result_df["AI推奨順位"] = range(1, len(result_df) + 1)
    result_df["AI分析コメント"] = "（マッチングできませんでした）"
    return result_df
