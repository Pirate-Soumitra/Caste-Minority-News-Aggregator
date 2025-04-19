import requests
from bs4 import BeautifulSoup
from newspaper import Article
import feedparser
import pandas as pd
from datetime import datetime
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

keywords = set(kw.lower() for kw in [
    'dalit', 'caste', 'atrocity', 'reservation', 'sc/st', 'scheduled caste',
    'manual scavenging', 'discrimination', 'minority',
    'muslim', 'women', 'woman', 'communal violence', 'mob lynching',
    'caste violence', 'untouchability', 'hindu-muslim', 'marginalized',
    'backward caste', 'obc', 'secularism', 'religious minority',
    'dalit protest', 'discrimination', 'gangrape', 'gang-rape', 'sexual assault',
    'rape', 'murder', 'killing', 'killing of dalit', 'killing of muslim',
    'scheduled tribe', 'girl', 'girls', 'sexual harassment', 'beaten',
    'private parts', 'genitals', 'muslims', 'rapes', 'protest', 'seat'
])

def contains_keywords(text):
    text = text.lower()
    return any(kw in text for kw in keywords)

def scrape_via_rss():
    rss_feeds = {
        'The Hindu': 'https://www.thehindu.com/feeder/default.rss',
        'Indian Express': 'https://indianexpress.com/feeder.rss',
        'Scroll.in': 'https://scroll.in/feeder.rss',
        'The Wire': 'https://thewire.in/rss',
        'Alt News': 'https://www.altnews.in/feed/',
        'Newslaundry': 'https://www.newslaundry.com/feed',
        'The Quint': 'https://www.thequint.com/rss',
        'Telegraph India': 'https://www.telegraphindia.com/feeds/rss.jsp?id=3',
        'The Lallantop': 'https://www.thelallantop.com/rss'
    }
    articles = []
    print("🧠 Starting RSS scraping...")

    for source, url in rss_feeds.items():
        try:
            feed = feedparser.parse(url)
            print(f"📡 Parsed RSS feed from {source} with {len(feed.entries)} entries")

            for entry in feed.entries[:20]:
                try:
                    article_obj = Article(entry.link, headers=HEADERS)
                    article_obj.download()
                    article_obj.parse()
                    content = article_obj.text

                    title = entry.get('title', '')
                    summary = entry.get('summary', '')

                    if contains_keywords(title) or contains_keywords(summary) or contains_keywords(content):
                        print(f"✅ Match found: {title}")

                        if 'published_parsed' in entry:
                            try:
                                date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
                            except:
                                date = datetime.now().strftime('%Y-%m-%d')
                        else:
                            date = datetime.now().strftime('%Y-%m-%d')

                        articles.append({
                            'source': source,
                            'title': title.strip(),
                            'link': entry.get('link', '#'),
                            'summary': summary.strip(),
                            'date': date,
                            'content': content.strip()
                        })
                except Exception as e:
                    print(f"⚠️ Newspaper3k failed on {entry.get('title', '')}: {e}")

        except Exception as e:
            print(f"❌ RSS Error ({source}): {str(e)}")

    print(f"🗞️ Total matched articles from RSS: {len(articles)}")
    return articles

def scrape_the_hindu():
    query = '+OR+'.join([kw.replace(' ', '+') for kw in keywords])
    url = f"https://www.thehindu.com/search/?q={query}"
    articles = []
    print(f"🔍 Scraping The Hindu with query: {query}")

    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    for item in soup.select('div.story-card-news, div.other-card, .story-card'):
        title_elem = item.select_one('h3 a') or item.select_one('a[data-section]')
        if not title_elem:
            continue

        link = title_elem['href']
        if not link.startswith('http'):
            link = "https://www.thehindu.com" + link

        article = {
            'source': 'The Hindu',
            'title': title_elem.text.strip(),
            'link': link,
            'summary': item.select_one('.excerpt').text.strip() if item.select_one('.excerpt') else "",
            'date': "",
            'content': ""
        }

        try:
            art = Article(article['link'], headers=HEADERS)
            art.download()
            art.parse()
            article['content'] = art.text
            if contains_keywords(article['title']) or contains_keywords(article['summary']) or contains_keywords(article['content']):
                if art.publish_date:
                    article['date'] = art.publish_date.strftime('%Y-%m-%d')
                articles.append(article)
        except Exception as e:
            print(f"⚠️ Failed to parse The Hindu article: {e}")

        if len(articles) >= 10:
            break

    return articles

