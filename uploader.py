"""
uploader.py — Secure Channel Publisher Engine
AI Dark Realities · Short-Form Video Pipeline
──────────────────────────────────────────────
"""

import json
import logging
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from tenacity import retry, stop_after_attempt, wait_exponential

import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def _get_youtube_service():
    """
    Authenticates and constructs the YouTube API service using tight scopes.
    """
    creds = None
    # Read client secret config from GitHub environment strings
    client_secret_
