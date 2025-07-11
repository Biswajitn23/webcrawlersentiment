"""
Sentiment Analysis Module
Analyzes sentiment of text content using TextBlob
"""

from textblob import TextBlob
import re
from typing import Dict

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the sentiment analyzer"""
        self.positive_threshold = 0.1
        self.negative_threshold = -0.1
    
    def analyze(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of the given text
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        if not text or not text.strip():
            return self._empty_result()
        
        try:
            # Clean text for better analysis
            cleaned_text = self._preprocess_text(text)
            
            if not cleaned_text:
                return self._empty_result()
            
            # Perform sentiment analysis using TextBlob
            blob = TextBlob(cleaned_text)
            
            # Get polarity and subjectivity
            polarity = blob.sentiment.polarity  # Range: -1 (negative) to 1 (positive)
            subjectivity = blob.sentiment.subjectivity  # Range: 0 (objective) to 1 (subjective)
            
            # Determine sentiment label
            if polarity > self.positive_threshold:
                label = "Positive"
            elif polarity < self.negative_threshold:
                label = "Negative"
            else:
                label = "Neutral"
            
            # Calculate normalized scores (0-1 range)
            positive_score = max(0, polarity)
            negative_score = max(0, -polarity)
            neutral_score = 1 - abs(polarity)
            
            # Normalize scores to sum to 1
            total = positive_score + negative_score + neutral_score
            if total > 0:
                positive_score /= total
                negative_score /= total
                neutral_score /= total
            
            return {
                'compound_score': polarity,
                'positive': round(positive_score, 3),
                'negative': round(negative_score, 3),
                'neutral': round(neutral_score, 3),
                'subjectivity': round(subjectivity, 3),
                'label': label,
                'confidence': self._calculate_confidence(polarity, subjectivity)
            }
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return self._empty_result()
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better sentiment analysis
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{3,}', '...', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        
        # Remove excessive whitespace again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_confidence(self, polarity: float, subjectivity: float) -> float:
        """
        Calculate confidence score based on polarity and subjectivity
        
        Args:
            polarity: Polarity score (-1 to 1)
            subjectivity: Subjectivity score (0 to 1)
            
        Returns:
            Confidence score (0 to 1)
        """
        # Higher absolute polarity and higher subjectivity indicate higher confidence
        polarity_confidence = abs(polarity)
        subjectivity_confidence = subjectivity
        
        # Combine scores (weighted towards polarity)
        confidence = (0.7 * polarity_confidence + 0.3 * subjectivity_confidence)
        
        return round(confidence, 3)
    
    def _empty_result(self) -> Dict[str, any]:
        """
        Return empty/neutral result for invalid text
        
        Returns:
            Dictionary with neutral sentiment values
        """
        return {
            'compound_score': 0.0,
            'positive': 0.33,
            'negative': 0.33,
            'neutral': 0.34,
            'subjectivity': 0.0,
            'label': 'Neutral',
            'confidence': 0.0
        }
    
    def analyze_batch(self, texts: list) -> list:
        """
        Analyze sentiment for a batch of texts
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of sentiment analysis results
        """
        results = []
        for text in texts:
            result = self.analyze(text)
            results.append(result)
        
        return results
    
    def get_overall_sentiment(self, sentiment_results: list) -> Dict[str, any]:
        """
        Calculate overall sentiment from multiple results
        
        Args:
            sentiment_results: List of sentiment analysis results
            
        Returns:
            Overall sentiment statistics
        """
        if not sentiment_results:
            return self._empty_result()
        
        # Calculate averages
        total_compound = sum(result['compound_score'] for result in sentiment_results)
        total_positive = sum(result['positive'] for result in sentiment_results)
        total_negative = sum(result['negative'] for result in sentiment_results)
        total_neutral = sum(result['neutral'] for result in sentiment_results)
        total_subjectivity = sum(result['subjectivity'] for result in sentiment_results)
        
        count = len(sentiment_results)
        
        avg_compound = total_compound / count
        avg_positive = total_positive / count
        avg_negative = total_negative / count
        avg_neutral = total_neutral / count
        avg_subjectivity = total_subjectivity / count
        
        # Determine overall label
        if avg_compound > self.positive_threshold:
            overall_label = "Positive"
        elif avg_compound < self.negative_threshold:
            overall_label = "Negative"
        else:
            overall_label = "Neutral"
        
        return {
            'compound_score': round(avg_compound, 3),
            'positive': round(avg_positive, 3),
            'negative': round(avg_negative, 3),
            'neutral': round(avg_neutral, 3),
            'subjectivity': round(avg_subjectivity, 3),
            'label': overall_label,
            'confidence': self._calculate_confidence(avg_compound, avg_subjectivity),
            'total_analyzed': count
        }
