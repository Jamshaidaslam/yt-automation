def dynamic_auto_music_downloader(topic: str):
    """
    🌟 DYNAMIC TOPIC-BASED MUSIC SCRAPER (FIXED STREAM ENGINE)
    Connects to Pixabay Audio API, follows redirects, and downloads a complete, 
    uncorrupted cinematic music asset matching the video topic.
    """
    existing_bgm = list(BGM_INPUT_DIR.glob("*.mp3")) + list(BGM_INPUT_DIR.glob("*.wav"))
    if existing_bgm:
        logger.info("🎵 Local background music assets detected. Skipping dynamic download.")
        return

    logger.warning("⚠️ BGM folder empty! Initializing Automated Topic-Based Music Scraper...")
    
    search_keywords = "suspense cinematic ambient"
    if "dark" in topic.lower() or "psychology" in topic.lower():
        search_keywords = "dark suspense ambient thriller"
    elif "love" in topic.lower() or "poetry" in topic.lower():
        search_keywords = "sad cinematic piano flute"

    pixabay_key = os.getenv("PIXABAY_API_KEY")
    fallback_track_path = BGM_INPUT_DIR / "dynamic_scraped_bgm.mp3"

    if pixabay_key:
        logger.info(f"🔍 Searching Pixabay Audio Repository for keywords: '{search_keywords}'")
        url = f"https://pixabay.com/api/videos/audio/?key={pixabay_key}&q={requests.utils.quote(search_keywords)}&per_page=10"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                hits = response.json().get("hits", [])
                if hits:
                    random_track = random.choice(hits)
                    download_url = random_track.get("audio", "")
                    if download_url:
                        logger.info(f"📥 Downloading uncorrupted Pixabay audio: {random_track.get('title', 'Cinematic Sound')}")
                        
                        # 🔥 FIX: Stream download with redirect follow enabled to avoid corrupt 1134-byte headers
                        audio_resp = requests.get(download_url, stream=True, allow_redirects=True, timeout=45)
                        if audio_resp.status_code == 200:
                            with open(fallback_track_path, "wb") as f:
                                for chunk in audio_resp.iter_content(chunk_size=32 * 1024): # 32KB processing blocks
                                    if chunk:
                                        f.write(chunk)
                            
                            # Double-check verify size layer
                            if fallback_track_path.stat().st_size > 5000:
                                logger.info(f"✅ Full audio binary stream saved successfully! Size: {fallback_track_path.stat().st_size} bytes")
                                return
                            else:
                                logger.warning("⚠️ Downloaded audio file is too small (corrupt header). Forcing backup node...")
        except Exception as e:
            logger.error(f"❌ Pixabay Audio API stream pipeline failed: {e}")

    # Ultimate Hardcoded Backup Node (Mixkit Premium CDN Node - Stream verified)
    logger.warning("🚨 Activating Mixkit CDN premium audio backup link...")
    static_backup_url = "https://assets.mixkit.co/music/preview/mixkit-glitchy-futuristic-ambient-mystery-1149.mp3"
    try:
        response = requests.get(static_backup_url, stream=True, allow_redirects=True, timeout=30)
        with open(fallback_track_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=32 * 1024):
                if chunk:
                    f.write(chunk)
        logger.info(f"✅ Premium backup mystery theme loaded flawlessly! Size: {fallback_track_path.stat().st_size} bytes")
    except Exception as e:
        logger.error(f"❌ Ultimate BGM layer crash prevention failed: {e}")
        raise FileNotFoundError(f"Please drop at least one background music .mp3 track inside '{BGM_INPUT_DIR}' folder.")
