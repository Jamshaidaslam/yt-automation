"""
uploader_youtube.py — Production Grade YouTube Shorts API Pipeline
"""
import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

def upload_to_youtube(video_path, title, description, tags):
    print("🚀 Initializing YouTube Shorts Secure API Node...")
    
    if not os.path.exists("token.pickle"):
        print("⚠️ token.pickle missing. Skipping YouTube upload node.")
        return None

    try:
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
            
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=credentials
        )

        if "#Shorts" not in title:
            title += " #Shorts"

        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags,
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        
        print(f"📦 Uploading binary matrix stream to YouTube: {video_path}")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"📊 YouTube Upload progress: {int(status.progress() * 100)}%")
                
        print(f"✅ Successfully Published to YouTube! Video ID: {response['id']}")
        return response['id']
    except Exception as e:
        print(f"❌ YouTube upload node failed: {e}")
        return None
