# Author: Lem Wai Soon
# Created: 21/05/2024

# Mini Project 1 - WebScrapping News Summarizer

# Steps:
# 1. Send an HTTP request to the URL of the webpage you want to access.
# 2. Get the HTML content of the webpage.
# 3. Parse the HTML content.
# 4. Extract useful information/data from the webpage.[Author, Date, Title, Content, Tags, URL of the news article page (sub-links)]
# 5. Store it in a file (CSV).
# 6. Summarize the news article using NLP techniques (HuggingFace Model)

import requests
from bs4 import BeautifulSoup
import chardet
import csv

# URLs to scrape
urls = ["https://www.channelnewsasia.com/topic/cybersecurity",
        "https://thehackernews.com/search/label/Cyber%20Attack"]

# User agents to use
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
    # Add more user agents if needed
]

# Function to get the HTML content of the webpages


def get_html_content(urls):
    html_contents = {}
    for url in urls:
        for user_agent in user_agents:
            headers = {"User-Agent": user_agent}
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                html_contents[url] = response.text
                break  # If the request was successful, break out of the user agent loop
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"403 error fetching {url} with user agent {user_agent}, trying next user agent")
                    continue  # If a 403 error occurred, continue to the next user agent
                else:
                    print(f"Error fetching {url}: {e}")
                    break  # If an error other than 403 occurred, break out of the user agent loop
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {url}: {e}")
                break  # If an error occurred, break out of the user agent loop
    return html_contents

# Function to parse the HTML content and extract articles


def parse_html_content(html_contents):
    articles = []

    for url, content in html_contents.items():
        soup = BeautifulSoup(content, 'html.parser')

        # Find all article links using regex
        if 'channelnewsasia' in url:
            article_links = soup.find_all('a', class_='h6__link list-object__heading-link')
            base_url = 'https://www.channelnewsasia.com'
        elif 'thehackernews' in url:
            article_links = soup.find_all('a', class_='story-link')
            base_url = ''

        for link in article_links:
            relative_link = link['href']
            full_link = base_url + relative_link if base_url else relative_link

            # Fetch the article content
            for user_agent in user_agents:
                headers = {"User-Agent": user_agent}
                try:
                    article_response = requests.get(full_link, headers=headers)
                    article_response.raise_for_status()
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    break
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 403:
                        print(f"403 error fetching {full_link} with user agent {user_agent}, trying next user agent")
                        continue  # If a 403 error occurred, continue to the next user agent
                    else:
                        print(f"Error fetching {full_link}: {e}")
                        break  # If an error other than 403 occurred, break out of the user agent loop
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching {full_link}: {e}")
                    break  # If an error occurred, break out of the user agent loop

            try:
                title = article_soup.find('title').text.strip() if article_soup.find('title') else 'No title'
                tags = article_soup.find('meta', {'name': 'keywords'})[
                    'content'] if article_soup.find('meta', {'name': 'keywords'}) else ''

                if 'channelnewsasia' in full_link:
                    description_div = article_soup.find(
                        'div', {'class': ['content-detail__description content-detail__description--video', 'text']})
                    description = description_div.get_text(separator=' ', strip=True)
                elif 'thehackernews' in full_link:
                    description_paragraphs = article_soup.find('div', {'class': 'articlebody'}).find_all('p')
                    description = ' '.join([p.text for p in description_paragraphs])
                else:
                    description = 'No description available'

                articles.append({
                    'Title': title,
                    'Tags': tags,
                    'Description': description,
                    'URL': full_link
                })
            except Exception as e:
                print(f"Error parsing article content from {full_link}: {e}")

    return articles

# Function to store articles in a CSV file


def store_articles_in_csv(articles, filename='articles.csv'):
    keys = articles[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8-sig') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        for article in articles:
            # Detect the encoding of the description
            encoding = chardet.detect(article['Description'].encode())['encoding']
            # Decode the description using the detected encoding
            article['Description'] = article['Description'].encode(encoding).decode('utf-8', errors='replace')
            dict_writer.writerow(article)


# Main execution
html_contents = get_html_content(urls)
articles = parse_html_content(html_contents)

if articles:
    store_articles_in_csv(articles)
    print(f"Stored {len(articles)} articles in articles.csv")
else:
    print("No articles found.")
