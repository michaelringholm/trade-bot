# run_sentiment.py
from sentiment_core import daily_sentiment_flags, print_last_days
from adapters_example import fetch_rss, fetch_x_snscrape

def main():
    check_cuda()
    days = 30
    symbols_map = {
        "AAPL": ["apple", "iphone", "ipad", "macbook", "tim cook", "$aapl"],
        "MSFT": ["microsoft", "windows", "azure", "xbox", "satya", "$msft"],
        "TSLA": ["tesla", "elon", "musk", "model 3", "gigafactory", "$tsla"],
    }

    rows = []
    rows += fetch_rss("Apple OR $AAPL", since_days=days)
    rows += fetch_rss("Microsoft OR $MSFT", since_days=days)
    rows += fetch_rss("Tesla OR $TSLA", since_days=days)

    # Optional X (no API keys; via snscrape)
    rows += fetch_x_snscrape("(Apple OR $AAPL) lang:en", since_days=days, limit=300)
    rows += fetch_x_snscrape("(Microsoft OR $MSFT) lang:en", since_days=days, limit=300)
    rows += fetch_x_snscrape("(Tesla OR $TSLA) lang:en", since_days=days, limit=300)

    df = daily_sentiment_flags(rows, symbols_map)

    print_last_days(df, "TSLA", days=days)
    #print_last_days(df, "AAPL", days=7)
    #print_last_days(df, "MSFT", days=7)

def check_cuda():
    import torch
    cuda_ok = torch.cuda.is_available()
    if(cuda_ok):
        print(f"CUDA OK") # should be True
        print(torch.version.cuda)             # should show "12.1"
        print(torch.cuda.get_device_name(0)) 
    else:
        print(f"CUDA NOT available")
        #exit(1)

if __name__ == "__main__":
    main()