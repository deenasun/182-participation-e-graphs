"""
Post categorization using keyword matching aligned with course topics.
Extracts topics, tool types, and LLMs used from post content.
"""

import re
from typing import List, Dict

class PostCategorizer:
    """Extract categories and compute quality scores for posts."""
    
    def __init__(self):
        """Initialize categorizer with keyword dictionaries."""
        
        # Course-aligned topic keywords (based on CS 182 schedule)
        self.course_topics = {
            # Optimization topics (Weeks 1-4)
            'SGD & Optimization Basics': [
                'sgd', 'stochastic gradient descent', 'gradient descent', 
                'momentum', 'optimization', 'optimizer', 'learning rate',
                'implicit regularization', 'convergence'
            ],
            'Adam & Advanced Optimizers': [
                'adam', 'adamw', 'rmsprop', 'adagrad', 'locally linear',
                'matrix norm', 'induced norm'
            ],
            'muP & MuON': [
                'mup', 'maximal update', 'muon', 'parameterization',
                'newton-schulz', 'spectral'
            ],
            
            # CNN topics (Weeks 5-6)
            'CNN Basics': [
                'cnn', 'conv', 'convolution', 'convolutional', 'kernel', 
                'stride', 'padding', 'filter', 'feature map'
            ],
            'Pooling & Normalization': [
                'pooling', 'max pool', 'average pool', 'downsampling',
                'batch norm', 'layer norm', 'normalization', 'rms norm',
                'data augmentation', 'augment'
            ],
            'ResNets & U-Nets': [
                'resnet', 'residual', 'skip connection', 'u-net', 'unet',
                'fully convolutional', 'fcn', 'dropout'
            ],
            
            # GNN topics (Week 7)
            'Graph Neural Networks': [
                'gnn', 'graph neural', 'graph network', 'node embedding',
                'message passing', 'diffpool', 'graph convolution', 'gcn',
                'adjacency', 'node feature'
            ],
            
            # RNN topics (Weeks 7-8)
            'RNNs & Sequence Models': [
                'rnn', 'recurrent', 'lstm', 'gru', 'hidden state',
                'sequence', 'vanishing gradient', 'exploding gradient',
                'backprop through time', 'bptt', 'weight sharing'
            ],
            
            # Self-supervision (Week 8)
            'Self-Supervised Learning': [
                'self-supervised', 'self supervised', 'contrastive',
                'autoencoder', 'auto-encoder', 'pretext task', 'pretrain',
                'masked', 'reconstruction'
            ],
            
            # State-Space Models (Weeks 8-9)
            'State-Space Models': [
                'state space', 'state-space', 'ssm', 'mamba', 's4',
                'hippo', 'selective state'
            ],
            
            # Attention & Transformers (Weeks 9-10)
            'Attention Mechanisms': [
                'attention', 'self-attention', 'self attention', 
                'multi-head', 'multihead', 'cross attention',
                'query', 'key', 'value', 'qkv'
            ],
            'Transformers': [
                'transformer', 'bert', 'positional encoding', 
                'position embedding', 'layer norm', 'feed forward',
                'encoder decoder', 'decoder only'
            ],
            
            # PEFT & Transfer Learning (Weeks 10-12)
            #'Prompting & In-Context Learning': [
            #    'prompt', 'prompting', 'in-context', 'in context',
            #    'few-shot', 'few shot', 'zero-shot', 'zero shot',
            #    'chain of thought', 'cot'
            #],
            'PEFT & Fine-Tuning': [
                'lora', 'peft', 'fine-tune', 'fine tune', 'finetuning',
                'soft prompt', 'adapter', 'parameter efficient', 'finetune'
            ],
            'Transfer Learning': [
                'transfer learning', 'pretrained', 'pre-trained',
                'domain adaptation', 'feature extraction', 'pretrain'
            ],
            'Meta-Learning': [
                'meta-learning', 'meta learning', 'maml', 'few-shot learning',
                'learn to learn', 'reptile'
            ],
            
            # Generative Models (Weeks 12-14)
            'Generative Models': [
                'generative', 'vae', 'variational', 'autoencoder',
                'diffusion', 'ddpm', 'score matching', 'flow',
                'normalizing flow', 'gan', 'generative adversarial'
            ],
            'Post-Training & RLHF': [
                'post-training', 'post training', 'rlhf', 'dpo',
                'reward model', 'preference', 'alignment', 'instruction tuning'
            ],
            
            # General/Foundational
            'Backpropagation': [
                'backprop', 'backward pass', 'chain rule', 'gradient',
                'derivative', 'jacobian', 'computational graph'
            ],
            'Neural Network Basics': [
                'mlp', 'perceptron', 'activation', 'relu', 'sigmoid',
                'tanh', 'softmax', 'weight', 'bias', 'layer'
            ],
            'Loss Functions & Regularization': [
                'loss', 'cross entropy', 'mse', 'regularization',
                'l1', 'l2', 'weight decay', 'overfitting', 'underfitting'
            ],
        }
        
        # Tool type keywords
        self.tool_keywords = {
            'homework': ['homework', 'hw', 'problem set'],
            'flashcard': ['flashcard', 'flash card', 'anki', 'quizlet'],
            'quiz': ['quiz', 'question generator', 'practice problems', 'practice questions', "exam"],
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
            'ChatGPT': ['gpt', 'chatgpt', 'openai'],
            'Gemini': ['gemini', 'google'],
            'NotebookLM': ['notebooklm', 'notebook lm'],
            'Perplexity': ['perplexity'],
            'Cursor': ['cursor'],
            'Other': []
        }
    
    def extract_topics(self, content: str, post_idx: int = None) -> List[str]:
        """
        Extract course-aligned topic labels for a post using keyword matching.
        
        Args:
            content: Post content
            post_idx: Index of post (unused, kept for backwards compatibility)
            
        Returns:
            List of matched course topics
        """
        # Clean content - remove HTML tags and normalize
        clean_content = re.sub(r'<[^>]+>', ' ', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip().lower()
        
        detected_topics = []
        topic_scores = {}
        
        for topic, keywords in self.course_topics.items():
            # Count keyword matches for this topic
            match_count = 0
            for keyword in keywords:
                # Use word boundary matching for short keywords to avoid false positives
                if len(keyword) <= 3:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    matches = len(re.findall(pattern, clean_content, re.IGNORECASE))
                else:
                    matches = clean_content.count(keyword.lower())
                match_count += matches
            
            if match_count > 0:
                topic_scores[topic] = match_count
        
        # Sort by match count and return top topics (max 3)
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        detected_topics = [topic for topic, score in sorted_topics[:3]]
        
        return detected_topics
    
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
