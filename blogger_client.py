"""Shared Blogger API service builder."""
import os
from config import TOKEN_FILE, BLOGGER_SCOPES


def _get_service():
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, BLOGGER_SCOPES)
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
        if creds and creds.valid:
            return build('blogger', 'v3', credentials=creds)
    except Exception:
        pass
    return None
