# adapters_example.py
import datetime as dt
import feedparser
import subprocess, json
from urllib.parse import quote_plus

def fetch_rss(query="Tesla", since_days=7):
    # Example: Google News RSS
    #url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)
    cutoff = dt.datetime.utcnow() - dt.timedelta(days=since_days)
    rows = []
    for e in feed.entries:
        dt_pub = getattr(e, "published_parsed", None)
        if not dt_pub: continue
        d = dt.datetime(*dt_pub[:6])
        if d < cutoff: continue
        rows.append({"dt": d, "text": f"{e.title} - {getattr(e,'summary','')}"})
    return rows

def fetch_x_snscrape(query="(TSLA OR $TSLA) lang:en", since_days=7, limit=500):
    """
    Requires: 'pip install snscrape' then call CLI
    """
    since = (dt.datetime.utcnow() - dt.timedelta(days=since_days)).date().isoformat()
    cmd = ["snscrape", "--jsonl", f"--since", since, "twitter-search", query]
    out = subprocess.run(cmd, capture_output=True, text=True, check=False)
    rows = []
    for line in out.stdout.splitlines()[:limit]:
        try:
            j = json.loads(line)
            rows.append({"dt": dt.datetime.fromisoformat(j["date"].replace("Z","+00:00")), "text": j.get("content","")})
        except Exception:
            continue
    return rows
