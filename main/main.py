import requests

def fetch_news(api_key, query, language='en', page_size=5):
    """
    Fetches news articles based on the provided query.
    
    :param api_key: NewsAPI key
    :param query: The keyword to search for
    :param language: Language of the news articles (default is 'en')
    :param page_size: Number of articles to retrieve (default is 5)
    :return : A list of new articles
    """

    url = f'https://newsapi.org/v2/everything?q={query}&language={language}&pageSize={page_size}'
    headers = {'Authorization': f'Bearer {api_key}'}

    response = requests.get(url, headers = headers)
    
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return articles
    
    else: 
        print(f"Error fetching news: {response.status_code}")
        return []
    
# Example usage
api_key = '51cac7033df04793a0f9f554d9bc0129'    # key from NewsAPI.org
query = 'technology'

news_articles = fetch_news(api_key, query)
for idx, article in enumerate(news_articles):
    print(f"{idx + 1}. {article['title']}")
    print(f"    Source: {article['source']['name']}")
    print(f"    URL: {article['url']}\n")