# Google Drive API Setup Guide

This guide explains how to set up Google Drive API authentication to download restricted files from Google Drive.

## Why You Need This

If Google Drive files are restricted to your school's domain or require authentication, you'll need to set up Google Drive API credentials. The scraper will automatically try the API method first, then fall back to public downloads if authentication isn't available.

## Setup Steps

### 1. Create Google Cloud Project and Enable Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Google Drive API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

### 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" (unless you have a Google Workspace account)
   - Fill in the required fields (app name, user support email, etc.)
   - Add your email as a test user
4. For the OAuth client:
   - Application type: **Desktop app**
   - Name: "EECS 182 Scraper" (or any name)
5. Download the credentials JSON file
6. Save it as `credentials.json` in the `backend/` directory

### 3. Set Environment Variables

Add to your `.env` file:

```bash
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_TOKEN_FILE=token.json
```

Or set them as environment variables:

```bash
export GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
export GOOGLE_DRIVE_TOKEN_FILE=token.json
```

### 4. First-Time Authentication

When you run the scraper for the first time with credentials:

1. A browser window will open
2. Sign in with your **school Google account** (the one that has access to the restricted files)
3. Grant permissions to access Google Drive
4. The token will be saved to `token.json` for future use

### 5. Install Required Packages

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## How It Works

- **With credentials**: The scraper uses Google Drive API to download files (works for restricted files)
- **Without credentials**: The scraper falls back to public download URLs (only works for public files)
- **Automatic fallback**: If API download fails, it tries the public method

## Troubleshooting

- **"Access denied" errors**: Make sure you're signed in with a Google account that has access to the files
- **"Token expired"**: The token will automatically refresh, but if it fails, delete `token.json` and re-authenticate
- **"File not found"**: The file might not be accessible with your current account, or the file ID might be incorrect

## Security Notes

- **Never commit** `credentials.json` or `token.json` to git (they're in `.gitignore`)
- Keep your credentials file secure
- The token file contains refresh tokens - treat it as sensitive

