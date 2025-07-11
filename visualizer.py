"""
Visualization Module
Creates charts and graphs for sentiment analysis results
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List

class SentimentVisualizer:
    def __init__(self):
        """Initialize the visualizer with color schemes"""
        self.sentiment_colors = {
            'Positive': '#2E8B57',  # Sea Green
            'Negative': '#DC143C',  # Crimson
            'Neutral': '#4682B4'    # Steel Blue
        }
        
        self.color_sequence = ['#2E8B57', '#DC143C', '#4682B4', '#FF6347', '#20B2AA']
    
    def create_pie_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Create pie chart showing sentiment distribution
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Plotly figure object
        """
        # Count sentiment labels
        sentiment_counts = df['Sentiment Label'].value_counts()
        
        # Create pie chart
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Sentiment Distribution",
            color=sentiment_counts.index,
            color_discrete_map=self.sentiment_colors
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            showlegend=True,
            height=400,
            font=dict(size=12)
        )
        
        return fig
    
    def create_histogram(self, df: pd.DataFrame) -> go.Figure:
        """
        Create histogram of sentiment scores
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Plotly figure object
        """
        fig = px.histogram(
            df,
            x='Sentiment Score',
            nbins=20,
            title='Distribution of Sentiment Scores',
            labels={'Sentiment Score': 'Sentiment Score', 'count': 'Number of Pages'},
            color_discrete_sequence=[self.color_sequence[0]]
        )
        
        # Add vertical lines for positive/negative thresholds
        fig.add_vline(x=0.1, line_dash="dash", line_color="green", 
                     annotation_text="Positive Threshold")
        fig.add_vline(x=-0.1, line_dash="dash", line_color="red", 
                     annotation_text="Negative Threshold")
        fig.add_vline(x=0, line_dash="solid", line_color="blue", 
                     annotation_text="Neutral")
        
        fig.update_layout(
            xaxis_title="Sentiment Score",
            yaxis_title="Number of Pages",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_trend_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Create line chart showing sentiment trend across pages
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Plotly figure object
        """
        # Add page index for x-axis
        df_copy = df.copy()
        df_copy['Page Index'] = range(1, len(df_copy) + 1)
        
        fig = go.Figure()
        
        # Add sentiment score line
        fig.add_trace(go.Scatter(
            x=df_copy['Page Index'],
            y=df_copy['Sentiment Score'],
            mode='lines+markers',
            name='Sentiment Score',
            line=dict(color=self.color_sequence[0], width=2),
            marker=dict(size=6),
            hovertemplate='<b>Page %{x}</b><br>Sentiment: %{y:.3f}<br>URL: %{customdata}<extra></extra>',
            customdata=df_copy['URL']
        ))
        
        # Add horizontal reference lines
        fig.add_hline(y=0.1, line_dash="dash", line_color="green", 
                     annotation_text="Positive", annotation_position="right")
        fig.add_hline(y=-0.1, line_dash="dash", line_color="red", 
                     annotation_text="Negative", annotation_position="right")
        fig.add_hline(y=0, line_dash="solid", line_color="blue", 
                     annotation_text="Neutral", annotation_position="right")
        
        fig.update_layout(
            title="Sentiment Trend Across Crawled Pages",
            xaxis_title="Page Number (Crawl Order)",
            yaxis_title="Sentiment Score",
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_scatter_plot(self, df: pd.DataFrame) -> go.Figure:
        """
        Create scatter plot of word count vs sentiment score
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Plotly figure object
        """
        fig = px.scatter(
            df,
            x='Word Count',
            y='Sentiment Score',
            color='Sentiment Label',
            title='Word Count vs Sentiment Score',
            hover_data=['URL', 'Title'],
            color_discrete_map=self.sentiment_colors
        )
        
        fig.update_traces(
            marker=dict(size=8, opacity=0.7),
            hovertemplate='<b>%{customdata[1]}</b><br>' +
                         'Word Count: %{x}<br>' +
                         'Sentiment: %{y:.3f}<br>' +
                         'URL: %{customdata[0]}<extra></extra>'
        )
        
        fig.update_layout(
            xaxis_title="Word Count",
            yaxis_title="Sentiment Score",
            height=400
        )
        
        return fig
    
    def create_bar_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Create bar chart showing top positive and negative pages
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Plotly figure object
        """
        # Get top 5 positive and negative pages
        top_positive = df.nlargest(5, 'Sentiment Score')
        top_negative = df.nsmallest(5, 'Sentiment Score')
        
        # Combine and create labels
        combined_df = pd.concat([top_negative, top_positive])
        combined_df['Short URL'] = combined_df['URL'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
        
        # Create colors based on sentiment
        colors = ['red' if score < 0 else 'green' for score in combined_df['Sentiment Score']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=combined_df['Sentiment Score'],
                y=combined_df['Short URL'],
                orientation='h',
                marker_color=colors,
                hovertemplate='<b>%{customdata}</b><br>Sentiment: %{x:.3f}<extra></extra>',
                customdata=combined_df['Title']
            )
        ])
        
        fig.update_layout(
            title="Top Positive and Negative Pages",
            xaxis_title="Sentiment Score",
            yaxis_title="Pages",
            height=400,
            yaxis=dict(autorange="reversed")  # Show most positive at top
        )
        
        return fig
    
    def create_sentiment_breakdown(self, df: pd.DataFrame) -> go.Figure:
        """
        Create stacked bar chart showing positive/negative/neutral breakdown
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Plotly figure object
        """
        # Calculate averages
        avg_positive = df['Positive'].mean()
        avg_negative = df['Negative'].mean()
        avg_neutral = df['Neutral'].mean()
        
        fig = go.Figure(data=[
            go.Bar(name='Positive', x=['Overall'], y=[avg_positive], marker_color=self.sentiment_colors['Positive']),
            go.Bar(name='Neutral', x=['Overall'], y=[avg_neutral], marker_color=self.sentiment_colors['Neutral']),
            go.Bar(name='Negative', x=['Overall'], y=[avg_negative], marker_color=self.sentiment_colors['Negative'])
        ])
        
        fig.update_layout(
            barmode='stack',
            title='Average Sentiment Composition',
            yaxis_title='Proportion',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_summary_stats(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Calculate summary statistics for visualization
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Dictionary with summary statistics
        """
        stats = {
            'total_pages': len(df),
            'average_sentiment': df['Sentiment Score'].mean(),
            'sentiment_std': df['Sentiment Score'].std(),
            'most_positive': {
                'score': df['Sentiment Score'].max(),
                'url': df.loc[df['Sentiment Score'].idxmax(), 'URL'],
                'title': df.loc[df['Sentiment Score'].idxmax(), 'Title']
            },
            'most_negative': {
                'score': df['Sentiment Score'].min(),
                'url': df.loc[df['Sentiment Score'].idxmin(), 'URL'],
                'title': df.loc[df['Sentiment Score'].idxmin(), 'Title']
            },
            'sentiment_distribution': df['Sentiment Label'].value_counts().to_dict(),
            'average_word_count': df['Word Count'].mean(),
            'total_words': df['Word Count'].sum()
        }
        
        return stats
