from flask import Flask, render_template, request
import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer

app = Flask(__name__)

# Set up the Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# NewsAPI key
NEWS_API_KEY = '51cac7033df04793a0f9f554d9bc0129'

def fetch_news(api_key, query, language='en', page_size=25):
    """
    Fetches news articles based on the provided query.
    
    :param api_key: NewsAPI key
    :param query: The keyword to search for
    :param language: Language of the news articles (default is 'en')
    :param page_size: Number of articles to retrieve (default is 50)
    :return : A list of new articles with sentiment scores
    """

    url = f'https://newsapi.org/v2/everything?q={query}&language={language}&pageSize={page_size}'
    headers = {'Authorization': f'Bearer {api_key}'}

    response = requests.get(url, headers = headers)
    
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        analyzer = SentimentIntensityAnalyzer()# Calculates sentiment scores for the article text

        for article in articles:
            # Analyze sentiment of the article description or content
            text = article.get('description') or article.get('content') or ''
            sentiment_score = analyzer.polarity_scores(text)
            article['sentiment'] = sentiment_score['compound'] # Compound score as the overall sentiment

            # Optional: Categorize the sentiment as positive, negative, or neutral
            if sentiment_score['compound'] >= 0.2:
                article['sentiment_category'] = 'Positive'
            elif sentiment_score['compound'] <= -0.2:
                article['sentiment_category'] = 'Negative'
            else:
                article['sentiment_category'] = 'Neutral'

        return articles
    
    else: 
        print(f"Error fetching news: {response.status_code}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    query = request.form.get('query', 'technology') # default query
    news_articles = fetch_news(NEWS_API_KEY, query) if query else []
    sentiment_filter = request.form.get('sentiment_filter', 'all')

    # Apply sentiment filter
    if sentiment_filter!= 'all':
        news_articles = [
            article for article in news_articles 
            if article['sentiment_category'].lower() == sentiment_filter
        ]

    return render_template('index.html', articles=news_articles, query=query, sentiment_filter=sentiment_filter)

if __name__ == '__main__':
    app.run(debug=True)