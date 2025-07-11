# Web Crawler & Sentiment Analysis Engine

## Overview

This application is a web crawler combined with sentiment analysis capabilities, built using Streamlit for the user interface. The system crawls websites, extracts text content, and performs sentiment analysis on the collected data. It provides visualizations and insights about the sentiment distribution across crawled pages.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: Streamlit-based web interface for user interaction and data visualization
- **Web Crawling**: Custom crawler with domain restrictions and depth limits
- **Text Processing**: Multi-layered text extraction using trafilatura and BeautifulSoup
- **Sentiment Analysis**: TextBlob-based sentiment analysis engine
- **Visualization**: Plotly-powered interactive charts and graphs

## Key Components

### 1. Web Crawler (`crawler.py`)
- **Purpose**: Handles systematic crawling of web pages with configurable limits
- **Features**: 
  - Domain restriction enforcement
  - Robots.txt compliance
  - Configurable crawl depth and page limits
  - Rate limiting with delays between requests
- **Dependencies**: requests, urllib

### 2. Text Extractor (`text_extractor.py`)
- **Purpose**: Extracts clean, readable text from HTML content
- **Strategy**: Uses trafilatura as primary extraction method with BeautifulSoup fallback
- **Features**:
  - Removes unwanted HTML elements (scripts, styles, navigation)
  - Extracts titles and internal links
  - Text cleaning and normalization

### 3. Sentiment Analyzer (`sentiment_analyzer.py`)
- **Purpose**: Performs sentiment analysis on extracted text content
- **Engine**: TextBlob for natural language processing
- **Output**: Polarity scores, subjectivity scores, and categorical labels (Positive/Negative/Neutral)
- **Thresholds**: Configurable positive (0.1) and negative (-0.1) thresholds

### 4. Visualizer (`visualizer.py`)
- **Purpose**: Creates interactive visualizations of sentiment analysis results
- **Library**: Plotly for interactive charts
- **Features**: Pie charts for sentiment distribution with custom color schemes

### 5. Main Application (`app.py`)
- **Purpose**: Streamlit-based user interface orchestrating all components
- **Features**: Configuration sidebar, real-time crawling progress, data export capabilities

## Data Flow

1. **User Input**: User provides starting URL and crawl parameters via Streamlit interface
2. **Web Crawling**: WebCrawler systematically visits pages within specified constraints
3. **Content Extraction**: TextExtractor processes HTML and extracts clean text content
4. **Sentiment Analysis**: SentimentAnalyzer processes extracted text and generates sentiment scores
5. **Data Storage**: Results stored in pandas DataFrames for manipulation and export
6. **Visualization**: SentimentVisualizer creates interactive charts displayed in Streamlit interface
7. **Export**: Users can download results as CSV files

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **requests**: HTTP library for web crawling
- **textblob**: Natural language processing for sentiment analysis
- **trafilatura**: Primary text extraction from HTML
- **beautifulsoup4**: Fallback HTML parsing and extraction
- **plotly**: Interactive visualization library

### System Dependencies
- **urllib**: URL parsing and robots.txt handling (built-in)
- **logging**: Application logging (built-in)
- **datetime**: Timestamp generation (built-in)

## Deployment Strategy

The application is designed for deployment on Replit with the following characteristics:

- **Single-file entry point**: `app.py` serves as the main application entry
- **No database requirements**: Uses in-memory data structures (pandas DataFrames)
- **Minimal configuration**: All settings configurable through Streamlit interface
- **Self-contained**: All dependencies manageable through standard Python package managers

### Potential Enhancements
- Database integration could be added later for persistent storage of crawl results
- API endpoints could be exposed for programmatic access
- Background task processing for large-scale crawls
- User authentication for multi-user scenarios

The architecture prioritizes simplicity and modularity, making it easy to extend and modify individual components without affecting the overall system.