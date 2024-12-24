
import pandas as pd
from pyfin_sentiment.model import SentimentModel
import tweepy
import imghdr

# only run at first time
# SentimentModel.download("small")

# Twitter API credentials
API_KEY = "OXgTS468Y88OEZyDZOf2B9yUH"
API_SECRET = "7jYhu3Bd4Z1Yz7LBZS4L42rqLswGSy2qpt5XvpqdTwt0ZsyIqg"
ACCESS_TOKEN = "1867450592869994496-8Z9czWhmk6irt0Exk3cCHavXyBTIA1"
ACCESS_SECRET = "jnKs2b31nx4R6z4ykjegpn6FVMEc4oLEfN1zUyy5OQuy6"

def authenticate_twitter():
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

def fetch_tweets(api, ticker, count=1):
    try:
        tweets = tweepy.Cursor(api.search_tweets, q=ticker, lang="en", tweet_mode="extended").items(count)
        return [tweet.full_text for tweet in tweets]
    except Exception as e:
        print(f"Error fetching tweets: {e}")
    return []

def analyze_sentiment(tweets):

    sentiment_data = []
    model = SentimentModel("small")

    for tweet in tweets:
        score = model.predict([tweet])[0]
        if score == 1:
            sentiment = "Bullish"
        elif score == 3:
            sentiment = "Bearish"
        else:
            sentiment = "Uncertain"

        sentiment_data.append({"Tweet": tweet, "Sentiment": sentiment})

    return pd.DataFrame(sentiment_data)

def analyze_stock_sentiment(stock_ticker, count=1):
    '''
    api = authenticate_twitter()

    print(f"Fetching tweets for {stock_ticker}...")
    tweets = fetch_tweets(api, ticker=stock_ticker, count=count)
    '''
    tweets = ['AAPL is shit stock', 'AAPL is a skyrocketing stock!', 'i lost so much in AAPL..']
    if not tweets:
        print("No tweets found for the given stock.")
        return None
    
    print(f"Analyzing sentiment for {len(tweets)} tweets...")
    sentiment_df = analyze_sentiment(tweets)
    if sentiment_df is not None:
        # Save results to a CSV file
        sentiment_df.to_csv(f"{stock_ticker}_sentiment.csv", index=False)
        print(f"\nSentiment analysis saved to {stock_ticker}_sentiment.csv")
    sentiment_summary = sentiment_df["Sentiment"].value_counts(ascending=True, normalize=True) * 100
    if sentiment_summary.iloc[0] > 53:
        people_sentiment = sentiment_summary.index[0]
    else:
        people_sentiment = "Uncertain"

    return people_sentiment

analyze_stock_sentiment('AAPL')