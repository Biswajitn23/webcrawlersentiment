"""
Web Crawler + Sentiment Analysis Engine
A Streamlit application for crawling websites and analyzing sentiment
"""

import streamlit as st
import pandas as pd
import time
from urllib.parse import urlparse
import os
from datetime import datetime

from crawler import WebCrawler
from sentiment_analyzer import SentimentAnalyzer
from visualizer import SentimentVisualizer

def main():
    st.set_page_config(
        page_title="Web Crawler & Sentiment Analysis",
        page_icon="🕸️",
        layout="wide"
    )
    
    st.title("🕸️ Web Crawler & Sentiment Analysis Engine")
    st.markdown("Crawl websites and analyze the sentiment of their content")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # URL input
        start_url = st.text_input(
            "Starting URL:",
            placeholder="https://example.com",
            help="Enter the URL where crawling should start"
        )
        
        # Crawl depth
        max_depth = st.slider(
            "Crawl Depth:",
            min_value=1,
            max_value=5,
            value=2,
            help="Maximum depth to crawl (1 = only starting page)"
        )
        
        # Max pages limit
        max_pages = st.slider(
            "Max Pages:",
            min_value=1,
            max_value=50,
            value=10,
            help="Maximum number of pages to crawl"
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            delay_between_requests = st.slider(
                "Delay between requests (seconds):",
                min_value=0.0,
                max_value=5.0,
                value=1.0,
                step=0.5,
                help="Delay to be respectful to the server"
            )
            
            include_external = st.checkbox(
                "Include external links",
                value=False,
                help="Allow crawling external domains (use with caution)"
            )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Start Crawling", type="primary", disabled=not start_url):
            if not start_url:
                st.error("Please enter a starting URL")
                return
                
            try:
                # Validate URL
                parsed_url = urlparse(start_url)
                if not parsed_url.scheme or not parsed_url.netloc:
                    st.error("Please enter a valid URL (including http:// or https://)")
                    return
                
                # Initialize components
                crawler = WebCrawler(
                    max_depth=max_depth,
                    max_pages=max_pages,
                    delay=delay_between_requests,
                    allow_external=include_external
                )
                analyzer = SentimentAnalyzer()
                visualizer = SentimentVisualizer()
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Results containers
                results_container = st.empty()
                
                # Start crawling
                status_text.text("Starting crawler...")
                crawled_pages = []
                
                for i, page_data in enumerate(crawler.crawl(start_url)):
                    # Update progress
                    progress = min((i + 1) / max_pages, 1.0)
                    progress_bar.progress(progress)
                    status_text.text(f"Crawling: {page_data['url']}")
                    
                    # Analyze sentiment
                    sentiment_data = analyzer.analyze(page_data['content'])
                    
                    # Combine data
                    result = {
                        'URL': page_data['url'],
                        'Title': page_data['title'],
                        'Content Preview': page_data['content'][:300] + "..." if len(page_data['content']) > 300 else page_data['content'],
                        'Word Count': len(page_data['content'].split()),
                        'Sentiment Score': sentiment_data['compound_score'],
                        'Sentiment Label': sentiment_data['label'],
                        'Positive': sentiment_data['positive'],
                        'Negative': sentiment_data['negative'],
                        'Neutral': sentiment_data['neutral']
                    }
                    
                    crawled_pages.append(result)
                    
                    # Update results display in real-time
                    if crawled_pages:
                        df = pd.DataFrame(crawled_pages)
                        with results_container.container():
                            st.subheader(f"📊 Results ({len(crawled_pages)} pages crawled)")
                            st.dataframe(
                                df[['URL', 'Title', 'Content Preview', 'Sentiment Score', 'Sentiment Label']],
                                use_container_width=True
                            )
                    
                    time.sleep(delay_between_requests)
                
                status_text.text("✅ Crawling completed!")
                progress_bar.progress(1.0)
                
                if crawled_pages:
                    # Store results in session state
                    st.session_state['crawl_results'] = crawled_pages
                    st.session_state['crawl_timestamp'] = datetime.now()
                    
                    # Final results display
                    display_results(crawled_pages, visualizer)
                else:
                    st.warning("No pages were successfully crawled.")
                    
            except Exception as e:
                st.error(f"An error occurred during crawling: {str(e)}")
    
    with col2:
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. Enter a starting URL
        2. Configure crawl settings
        3. Click "Start Crawling"
        4. View real-time results
        5. Download CSV when complete
        """)
        
        if 'crawl_results' in st.session_state:
            st.markdown("### 📥 Download Results")
            df = pd.DataFrame(st.session_state['crawl_results'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"crawl_results_{st.session_state['crawl_timestamp'].strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def display_results(crawled_pages, visualizer):
    """Display comprehensive results with visualizations"""
    
    df = pd.DataFrame(crawled_pages)
    
    # Summary metrics
    st.subheader("📈 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pages", len(df))
    with col2:
        avg_sentiment = df['Sentiment Score'].mean()
        st.metric("Average Sentiment", f"{avg_sentiment:.3f}")
    with col3:
        positive_count = len(df[df['Sentiment Label'] == 'Positive'])
        st.metric("Positive Pages", positive_count)
    with col4:
        total_words = df['Word Count'].sum()
        st.metric("Total Words", f"{total_words:,}")
    
    # Visualizations
    st.subheader("📊 Sentiment Analysis Visualizations")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Distribution", "Trends", "Detailed Results"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment distribution pie chart
            fig_pie = visualizer.create_pie_chart(df)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Sentiment score histogram
            fig_hist = visualizer.create_histogram(df)
            st.plotly_chart(fig_hist, use_container_width=True)
    
    with tab2:
        # Sentiment over pages (trend)
        fig_trend = visualizer.create_trend_chart(df)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Word count vs sentiment scatter
        fig_scatter = visualizer.create_scatter_plot(df)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab3:
        # Detailed results table
        st.dataframe(
            df[['URL', 'Title', 'Content Preview', 'Word Count', 'Sentiment Score', 'Sentiment Label']],
            use_container_width=True
        )
        
        # Top positive and negative pages
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🟢 Most Positive Pages")
            top_positive = df.nlargest(3, 'Sentiment Score')[['URL', 'Title', 'Sentiment Score']]
            st.dataframe(top_positive, use_container_width=True)
        
        with col2:
            st.subheader("🔴 Most Negative Pages")
            top_negative = df.nsmallest(3, 'Sentiment Score')[['URL', 'Title', 'Sentiment Score']]
            st.dataframe(top_negative, use_container_width=True)

if __name__ == "__main__":
    main()
