# sentiment_core.py
import re, math, datetime as dt
import pandas as pd
from collections import defaultdict

# --- Choose sentiment engine: FinBERT -> fallback to VADER ---
def get_sentiment_fn():
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
        import torch
        model_id = "ProsusAI/finbert"
        tok = AutoTokenizer.from_pretrained(model_id)
        mdl = AutoModelForSequenceClassification.from_pretrained(model_id)
        pipe = TextClassificationPipeline(model=mdl, tokenizer=tok, framework="pt", top_k=None, device=0 if torch.cuda.is_available() else -1)
        labels = ["negative","neutral","positive"]
        def finbert_score(text: str) -> float:
            scores = pipe(text[:512])[0]  # [{label, score}, ...]
            d = {s['label'].lower(): s['score'] for s in scores}
            return d.get("positive",0)-d.get("negative",0)  # [-1..+1]
        return finbert_score
    except Exception:
        # Fallback VADER
        from nltk.sentiment import SentimentIntensityAnalyzer
        import nltk; nltk.download('vader_lexicon', quiet=True)
        sia = SentimentIntensityAnalyzer()
        def vader_score(text: str) -> float:
            return sia.polarity_scores(text)["compound"]  # [-1..+1]
        return vader_score

SCORE = get_sentiment_fn()

CASHTAG = re.compile(r'\$[A-Z]{1,5}\b')
def normalize_text(s: str) -> str:
    s = re.sub(r'https?://\S+', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def route_symbols(text: str, symbols_map: dict) -> set:
    """Map text to tickers via $TSLA/$AAPL OR company-name keywords."""
    found = set(t.strip('$') for t in CASHTAG.findall(text))
    low = text.lower()
    for tkr, kws in symbols_map.items():
        if any(k in low for k in kws):
            found.add(tkr)
    return found

def daily_sentiment_flags(rows, symbols_map, tz="UTC", pos_th=0.1, neg_th=-0.1):
    """
    rows: iterable of dicts with {'dt': datetime, 'text': str}
    symbols_map: {'AAPL': ['apple','iphone','tim cook'], ...}
    Returns: DataFrame per ticker per day with score and flag.
    """
    buckets = defaultdict(list)
    for r in rows:
        text = normalize_text(r["text"])
        if not text: continue
        syms = route_symbols(text, symbols_map)
        if not syms: continue
        s = SCORE(text)
        day = r["dt"].astimezone(dt.timezone.utc).date() if hasattr(r["dt"], "astimezone") else r["dt"].date()
        for sym in syms:
            buckets[(sym, day)].append(s)

    recs = []
    for (sym, day), vals in buckets.items():
        # robust aggregate: winsorize-ish clamp, then mean
        vals = [max(min(v, 1), -1) for v in vals]
        n = len(vals)
        mean = sum(vals)/n
        flag = "😐 Neutral"
        if mean >= pos_th: flag = "👍 Positive"
        elif mean <= neg_th: flag = "👎 Negative"
        recs.append({"ticker": sym, "date": day, "n_posts": n, "score": mean, "flag": flag})
    df = pd.DataFrame(recs).sort_values(["ticker","date"])
    return df

def print_last_days(df, ticker, days=7):
    sub = df[df["ticker"]==ticker].tail(days)
    for _, r in sub.iterrows():
        print(f"{r['ticker']} {r['date']} | {r['flag']} | score={r['score']:.2f} | posts={int(r['n_posts'])}")
