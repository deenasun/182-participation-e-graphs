"""
Data ingestion pipeline for EECS 182 Post Graph.
Processes EdStem posts, extracts metadata, generates embeddings, and builds graph layouts.
"""

from .pdf_processor import extract_pdf_text, process_attachments
from .embedder import PostEmbedder
from .categorizer import PostCategorizer
from .graph_builder import GraphBuilder

__all__ = [
    'extract_pdf_text',
    'process_attachments',
    'PostEmbedder',
    'PostCategorizer',
    'GraphBuilder',
    'run_ingestion_pipeline'
]

def convert_xml_to_formatted_text(xml_content: str) -> str:
    """
    Convert EdStem XML content to formatted text while preserving structure.
    
    Handles:
    - <paragraph> tags -> newlines
    - <bold> tags -> **bold** (markdown style)
    - <italic> tags -> *italic* (markdown style)
    - <underline> tags -> __underline__ (markdown style)
    - <list> and <list-item> -> bullet points
    - <link> tags -> preserve URLs
    - <break/> -> line breaks
    - <file> tags -> remove (attachments handled separately)
    - Other tags -> remove but preserve content
    """
    if not xml_content:
        return ""
    
    import re
    
    # Remove document wrapper tags
    text = xml_content.replace('<document version="2.0">', '').replace('</document>', '')
    
    # Handle file tags (remove them, attachments are handled separately)
    text = re.sub(r'<file[^>]*/>', '', text)
    
    # Handle break tags -> line break
    text = text.replace('<break/>', '\n')
    text = text.replace('<break />', '\n')
    
    # Handle paragraph tags -> newline (but preserve content)
    # Replace closing paragraph tags with newline first
    text = text.replace('</paragraph>', '\n')
    # Then remove opening paragraph tags
    text = re.sub(r'<paragraph[^>]*>', '', text)
    
    # Handle list items -> bullet points
    text = text.replace('</list-item>', '\n')
    text = re.sub(r'<list-item[^>]*>', '• ', text)
    
    # Handle list tags (remove, but preserve structure)
    text = text.replace('</list>', '\n')
    text = re.sub(r'<list[^>]*>', '', text)
    
    # Handle blockquote tags -> indented block
    text = text.replace('</blockquote>', '\n')
    text = re.sub(r'<blockquote[^>]*>', '\n> ', text)
    
    # Handle heading tags -> bold headers
    text = re.sub(r'</heading[^>]*>', '\n\n', text)
    text = re.sub(r'<heading[^>]*level="(\d+)"[^>]*>', lambda m: '\n' + '#' * int(m.group(1)) + ' ', text)
    text = re.sub(r'<heading[^>]*>', '\n## ', text)
    
    # Handle link tags -> extract URL and text
    def replace_link(match):
        href_match = re.search(r'href="([^"]+)"', match.group(0))
        url = href_match.group(1) if href_match else ''
        # Get text content between tags
        content_match = re.search(r'>([^<]+)</link>', match.group(0))
        link_text = content_match.group(1) if content_match else url
        return f'[{link_text}]({url})' if url else link_text
    
    text = re.sub(r'<link[^>]*>.*?</link>', replace_link, text, flags=re.DOTALL)
    
    # Handle formatting tags (bold, italic, underline)
    text = text.replace('</bold>', '**')
    text = re.sub(r'<bold[^>]*>', '**', text)
    
    text = text.replace('</italic>', '*')
    text = re.sub(r'<italic[^>]*>', '*', text)
    
    text = text.replace('</underline>', '__')
    text = re.sub(r'<underline[^>]*>', '__', text)
    
    # Remove any remaining XML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode XML entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&apos;', "'")
    
    # Normalize whitespace: collapse multiple spaces but preserve newlines
    # Replace multiple spaces with single space (but not newlines)
    lines = text.split('\n')
    normalized_lines = []
    for line in lines:
        # Collapse multiple spaces within a line
        line = re.sub(r'[ \t]+', ' ', line)
        # Remove trailing spaces
        line = line.rstrip()
        normalized_lines.append(line)
    
    # Join lines back, removing empty lines at the end
    text = '\n'.join(normalized_lines)
    text = text.rstrip()
    
    return text

