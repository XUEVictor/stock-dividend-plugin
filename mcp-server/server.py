#!/usr/bin/env python3
"""
台股除權息回填分析 MCP Server
提供除權息資料查詢與回填狀態判斷工具
"""

import sys
import json
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stock-dividend-mcp")


def _ticker(stock_id: str) -> str:
    """Convert Taiwan stock ID to Yahoo Finance ticker."""
    sid = stock_id.strip()
    if not sid.endswith(".TW") and not sid.endswith(".TWO"):
        sid = sid + ".TW"
    return sid


@mcp.tool()
def get_ex_dividend_info(stock_id: str, year: int) -> str:
    """
    取得指定台股在特定年份的所有除權息資訊。

    Args:
        stock_id: 股票代號，例如 "2330"（台積電）
        year: 查詢年份，例如 2024

    Returns:
        JSON 字串，包含除權息日期清單與股利金額
    """
    ticker = _ticker(stock_id)
    tk = yf.Ticker(ticker)
    dividends = tk.dividends

    if dividends.empty:
        return json.dumps({"stock_id": stock_id, "year": year, "dividends": [], "message": "查無除息資料"})

    # 過濾指定年份
    dividends.index = pd.to_datetime(dividends.index)
    # Remove timezone info for comparison
    dividends.index = dividends.index.tz_localize(None)
    yearly = dividends[dividends.index.year == year]

    results = []
    for date, amount in yearly.items():
        results.append({
            "ex_date": date.strftime("%Y-%m-%d"),
            "dividend_amount": round(float(amount), 4)
        })

    return json.dumps({
        "stock_id": stock_id,
        "ticker": ticker,
        "year": year,
        "dividends": results,
        "count": len(results)
    }, ensure_ascii=False)


@mcp.tool()
def get_stock_price_history(stock_id: str, start_date: str, end_date: str) -> str:
    """
    取得台股指定日期區間的每日股價歷史資料（OHLCV）。

    Args:
        stock_id: 股票代號，例如 "2330"
        start_date: 起始日期，格式 "YYYY-MM-DD"
        end_date: 結束日期，格式 "YYYY-MM-DD"（含）

    Returns:
        JSON 字串，包含每日開盤、收盤、最高、最低價與成交量
    """
    ticker = _ticker(stock_id)
    tk = yf.Ticker(ticker)

    # Extend end_date by 1 day since yfinance end is exclusive
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    hist = tk.history(start=start_date, end=end_dt.strftime("%Y-%m-%d"))

    if hist.empty:
        return json.dumps({"stock_id": stock_id, "data": [], "message": "查無股價資料"})

    records = []
    for date, row in hist.iterrows():
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"])
        })

    return json.dumps({
        "stock_id": stock_id,
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "data": records
    }, ensure_ascii=False)


@mcp.tool()
def check_recovery(stock_id: str, ex_date: str, pre_ex_close: float, dividend_amount: float) -> str:
    """
    判斷股票在除權息後是否回填（股價漲回除息前水位）。

    回填定義：收盤價 >= 除息前收盤價 - 股利金額（即漲回到「填息」位置）
    注意：除息日開盤價已依股利調整下調，所以目標是 pre_ex_close（原始除息前收盤）

    Args:
        stock_id: 股票代號
        ex_date: 除息日，格式 "YYYY-MM-DD"
        pre_ex_close: 除息前一交易日收盤價
        dividend_amount: 股利金額（現金股利）

    Returns:
        JSON 字串，包含：
        - recovery_status: "當天回填" | "一週內回填" | "未回填"
        - recovery_day: 回填發生的日期（若有）
        - recovery_day_index: 第幾個交易日回填（0=當天）
        - target_price: 回填目標價
        - price_on_ex_date: 除息當天收盤
        - prices: 觀測期間每日收盤價清單
    """
    # 填息目標：回到除息前的收盤價
    target_price = round(pre_ex_close, 2)

    # 取得除息日起 14 個日曆天的資料（確保涵蓋 7 個交易日）
    ex_dt = datetime.strptime(ex_date, "%Y-%m-%d")
    end_dt = ex_dt + timedelta(days=14)

    ticker = _ticker(stock_id)
    tk = yf.Ticker(ticker)
    hist = tk.history(start=ex_date, end=end_dt.strftime("%Y-%m-%d"), auto_adjust=False)

    if hist.empty:
        return json.dumps({
            "stock_id": stock_id,
            "ex_date": ex_date,
            "recovery_status": "資料不足",
            "message": "查無股價資料"
        }, ensure_ascii=False)

    # 取前 8 個交易日（除息日 + 7 個後續交易日）
    hist = hist.head(8)

    price_records = []
    recovery_status = "未回填"
    recovery_day = None
    recovery_day_index = None

    for i, (date, row) in enumerate(hist.iterrows()):
        close = round(float(row["Close"]), 2)
        price_records.append({"date": date.strftime("%Y-%m-%d"), "close": close})

        if recovery_status == "未回填" and close >= target_price:
            recovery_day = date.strftime("%Y-%m-%d")
            recovery_day_index = i
            if i == 0:
                recovery_status = "當天回填"
            else:
                recovery_status = f"一週內回填（第{i}個交易日）"

    ex_close = price_records[0]["close"] if price_records else None

    return json.dumps({
        "stock_id": stock_id,
        "ex_date": ex_date,
        "pre_ex_close": pre_ex_close,
        "dividend_amount": dividend_amount,
        "target_price": target_price,
        "price_on_ex_date": ex_close,
        "recovery_status": recovery_status,
        "recovery_day": recovery_day,
        "recovery_day_index": recovery_day_index,
        "prices": price_records
    }, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
