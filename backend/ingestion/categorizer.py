"""
Post categorization using BERTopic and keyword matching.
Extracts topics, tool types, and LLMs used from post content.
"""

from bertopic import BERTopic
import re
from typing import List, Dict
from sklearn.feature_extraction.text import CountVectorizer

class PostCategorizer:
    """Extract categories and compute quality scores for posts."""
    
    def __init__(self):
        """Initialize categorizer with keyword dictionaries."""
        self.bertopic = None
        self.topics = None
        self.probs = None
        
        # Stop words to filter out from topic generation
        self.stop_words = [
            'to', 'and', 'the', 'a', 'an', 'is', 'of', 'in', 'for', 'on', 
            'with', 'as', 'by', 'at', 'it', 'from', 'be', 'was', 'are', 
            'that', 'this', 'but', 'not', 'or', 'if', 'so', 'up', 'out',
            'what', 'how', 'why', 'when', 'where', 'which', 'who', 'whom',
            'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because',
            'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
            'against', 'between', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
            'over', 'under', 'again', 'further', 'then', 'once', "my", "et", "al", "me", "you", 
            "ai", "gemini", "claude", "gpt", "openai", "perplexity", "cursor"
        ]
        
        # Tool type keywords
        self.tool_keywords = {
            'flashcard': ['flashcard', 'flash card', 'anki', 'quizlet'],
            'quiz': ['quiz', 'test', 'question generator', 'practice problems', 'practice questions'],
            'interactive': ['interactive', 'visualization', 'visualizer', 'simulator', 'playground'],
            'diagram': ['diagram', 'mermaid', 'concept map', 'mind map', 'graph'],
            'notebook': ['notebook', 'colab', 'jupyter'],
            'chat': ['chat', 'conversation', 'dialogue', 'tutor', 'chatbot'],
            'summary': ['summary', 'summarize', 'notes', 'outline'],
            'video': ['video', 'recording', 'screencast'],
            'tutorial': ['tutorial', 'guide', 'walkthrough', 'explanation'],
            "lecture": ["lecture"],
        }
        
        # LLM keywords
        self.llm_keywords = {
            'Claude': ['claude', 'anthropic'],
            'GPT': ['gpt', 'chatgpt', 'openai'],
            'Gemini': ['gemini', 'google'],
            'NotebookLM': ['notebooklm', 'notebook lm'],
            'Perplexity': ['perplexity'],
            'Cursor': ['cursor'],
            'Other': []
        }
    
    def train_topic_model(self, documents: List[str]):
        """
        Train BERTopic model on all posts to extract topics.
        
        Args:
            documents: List of post contents
        """
        # Strip HTML tags from documents for better topic modeling
        cleaned_docs = []
        for doc in documents:
            # Remove XML/HTML tags
            clean = re.sub(r'<[^>]+>', ' ', doc)
            # Remove extra whitespace
            clean = re.sub(r'\s+', ' ', clean).strip()
            cleaned_docs.append(clean)
        
        # Use CountVectorizer with stop words to filter out common words
        vectorizer_model = CountVectorizer(stop_words=self.stop_words)
        
        self.bertopic = BERTopic(
            language="english",
            calculate_probabilities=True,
            verbose=False,
            min_topic_size=3,
            nr_topics='auto',
            vectorizer_model=vectorizer_model
        )
        
        try:
            self.topics, self.probs = self.bertopic.fit_transform(cleaned_docs)
            print(f"  Identified {len(set(self.topics)) - (1 if -1 in self.topics else 0)} topics")
        except Exception as e:
            print(f"  Warning: Topic modeling failed: {e}")
            print(f"  Using fallback topic extraction")
            self.topics = [-1] * len(documents)  # All outliers
    
    def extract_topics(self, content: str, post_idx: int = None) -> List[str]:
        """
        Extract topic labels for a post using BERTopic.
        
        Args:
            content: Post content
            post_idx: Index of post in training data (if available)
            
        Returns:
            List of topic keywords
        """
        if self.bertopic is None or self.topics is None:
            return []
        
        try:
            # Get topic for this post
            if post_idx is not None and post_idx < len(self.topics):
                topic_id = self.topics[post_idx]
            else:
                # Clean content
                clean = re.sub(r'<[^>]+>', ' ', content)
                clean = re.sub(r'\s+', ' ', clean).strip()
                topic_id, _ = self.bertopic.transform([clean])
                topic_id = topic_id[0]
            
            if topic_id == -1:  # Outlier
                return []
            
            # Get representative words for topic
            topic_words = self.bertopic.get_topic(topic_id)
            if topic_words:
                return [word for word, _ in topic_words[:3]]  # Top 3 words
        except Exception as e:
            # Silently handle errors - some posts may not fit well
            pass
        
        return []
    
    def extract_tools(self, content: str) -> List[str]:
        """
        Extract tool types using keyword matching.
        
        Args:
            content: Post content
            
        Returns:
            List of detected tool types
        """
        content_lower = content.lower()
        detected_tools = []
        
        for tool, keywords in self.tool_keywords.items():
            if any(kw in content_lower for kw in keywords):
                detected_tools.append(tool)
        
        return detected_tools if detected_tools else ['other']
    
    def extract_llms(self, content: str) -> List[str]:
        """
        Extract LLMs used via keyword matching.
        
        Args:
            content: Post content
            
        Returns:
            List of detected LLMs
        """
        content_lower = content.lower()
        detected_llms = []
        
        for llm, keywords in self.llm_keywords.items():
            if llm == 'Other':
                continue
            if any(kw in content_lower for kw in keywords):
                detected_llms.append(llm)
        
        return detected_llms if detected_llms else ['Other']
    
    def calculate_impressiveness(self, post: Dict) -> float:
        """
        Score post quality/impressiveness based on various factors.
        
        Factors:
        - Engagement (reactions, replies)
        - Content length
        - Has attachments
        - Has external links
        
        Args:
            post: Post dictionary
            
        Returns:
            Impressiveness score (0-100+)
        """
        score = 0.0
        
        # Engagement
        score += post.get('num_reactions', 0) * 2
        score += post.get('num_replies', 0) * 1
        
        # Completeness - content length
        content_length = len(post.get('content', ''))
        score += min(content_length / 1000, 5)  # Max 5 points for length
        
        # Has attachments
        if post.get('attachment_urls'):
            score += 5
        
        # Has external links
        if post.get('github_url') or post.get('website_url'):
            score += 3
        
        return score