def scrape_indian_express():
    query = '+OR+'.join([kw.replace(' ', '+') for kw in keywords])
    url = f"https://www.indianexpress.com/search/?q={query}"
    articles = []
    print(f"🔍 Scraping Indian Express with query: {query}")

    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    for item in soup.select('.search-details'):
        title_elem = item.select_one('a')
        if not title_elem:
            continue

        article = {
            'source': 'Indian Express',
            'title': title_elem.text.strip(),
            'link': "https://www.indianexpress.com" + title_elem['href'],
            'summary': item.select_one('p').text.strip() if item.select_one('p') else "",
            'date': "",
            'content': ""
        }

        try:
            art = Article(article['link'], headers=HEADERS)
            art.download()
            art.parse()
            article['content'] = art.text
            if contains_keywords(article['title']) or contains_keywords(article['summary']) or contains_keywords(article['content']):
                if art.publish_date:
                    article['date'] = art.publish_date.strftime('%Y-%m-%d')
                articles.append(article)
        except Exception as e:
            print(f"⚠️ Failed to parse Indian Express article: {e}")

        if len(articles) >= 10:
            break

    return articles

def scrape_scroll():
    query = '+OR+'.join([kw.replace(' ', '+') for kw in keywords])
    url = f"https://www.scroll.in/search/?q={query}"
    articles = []
    print(f"🔍 Scraping Scroll with query: {query}")

    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    for item in soup.select('.story-card'):
        title_elem = item.select_one('h3 a')
        if not title_elem:
            continue

        article = {
            'source': 'Scroll.in',
            'title': title_elem.text.strip(),
            'link': "https://www.scroll.in" + title_elem['href'],
            'summary': item.select_one('.excerpt').text.strip() if item.select_one('.excerpt') else "",
            'date': "",
            'content': ""
        }

        try:
            art = Article(article['link'], headers=HEADERS)
            art.download()
            art.parse()
            article['content'] = art.text
            if contains_keywords(article['title']) or contains_keywords(article['summary']) or contains_keywords(article['content']):
                if art.publish_date:
                    article['date'] = art.publish_date.strftime('%Y-%m-%d')
                articles.append(article)
        except Exception as e:
            print(f"⚠️ Failed to parse Scroll article: {e}")

        if len(articles) >= 10:
            break

    return articles

def scrape_article_14():
    articles = []
    base_url = "https://article-14.com"
    listing_url = f"{base_url}/news"
    print("🔍 Scraping Article 14...")

    try:
        response = requests.get(listing_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.select('a.news-card'):
            href = link.get('href')
            if not href.startswith('http'):
                href = base_url + href

            try:
                art = Article(href, headers=HEADERS)
                art.download()
                art.parse()
                title = art.title
                content = art.text
                summary = content[:250]

                if contains_keywords(title) or contains_keywords(summary) or contains_keywords(content):
                    article = {
                        'source': 'Article 14',
                        'title': title,
                        'link': href,
                        'summary': summary,
                        'date': art.publish_date.strftime('%Y-%m-%d') if art.publish_date else datetime.now().strftime('%Y-%m-%d'),
                        'content': content
                    }
                    articles.append(article)
                    if len(articles) >= 10:
                        break
            except Exception as e:
                print(f"⚠️ Failed to parse Article 14 article: {e}")
    except Exception as e:
        print(f"❌ Article 14 main page error: {e}")

    return articles

def fallback_scrape():
    articles = []
    print("🔄 Starting fallback scrapers...")

    try:
        articles += scrape_the_hindu()
    except Exception as e:
        print(f"❌ The Hindu scraper failed: {str(e)}")

    try:
        articles += scrape_indian_express()
    except Exception as e:
        print(f"❌ Indian Express scraper failed: {str(e)}")

    try:
        articles += scrape_scroll()
    except Exception as e:
        print(f"❌ Scroll scraper failed: {str(e)}")

    try:
        articles += scrape_article_14()
    except Exception as e:
        print(f"❌ Article 14 scraper failed: {str(e)}")

    print(f"🗞️ Total articles from fallback: {len(articles)}")
    return articles

def get_all_news():
    print("🚀 Fetching from RSS and fallback scrapers...")
    rss_articles = scrape_via_rss()
    fallback_articles = fallback_scrape()
    all_articles = rss_articles + fallback_articles

    if not all_articles:
        return [{
            'source': 'Error',
            'title': 'No articles found',
            'link': '#',
            'summary': 'Could not retrieve news from any source',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'content': ''
        }]

    for article in all_articles:
        if not article.get('date') or not article['date'].strip():
            article['date'] = datetime.now().strftime('%Y-%m-%d')

    sorted_articles = sorted(all_articles, key=lambda x: x['date'], reverse=True)
    print(f"✅ Fetched {len(sorted_articles)} articles.")
    return sorted_articles
