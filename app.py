# app.py

import streamlit as st
from scraper import get_all_news
import pandas as pd
from datetime import datetime, timedelta

# Configure app
st.set_page_config(
    page_title="Caste & Minority News Aggregator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .news-card {
        border-left: 4px solid #ff4b4b;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
        border-radius: 0.25rem;
    }
    .news-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
    }
    .news-source {
        font-size: 0.8rem;
        color: #7f8c8d;
    }
    .news-date {
        font-size: 0.8rem;
        color: #7f8c8d;
        float: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📰 Caste & Minority News Aggregator")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    selected_source = st.selectbox("News Source", [
    'All Sources', 'The Hindu', 'Indian Express', 'Scroll.in',
    'The Wire', 'Alt News', 'Newslaundry', 'The Quint', 'Article 14',
    'Telegraph India', 'The Lallantop'
    ])    
    days_back = st.slider("Show news from last N days", 1, 30, 7)
    if st.button("🔄 Refresh News"):
        st.cache_data.clear()

# Cached loading
@st.cache_data(ttl=3600)
def load_news():
    return get_all_news()

# Fetch and display
with st.spinner("Fetching latest news..."):
    news_data = load_news()

df = pd.DataFrame(news_data)

if not df.empty and 'date' in df.columns:
    try:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        cutoff_date = datetime.now() - timedelta(days=days_back)
        df = df[df['date'] >= cutoff_date]
    except Exception as e:
        st.error(f"❌ Date parsing error: {e}")

# Filter by source
if selected_source != 'All Sources' and 'source' in df.columns:
    df = df[df['source'] == selected_source]

# Display
if df.empty:
    st.warning("No news articles found matching your criteria.")
else:
    st.subheader(f"📢 Latest News ({len(df)} articles)")
    for _, row in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{row['title']}</div>
                <div>
                    <span class="news-source">{row['source']}</span>
                    <span class="news-date">
                        {pd.to_datetime(row['date']).strftime('%b %d, %Y') if not pd.isna(row['date']) else 'Date not available'}
                    </span>
                </div>
                <p>{row['summary'][:200] + '...' if isinstance(row['summary'], str) and len(row['summary']) > 200 else row.get('summary', '')}</p>
                <a href="{row['link']}" target="_blank">Read full article →</a>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("View full content"):
                st.write(row.get('content', 'Content not available'))