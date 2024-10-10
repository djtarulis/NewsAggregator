import requests
import nltk
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')  # required to use Vader

def fetch_news(api_key, query, language='en', page_size=50):
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
    

def visualize_sentiment_distribution(articles):
    """
    Visualizes the distribution of sentiment categories for the given articles.

    :param articles: List of articles with the sentiment scores and categories
    """

    #Count sentiment categories
    sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    for article in articles:
        category = article.get('sentiment_category', 'Neutral')
        sentiment_counts[category] += 1
    
    # Plotting the bar chart for sentiment categories
    plt.figure(figsize=(10, 6))
    plt.bar(sentiment_counts.keys(), sentiment_counts.values(), color=['green', 'red', 'blue'])
    plt.title('Sentiment Distribution of News Articles')
    plt.xlabel('Sentiment Category')
    plt.ylabel('Number of Articles')
    plt.show()

def visualize_sentiment_scores(articles):
    """
    Visualizes the distribution of sentiment scores for the given articles

    :param articles: List of articles with the sentiment scores
    """

    # Extract the sentiment scores
    sentiment_scores = [article['sentiment'] for article in articles]

    # Plotting the histogram for sentiment scores
    plt.figure(figsize=(10, 6))
    plt.hist(sentiment_scores, bins=20, color='purple', edgecolor='black')
    plt.title('Distribution of Sentiment Scores')
    plt.xlabel('Sentiment Score')
    plt.ylabel('Number of Articles')
    plt.show()


# Example usage
api_key = '51cac7033df04793a0f9f554d9bc0129'    # key from NewsAPI.org
query = 'politics'

news_articles = fetch_news(api_key, query)
for idx, article in enumerate(news_articles):
    print(f"{idx + 1}. {article['title']}")
    print(f"    Source: {article['source']['name']}")
    print(f"    Sentiment Score: {article['sentiment']}")
    print(f"    Sentiment Category: {article['sentiment_category']}")
    print(f"    URL: {article['url']}\n")

visualize_sentiment_distribution(news_articles)
visualize_sentiment_scores(news_articles)