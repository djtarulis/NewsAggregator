from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import matplotlib
matplotlib.use('Agg')   # Render the plots to image files without attempting to open a GUI window
import requests
import os
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from models import user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Avengedsevenfold1!'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirect to login page if not logged in

# Set up the Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()


# NewsAPI key
NEWS_API_KEY = '51cac7033df04793a0f9f554d9bc0129'

def fetch_news(api_key, query, language='en', page_size=100, page=1):
    """
    Fetches news articles based on the provided query.
    
    :param api_key: NewsAPI key
    :param query: The keyword to search for
    :param language: Language of the news articles (default is 'en')
    :param page_size: Number of articles to retrieve (default is 50)
    :param page: Page number to retrieve (default is 1)
    :return : A list of new articles with sentiment scores
    """

    url = f'https://newsapi.org/v2/everything?q={query}&language={language}&pageSize={page_size}&page={page}'
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
    
def save_sentiment_distribution_plot(articles, output_path='static/sentiment_distribution.png'):    
    sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    for article in articles:
        category = article.get('sentiment_category', 'Neutral')
        sentiment_counts[category] += 1

    plt.figure(figsize=(10, 6))
    plt.bar(sentiment_counts.keys(), sentiment_counts.values(), color=['green', 'red', 'blue'])
    plt.title('Sentiment Distribution of News Articles')
    plt.xlabel('Sentiment Category')
    plt.ylabel('Number of Articles')
    plt.savefig(output_path)
    plt.close()

def save__sentiment_scores(articles, output_path='static/sentiment_scores.png'):
    # Extract the sentiment scores
    sentiment_scores = [article['sentiment'] for article in articles]

    # Plotting the histogram for sentiment scores
    plt.figure(figsize=(10, 6))
    plt.hist(sentiment_scores, bins=20, color='purple', edgecolor='black')
    plt.title('Distribution of Sentiment Scores')
    plt.xlabel('Sentiment Score')
    plt.ylabel('Number of Articles')
    plt.savefig(output_path)
    plt.close()

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    query = request.form.get('query', 'technology') # default query
    sentiment_filter = request.form.get('sentiment_filter', 'all')
    page = int(request.form.get('page', 1))
    page_size = 15
    news_articles = fetch_news(NEWS_API_KEY, query, page_size=page_size, page=page) if query else []


    # Apply sentiment filter
    if sentiment_filter!= 'all':
        news_articles = [
            article for article in news_articles 
            if article['sentiment_category'].lower() == sentiment_filter
        ]
    
    # Save sentiment distribution plot
    if news_articles:
        save_sentiment_distribution_plot(news_articles)
        save__sentiment_scores(news_articles)

    return render_template('index.html', articles=news_articles, query=query, sentiment_filter=sentiment_filter, page=page)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        existing_user = user.User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        # Create a new user with a hashed password
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = user.User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Find the user by username
        user = user.User.query.filter_by(username=username).first()
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id):
    return user.User.query.get(int(user_id))

# Create the database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':

    # Run the Flask app
    app.run(debug=True)