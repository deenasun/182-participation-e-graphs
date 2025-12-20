import requests
import json
import time
import os
import re
from dotenv import load_dotenv

load_dotenv()

import dotenv
dotenv.load_dotenv()

# Try to import Google Drive API libraries (optional)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import io
    GOOGLE_DRIVE_API_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_API_AVAILABLE = False
    print("[!] Google Drive API libraries not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

ED_COURSE_ID = os.environ.get("ED_COURSE_ID")
ED_API_TOKEN = os.environ.get("ED_API_KEY")
SEARCH_STRING = "Special Participation E"        
OUTPUT_FILE = "ed_posts.json"
ATTACHMENT_DIR = "attachments"

# Google Drive API credentials (optional)
GOOGLE_DRIVE_CREDENTIALS_FILE = os.environ.get("GOOGLE_DRIVE_CREDENTIALS_FILE")  # Path to credentials.json
GOOGLE_DRIVE_TOKEN_FILE = os.environ.get("GOOGLE_DRIVE_TOKEN_FILE", "token.json")  # Path to store/load token
GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Cache for Google Drive service (created once per script run)
_google_drive_service_cache = None

BASE_URL = "https://us.edstem.org/api"

headers = {
    "Authorization": f"Bearer {ED_API_TOKEN}",
    "Content-Type": "application/json"
}

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_google_drive_service():
    """
    Authenticates and returns a Google Drive API service object.
    Uses caching to avoid recreating the service on every call.
    Returns None if authentication fails or credentials are not available.
    """
    global _google_drive_service_cache
    
    # Return cached service if available
    if _google_drive_service_cache is not None:
        return _google_drive_service_cache
    
    if not GOOGLE_DRIVE_API_AVAILABLE:
        return None
    
    if not GOOGLE_DRIVE_CREDENTIALS_FILE or not os.path.exists(GOOGLE_DRIVE_CREDENTIALS_FILE):
        return None
    
    creds = None
    # Load existing token if available
    if os.path.exists(GOOGLE_DRIVE_TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(GOOGLE_DRIVE_TOKEN_FILE, GOOGLE_DRIVE_SCOPES)
        except Exception as e:
            print(f"    [!] Error loading Google Drive token: {e}")
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"    [!] Error refreshing Google Drive token: {e}")
                return None
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_DRIVE_CREDENTIALS_FILE, GOOGLE_DRIVE_SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"    [!] Error authenticating with Google Drive: {e}")
                return None
        
        # Save the credentials for the next run
        try:
            with open(GOOGLE_DRIVE_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"    [!] Error saving Google Drive token: {e}")
    
    try:
        service = build('drive', 'v3', credentials=creds)
        _google_drive_service_cache = service  # Cache the service
        return service
    except Exception as e:
        print(f"    [!] Error building Google Drive service: {e}")
        return None

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

def extract_google_drive_links(content_str):
    """
    Extracts Google Drive links from content and converts them to direct download URLs.
    Returns a list of dictionaries with 'url' (download URL) and 'filename' (inferred).
    """
    # Pattern to match various Google Drive URL formats
    # Matches: drive.google.com/file/d/FILE_ID, drive.google.com/open?id=FILE_ID, etc.
    patterns = [
        r'https?://(?:www\.)?drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'https?://(?:www\.)?drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
        r'https?://(?:www\.)?drive\.google\.com/uc\?id=([a-zA-Z0-9_-]+)',
    ]
    
    file_ids = set()
    for pattern in patterns:
        matches = re.findall(pattern, content_str)
        file_ids.update(matches)
    
    drive_attachments = []
    for file_id in file_ids:
        # Convert to direct download URL
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        drive_attachments.append({
            'url': download_url,
            'filename': f"gdrive_{file_id}.pdf",  # Default to PDF, will verify during download
            'file_id': file_id
        })
    
    return drive_attachments

