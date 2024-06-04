from flask import Flask, jsonify
import feedparser
import requests
from bs4 import BeautifulSoup
import transformers

app = Flask(__name__)


def fetch_and_parse_rss(url):
    feed = feedparser.parse(url)
    articles = [{'title': entry.get('title', 'No title'), 'link': entry.get('link', '')} for entry in feed.entries]
    return articles


def fetch_article_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text() for p in paragraphs)
        return text
    except requests.RequestException as e:
        print(f"Error fetching article text from {url}: {e}")
        return "Content unavailable"


def summarize_article(article_text):
    # Load Bart tokenizer and model
    tokenizer = transformers.AutoTokenizer.from_pretrained("facebook/bart-base")
    model = transformers.AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-base")

    # Tokenize article
    encoded_input = tokenizer(article_text, return_tensors="pt", max_length=1024, truncation=True)

    # Summarize generation
    summary_ids = model.generate(encoded_input['input_ids'], max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary


@app.route('/articles')
def get_articles():
    try:
        # Get all recent articles using CNN Rss Flow
        cnn_articles = fetch_and_parse_rss('http://rss.cnn.com/rss/edition.rss')

        # Extract most 10 recent articles
        articles_info = cnn_articles[:10]

        # Process articles to fetch their text and generate summaries
        summarized_articles = [{
            'title': article['title'],
            'link': article['link'],
            'summary': summarize_article(fetch_article_text(article['link']))
        } for article in articles_info if article['link']]

        # Return articles' summary
        return jsonify(summarized_articles)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
