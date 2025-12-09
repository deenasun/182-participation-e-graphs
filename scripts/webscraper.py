import requests
import json
import time
import os
import re

COURSE_ID = 84647
API_TOKEN = os.environ.get("ED_API_KEY")
SEARCH_STRING = "Special Participation E"        
OUTPUT_FILE = "ed_posts.json"
ATTACHMENT_DIR = "attachments"   

BASE_URL = "https://us.edstem.org/api"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_file(url, filename):
    """
    Downloads a file from the given URL and saves it to ATTACHMENT_DIR.
    Returns the local path if successful, None otherwise.
    """
    try:
        ensure_dir(ATTACHMENT_DIR)
        
        safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).strip()
        local_path = os.path.join(ATTACHMENT_DIR, safe_filename)
        
        
        print(f"    --> Downloading: {safe_filename}...")
        
        # EdStem file URLs (static.us.edusercontent.com) usually don't need headers, 
        # but passing them doesn't hurt.
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
        return local_path
    except Exception as e:
        print(f"    [!] Failed to download {filename}: {e}")
        return None

def extract_attachments_from_xml(content_str):
    """
    Uses Regex to find <file url="..." filename="..." /> tags in the XML content.
    """
    # Regex pattern to capture url and filename attributes
    # Look for <file followed by attributes until closing />
    pattern = r'<file\s+url="([^"]+)"\s+filename="([^"]+)"\s*/>'
    matches = re.findall(pattern, content_str)
    
    attachments = []
    for url, filename in matches:
        attachments.append({
            'url': url,
            'filename': filename
        })
    return attachments

def get_threads(course_id):
    offset = 0
    limit = 30
    print(f"[*] Starting scrape for course {course_id}...")

    while True:
        url = f"{BASE_URL}/courses/{course_id}/threads"
        params = {"limit": limit, "offset": offset, "sort": "new"}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            threads = data.get('threads', [])
            
            if not threads:
                break
            
            for thread in threads:
                yield thread
            
            offset += len(threads)
            print(f"    Fetched {offset} threads so far...", end='\r')
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"\n[!] Error fetching threads: {e}")
            break

def process_threads(substring):
    results = []
    substring_lower = substring.lower()
    
    count = 0
    for thread in get_threads(COURSE_ID):
        title = thread.get('title', '') or ''
        # Some threads have content directly, others might need a fetch. 
        # Usually list endpoint has content snippets or full XML.
        body = thread.get('content', '') or ''
        
        if substring_lower in title.lower() or substring_lower in body.lower():
            
            user = thread.get('user', {})
            author_name = user.get('name', 'Anonymous') if user else 'Anonymous'
            
            found_files = extract_attachments_from_xml(body)
            
            downloaded_files = []
            if found_files:
                print(f"\n[+] Found matching post: '{title}' with {len(found_files)} attachment(s)")
                for f in found_files:
                    local_path = download_file(f['url'], f['filename'])
                    if local_path:
                        downloaded_files.append({
                            'original_filename': f['filename'],
                            'url': f['url'],
                            'local_path': local_path
                        })
            else:
                pass

            post_data = {
                'id': thread.get('id'),
                'title': title,
                'author': author_name,
                'date': thread.get('created_at'),
                'content': body,
                'attachments_downloaded': downloaded_files,
                'url': f"https://edstem.org/us/courses/{COURSE_ID}/discussion/{thread.get('id')}"
            }
            
            results.append(post_data)
            count += 1

    print(f"\n[*] Processing complete. Found {count} matching posts.")
    return results

if __name__ == "__main__":
    if API_TOKEN == "YOUR_TOKEN_HERE":
        print("Please update the API_TOKEN and COURSE_ID in the script.")
    else:
        matched_posts = process_threads(SEARCH_STRING)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(matched_posts, f, indent=4, ensure_ascii=False)
            
        print(f"[*] Saved data to {OUTPUT_FILE}")
        print(f"[*] Saved attachments to folder: {ATTACHMENT_DIR}/")
