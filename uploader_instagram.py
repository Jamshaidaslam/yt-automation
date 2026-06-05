"""
uploader_instagram.py — Elite Meta Graph API Reels Publisher
"""
import time
import requests

def upload_to_instagram(video_url, caption, instagram_account_id, access_token):
    print("📸 Initializing Meta Graph API Container Protocol for Reels...")
    if not instagram_account_id or not access_token:
        print("⚠️ Meta credentials missing. Skipping Instagram upload node.")
        return None

    try:
        base_url = f"https://graph.facebook.com/v19.0/{instagram_account_id}"
        container_url = f"{base_url}/media"
        
        payload = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': caption,
            'access_token': access_token
        }
        
        response = requests.post(container_url, data=payload).json()
        if 'id' not in response:
            print(f"❌ Meta Container initialization failed: {response}")
            return None
            
        container_id = response['id']
        print(f"⚙️ Container created successfully. ID: {container_id}. Awaiting Meta processing...")
        
        status_url = f"https://graph.facebook.com/v19.0/{container_id}"
        status_payload = {'fields': 'status_code', 'access_token': access_token}
        
        for check in range(15):
            time.sleep(20)
            status_res = requests.get(status_url, params=status_payload).json()
            status_code = status_res.get('status_code', 'ERROR')
            print(f"⏳ Verification cycle {check+1}: Status is [{status_code}]")
            
            if status_code == 'FINISHED':
                break
            elif status_code == 'ERROR':
                print(f"❌ Meta Video Processing pipeline failed: {status_res}")
                return None
        else:
            print("❌ Meta container processing timeout exceeded.")
            return None

        publish_url = f"{base_url}/media_publish"
        publish_payload = {
            'creation_id': container_id,
            'access_token': access_token
        }
        
        final_res = requests.post(publish_url, data=publish_payload).json()
        if 'id' in final_res:
            print(f"🚀 Success! Reel is now LIVE on Instagram. Media ID: {final_res['id']}")
            return final_res['id']
        else:
            print(f"❌ Execution failed during publish node: {final_res}")
            return None
    except Exception as e:
        print(f"❌ Instagram upload node failed: {e}")
        return None