def run_ingestion_pipeline(json_path: str = None, output_path: str = None):
    """
    Main ingestion pipeline - load JSON, process, generate embeddings, compute layouts.
    
    Args:
        json_path: Path to ed_posts.json file. If None, uses default location in the backend directory.
        output_path: Path to save processed_posts.json. If None, uses backend directory.
    """
    import json
    import numpy as np
    from pathlib import Path
    
    # Default paths
    if json_path is None:
        # Expect ed_posts.json to live in the backend directory
        json_path = Path(__file__).parent.parent / 'ed_posts.json'
    
    if output_path is None:
        output_path = Path(__file__).parent.parent / 'processed_posts.json'
    
    print("=" * 60)
    print("EECS 182 Post Graph - Data Ingestion Pipeline")
    print("=" * 60)
    
    print("\nStep 1: Loading posts from JSON...")
    with open(json_path, 'r') as f:
        raw_posts = json.load(f)
    print(f"Found {len(raw_posts)} posts")
    
    # Initialize components
    embedder = PostEmbedder()
    categorizer = PostCategorizer()
    graph_builder = GraphBuilder()
    
    print("\nStep 2: Processing posts...")
    processed_posts = []
    for raw_post in raw_posts:
        # Skip the header post
        if 'Extra Credit Opportunity' in raw_post.get('title', ''):
            continue
            
        # Convert XML content to formatted text while preserving structure
        import re
        content = raw_post.get('content', '')
        content = convert_xml_to_formatted_text(content)
        
        title = raw_post.get('title', '')
        title = convert_xml_to_formatted_text(title)
            
        # Extract basic metadata
        post_data = {
            'ed_post_id': raw_post['id'],
            'ed_post_number': raw_post.get('number'),  # Sequential post number shown in UI
            'title': title,
            'content': content,
            'author': raw_post['author'],
            'date': raw_post['date'],
            'attachment_urls': [att['url'] for att in raw_post.get('attachments_downloaded', [])],
            'attachment_summaries': '',
            'github_url': None,
            'website_url': None,
            'linkedin_url': None,
            'num_reactions': 0,
            'num_replies': 0
        }
        
        # Extract URLs from content using basic regex (use raw content for URL extraction)
        raw_content = raw_post['content']
        github = re.search(r'github\.com/[\w-]+(?:/[\w-]+)?', raw_content)
        # Look for website URLs (excluding github, linkedin, edstem)
        website = re.search(r'https?://(?!github\.com|linkedin\.com|edstem\.org)[\w.-]+\.[\w]+(?:/[\w.-]*)*', raw_content)
        linkedin = re.search(r'linkedin\.com/in/[\w-]+', raw_content)
        
        post_data['github_url'] = github.group(0) if github else None
        post_data['website_url'] = website.group(0) if website else None
        post_data['linkedin_url'] = linkedin.group(0) if linkedin else None
        
        # Process attachments (for now, just note we have them)
        if post_data['attachment_urls']:
            post_data['attachment_summaries'] = f"Attachments: {', '.join([att.get('original_filename', 'file') for att in raw_post.get('attachments_downloaded', [])])}"
        
        processed_posts.append(post_data)
    
    print(f"Processed {len(processed_posts)} posts (excluding header)")
    
    print("\nStep 3: Categorizing posts (extracting course-aligned topics, tools, LLMs)...")
    for i, post in enumerate(processed_posts):
        post['topics'] = categorizer.extract_topics(post['content'])
        post['tools'] = categorizer.extract_tools(post['content'])
        post['llms'] = categorizer.extract_llms(post['content'])
        post['impressiveness_score'] = categorizer.calculate_impressiveness(post)
    
    print("\nStep 4: Generating embeddings...")
    for i, post in enumerate(processed_posts):
        if (i + 1) % 20 == 0:
            print(f"  Generated embeddings for {i + 1}/{len(processed_posts)} posts")
        embeddings = embedder.embed_post(post)
        post.update(embeddings)
    print(f"  Generated embeddings for {len(processed_posts)}/{len(processed_posts)} posts")
    
    print("\nStep 5: Computing graph layouts...")
    layout_data = {}
    cluster_names_data = {}
    
    for view_mode in ['topic', 'tool', 'llm']:
        print(f"  Computing {view_mode} view...")
        
        # Get view-specific embeddings
        emb_key = f'{view_mode}_view_embedding'
        embeddings = np.array([p[emb_key] for p in processed_posts])
        
        # Compute layout
        positions, clusters = graph_builder.compute_layout(embeddings, view_mode)
        
        # Store layout
        for i, post in enumerate(processed_posts):
            post[f'{view_mode}_layout'] = {
                'x': float(positions[i][0]),
                'y': float(positions[i][1]),
                'cluster_id': int(clusters[i])
            }
        
        # Compute cluster names by finding most common labels in each cluster
        cluster_names = {}
        unique_clusters = set(clusters)
        from collections import Counter
        
        for cid in unique_clusters:
            cid_int = int(cid)
            if cid_int == -1:
                cluster_names[cid_int] = "Uncategorized"
                continue
                
            # Get all labels for posts in this cluster
            cluster_posts = [processed_posts[i] for i, cluster_val in enumerate(clusters) if cluster_val == cid]
            
            if view_mode == 'topic':
                labels = [label for p in cluster_posts for label in p.get('topics', [])]
            elif view_mode == 'tool':
                labels = [label for p in cluster_posts for label in p.get('tools', []) if label != 'other']
            else: # llm
                labels = [label for p in cluster_posts for label in p.get('llms', []) if label != 'Other']
            
            if labels:
                most_common = Counter(labels).most_common(1)[0][0]
                cluster_names[cid_int] = most_common
            else:
                cluster_names[cid_int] = f"Cluster {cid_int}"
        
        cluster_names_data[view_mode] = cluster_names
        
        # Compute similarities
        similarities = graph_builder.compute_similarities(embeddings)
        layout_data[f'{view_mode}_similarities'] = similarities
        
        print(f"    Found {len(similarities)} edges above similarity threshold")
    
    print("\nStep 6: Saving processed data...")
    # output_path is now passed as parameter or set to backend/processed_posts.json
    
    # Convert numpy arrays and int64 to native Python types for JSON serialization
    for post in processed_posts:
        for key in ['content_embedding', 'topic_view_embedding', 'tool_view_embedding', 'llm_view_embedding']:
            if key in post:
                post[key] = post[key].tolist()
        
        # Convert numpy int64 to int in layouts
        for view_mode in ['topic', 'tool', 'llm']:
            layout_key = f'{view_mode}_layout'
            if layout_key in post:
                post[layout_key]['cluster_id'] = int(post[layout_key]['cluster_id'])
    
    # Convert similarities to serializable format
    for key in layout_data:
        if key.endswith('_similarities'):
            layout_data[key] = [(int(i), int(j), float(sim)) for i, j, sim in layout_data[key]]
    
    with open(output_path, 'w') as f:
        json.dump({
            'posts': processed_posts,
            'layout_data': layout_data,
            'cluster_names': cluster_names_data
        }, f, indent=2)
    
    print(f"Saved processed data to: {output_path}")
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE - Summary Statistics")
    print("=" * 60)
    print(f"Total posts processed: {len(processed_posts)}")
    print(f"Average impressiveness score: {np.mean([p['impressiveness_score'] for p in processed_posts]):.2f}")
    
    # Count categories
    all_tools = [tool for post in processed_posts for tool in post['tools']]
    all_llms = [llm for post in processed_posts for llm in post['llms']]
    
    from collections import Counter
    tool_counts = Counter(all_tools)
    llm_counts = Counter(all_llms)
    
    print("\nTool distribution:")
    for tool, count in tool_counts.most_common(5):
        print(f"  {tool}: {count}")
    
    print("\nLLM distribution:")
    for llm, count in llm_counts.most_common():
        print(f"  {llm}: {count}")
    
    print("\n" + "=" * 60)
    
    return processed_posts