def download_google_drive_file_via_api(file_id, service):
    """
    Downloads a file from Google Drive using the API (for authenticated files).
    Returns the local path if successful, None otherwise.
    """
    try:
        ensure_dir(ATTACHMENT_DIR)
        
        # Get file metadata to check if it's a PDF and get the filename
        file_metadata = service.files().get(fileId=file_id, fields='name, mimeType').execute()
        filename = file_metadata.get('name', f"gdrive_{file_id}.pdf")
        mime_type = file_metadata.get('mimeType', '')
        
        # Only download PDFs
        if mime_type != 'application/pdf' and not filename.lower().endswith('.pdf'):
            print(f"    [!] Google Drive file {file_id} ({filename}) is not a PDF, skipping...")
            return None
        
        safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).strip()
        if not safe_filename.lower().endswith('.pdf'):
            safe_filename += '.pdf'
        
        local_path = os.path.join(ATTACHMENT_DIR, safe_filename)
        
        print(f"    --> Downloading Google Drive PDF (authenticated): {safe_filename}...")
        
        # Download the file
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(local_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        # Verify it's actually a PDF by checking magic number
        with open(local_path, 'rb') as f:
            first_bytes = f.read(4)
            if not first_bytes.startswith(b'%PDF'):
                print(f"    [!] Downloaded file {safe_filename} is not a PDF, removing...")
                os.remove(local_path)
                return None
        
        return local_path
        
    except Exception as e:
        print(f"    [!] Failed to download Google Drive file {file_id} via API: {e}")
        return None

def download_google_drive_file_public(download_url, file_id):
    """
    Downloads a file from Google Drive using public download URL (for public files).
    Returns the local path if successful, None otherwise.
    """
    try:
        ensure_dir(ATTACHMENT_DIR)
        
        session = requests.Session()
        
        # First, make a non-streaming request to check for virus scan warning
        response = session.get(download_url, allow_redirects=True)
        response.raise_for_status()
        
        # Check if we got a virus scan warning page (for large files)
        content = response.text
        if 'virus scan warning' in content.lower() or 'download anyway' in content.lower():
            # Extract the actual download link from the warning page
            # Google Drive warning pages contain a form with action="/uc?export=download&id=..."
            confirm_pattern = r'href="(/uc\?export=download[^"]*)"'
            confirm_match = re.search(confirm_pattern, content)
            if confirm_match:
                confirm_url = "https://drive.google.com" + confirm_match.group(1)
                # Now make a streaming request for the actual file
                response = session.get(confirm_url, allow_redirects=True, stream=True)
                response.raise_for_status()
            else:
                # If we can't find the confirm link, try the original URL with stream
                response = session.get(download_url, allow_redirects=True, stream=True)
                response.raise_for_status()
        else:
            # Not a warning page, so this might be the actual file
            # Check content type - if it's HTML, it might be an error page
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' in content_type:
                # This is likely an error or access denied page
                print(f"    [!] Google Drive file {file_id} may not be accessible (try using API authentication)")
                return None
            # Make a new streaming request for the actual download
            response = session.get(download_url, allow_redirects=True, stream=True)
            response.raise_for_status()
        
        # Try to get filename from Content-Disposition header
        filename = f"gdrive_{file_id}.pdf"
        content_disposition = response.headers.get('Content-Disposition', '')
        if content_disposition:
            filename_match = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disposition)
            if filename_match:
                filename = filename_match.group(1).strip('"\'')
        
        safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).strip()
        local_path = os.path.join(ATTACHMENT_DIR, safe_filename)
        
        print(f"    --> Downloading Google Drive PDF (public): {safe_filename}...")
        
        # Download the file
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        
        # Verify it's actually a PDF by checking magic number
        with open(local_path, 'rb') as f:
            first_bytes = f.read(4)
            if not first_bytes.startswith(b'%PDF'):
                print(f"    [!] Downloaded file {safe_filename} is not a PDF, removing...")
                os.remove(local_path)
                return None
        
        return local_path
        
    except Exception as e:
        print(f"    [!] Failed to download Google Drive file {file_id} (public): {e}")
        return None

def download_google_drive_file(download_url, file_id):
    """
    Downloads a file from Google Drive. Tries API first (for authenticated files),
    then falls back to public download method.
    Returns the local path if successful, None otherwise.
    """
    # Try API method first if credentials are available
    service = get_google_drive_service()
    if service:
        result = download_google_drive_file_via_api(file_id, service)
        if result:
            return result
        # If API fails, fall back to public method
        print(f"    [!] API download failed, trying public method for {file_id}...")
    
    # Fall back to public download method
    return download_google_drive_file_public(download_url, file_id)

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
    for thread in get_threads(ED_COURSE_ID):
        title = thread.get('title', '') or ''
        # Some threads have content directly, others might need a fetch. 
        # Usually list endpoint has content snippets or full XML.
        body = thread.get('content', '') or ''
        
        if substring_lower in title.lower() or substring_lower in body.lower():
            
            user = thread.get('user', {})
            author_name = user.get('name', 'Anonymous') if user else 'Anonymous'
            
            found_files = extract_attachments_from_xml(body)
            found_drive_links = extract_google_drive_links(body)
            
            downloaded_files = []
            total_attachments = len(found_files) + len(found_drive_links)
            
            if total_attachments > 0:
                print(f"\n[+] Found matching post: '{title}' with {total_attachments} attachment(s)")
            else:
                print(f"\n[+] Found matching post: '{title}' (no attachments)")
            
            # Download regular attachments
            for f in found_files:
                local_path = download_file(f['url'], f['filename'])
                if local_path:
                    downloaded_files.append({
                        'original_filename': f['filename'],
                        'url': f['url'],
                        'local_path': local_path
                    })
            
            # Download Google Drive PDFs
            for drive_file in found_drive_links:
                local_path = download_google_drive_file(drive_file['url'], drive_file['file_id'])
                if local_path:
                    downloaded_files.append({
                        'original_filename': drive_file['filename'],
                        'url': f"https://drive.google.com/file/d/{drive_file['file_id']}",
                        'local_path': local_path
                    })

            post_data = {
                'id': thread.get('id'),
                'number': thread.get('number'),  # Sequential post number shown in UI
                'title': title,
                'author': author_name,
                'date': thread.get('created_at'),
                'content': body,
                'attachments_downloaded': downloaded_files,
                'url': f"https://edstem.org/us/courses/{ED_COURSE_ID}/discussion/{thread.get('id')}"
            }
            
            results.append(post_data)
            count += 1

    print(f"\n[*] Processing complete. Found {count} matching posts.")
    return results

if __name__ == "__main__":
    if ED_API_TOKEN == "YOUR_TOKEN_HERE":
        print("Please update the ED_API_TOKEN and ED_COURSE_ID in the script.")
    else:
        matched_posts = process_threads(SEARCH_STRING)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(matched_posts, f, indent=4, ensure_ascii=False)
            
        print(f"[*] Saved data to {OUTPUT_FILE}")
        print(f"[*] Saved attachments to folder: {ATTACHMENT_DIR}/")
