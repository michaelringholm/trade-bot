import yfinance as yf
import pandas as pd
import numpy as np
import logging
import app_logger  # assuming you have your custom logger

# Parameters
tickers = ["AAPL", "MSFT", "TSLA"]
start = "2020-01-01"
end = "2025-01-01"

# Download OHLCV
data = yf.download(tickers, start=start, end=end, group_by="ticker", auto_adjust=True)

def compute_signals(df):
    df = df.copy()
    df["vol_ma20"] = df["Volume"].rolling(20).mean()
    df["vol_std20"] = df["Volume"].rolling(20).std()
    df["vol_zscore"] = (df["Volume"] - df["vol_ma20"]) / df["vol_std20"]
    df["disc_signal"] = (df["vol_zscore"] > 2).astype(int)
    df["fwd_5d_ret"] = df["Close"].pct_change(5).shift(-5)
    return df.dropna()

results = {}

def main():
    for ticker in tickers:
        df = compute_signals(data[ticker])
        df["trade_flag"] = np.where(df["disc_signal"] == 1, "🚩 SELL (Hype Spike)", "✅ HOLD/BUY")

        corr = df["disc_signal"].corr(df["fwd_5d_ret"])
        avg_signal_ret = df.loc[df["disc_signal"] == 1, "fwd_5d_ret"].mean()
        avg_nosignal_ret = df.loc[df["disc_signal"] == 0, "fwd_5d_ret"].mean()
        freq = df["disc_signal"].mean()

        results[ticker] = {
            "stats": {
                "Correlation": corr,
                "Avg 5d Ret (signal=1)": avg_signal_ret,
                "Avg 5d Ret (signal=0)": avg_nosignal_ret,
                "Signal Frequency": freq
            },
            "df": df
        }

        logger.info(
            f"📊 {ticker} | "
            f"🔔 Hype Detected → {df['trade_flag'].iloc[-1]} | "
            f"AvgRet[Signal=1]: {avg_signal_ret:.4f}, "
            f"AvgRet[Signal=0]: {avg_nosignal_ret:.4f} | "
            f"📈 Corr: {corr:.4f}, 📊 Freq: {freq:.2%}"
        )

def discretionary_flags(df, ticker, days=7):
    recent = df.tail(days).copy()
    for idx, row in recent.iterrows():
        signal = row["disc_signal"]
        fwd = row["fwd_5d_ret"]
        if signal == 1:
            flag = "👍" if fwd > 0 else "👎"
            note = f"HYPE spike → {flag} next"
        else:
            flag = "✅" if fwd > 0 else "❌"
            note = f"No hype → {flag} next"
        print(f"{ticker} {idx.date()} | VolZ={row['vol_zscore']:.2f} | {note}")

if __name__ == "__main__":
    # Use your custom logger if available, else fallback
    try:
        logger = app_logger.logger
    except AttributeError:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        logger = logging.getLogger("backtest")

    main()
    discretionary_flags(results["TSLA"]["df"], "TSLA", days=30)
