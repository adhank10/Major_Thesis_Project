from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time

app = Flask(__name__)

# Replace 'YOUR_NEWSAPI_API_KEY' with your actual NewsAPI API key
NEWSAPI_API_KEY = '55ba2e3384ae4193875068701a6147c8'


def get_content_from_url(article_url):
    try:
        response = requests.get(article_url)
        response.raise_for_status()  # Check for any request errors
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the main content of the article
        content = ""
        paragraphs = soup.find_all('p')
        if paragraphs:
            content = " ".join(p.get_text() for p in paragraphs)

        return content
    except (requests.RequestException, ValueError, TypeError):
        return None


def generate_summary(text, num_sentences=3):
    sentences = sent_tokenize(text)
    similarity_matrix = create_similarity_matrix(sentences)

    # Build the graph from the similarity matrix
    graph = nx.from_numpy_array(similarity_matrix)

    # Apply the PageRank algorithm
    scores = nx.pagerank(graph)

    # Sort the sentences by their scores
    ranked_sentences = sorted(
        ((scores[i], sentence) for i, sentence in enumerate(sentences)), reverse=True)

    # Select the top sentences as the summary
    summary = ' '.join(
        [sentence for _, sentence in ranked_sentences[:num_sentences]])

    return summary


def create_similarity_matrix(sentences):
    # Dummy implementation for the similarity matrix 
    num_sentences = len(sentences)
    similarity_matrix = np.zeros((num_sentences, num_sentences))

    #  Implementation to calculate similarity between sentences goes here
    #  The similarity matrix with dummy values (similarity scores)
    for i in range(num_sentences):
        for j in range(num_sentences):
            # Replace this with the actual similarity calculation
            similarity_matrix[i, j] = 0.5

    return similarity_matrix


def get_news(query):
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWSAPI_API_KEY}'
    response = requests.get(url)
    data = response.json()
    articles = data['articles'][:10]  # Limit to 10 articles

    # Filter out articles with None content 
    scraped_articles = []
    for article in articles:
        article_url = article['url']
        content = get_content_from_url(article_url)
        if content is not None:
            # Generate summary for the article content
            article['content'] = content
            article['summary'] = generate_summary(content)
            # Include the source in the  article data
            article['source'] = article['source']['name'] if 'source' in article and 'name' in article['source'] else 'Unknown'
            scraped_articles.append(article)

    return scraped_articles


@app.route('/')
def index():
    start_time = time.time()  # Record the start time

    # Default query: technology
    query = request.args.get('query', 'technology')
    news = get_news(query)

    end_time = time.time()  # Record the end time
    processing_time = end_time - start_time  # Calculate the processing time

    return render_template('index.html', news=news, processing_time=processing_time)


if __name__ == '__main__':
    app.run(debug=True)
