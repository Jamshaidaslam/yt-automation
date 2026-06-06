"""
uploader.py — Secure Channel Publisher Engine (v7.3 - DYNAMIC META SYNC)
Khateb Ishq Pipeline & Production Matrix Sync
"""

# ... [KEEP YOUR EXISTING IMPORTS AND CLOUDINARY CONFIG] ...

def upload_all_platforms(
    video_path: str,
    seo: dict,
    thumbnail_path: str = None,
    publish_at: str = None
) -> dict:
    """
    Publisher Engine: 
    - YouTube: Direct Upload with SEO metadata.
    - Meta (FB/IG): Cloudinary-based staging with auto-thumb attachment.
    """
    logger.info(f"Initiating publisher for: {video_path}")
    results = {"youtube": "skipped", "facebook": "skipped", "instagram": "skipped"}

    # Extract dynamic metadata from SEO dictionary
    title     = seo.get("title", "Khateb Ishq Insights")
    desc      = seo.get("description", "")
    hashtags  = seo.get("hashtags", ["#darkpsychology", "#shorts"])
    
    # Ensuring Hashtags string for meta platforms
    full_desc = f"{desc}\n\n" + " ".join(hashtags)
    meta_caption = f"{title}\n\n{full_desc}"

    # 1. YouTube Execution Route
    results["youtube"] = upload_to_youtube(video_path, seo, publish_at=publish_at)

    # 2. Cloudinary Engine for Meta Staging
    cloud_data      = upload_to_cloudinary(video_path, resource_type="video")
    cloudinary_url  = cloud_data["url"]
    cloud_pub_id    = cloud_data["public_id"]

    if not cloudinary_url:
        logger.error("Cloudinary deployment failed — skipping Meta Hooks.")
        return results

    # Process Thumbnail (if passed from media_fetcher)
    cloud_thumb_url = None
    cloud_thumb_id  = None
    if thumbnail_path and os.path.exists(thumbnail_path):
        logger.info(f"Uploading dynamic thumbnail to Cloudinary: {thumbnail_path}")
        td              = upload_to_cloudinary(thumbnail_path, resource_type="image")
        cloud_thumb_url = td["url"]
        cloud_thumb_id  = td["public_id"]

    # 3. Facebook Route Execution
    if META_TOKEN and FB_PAGE_ID:
        results["facebook"] = post_to_facebook_via_url(
            cloudinary_url, cloud_thumb_url, meta_caption
        )

    # 4. Instagram Route Execution
    if META_TOKEN and IG_ACCT_ID:
        results["instagram"] = post_to_instagram_via_url(
            cloudinary_url, cloud_thumb_url, meta_caption
        )

    # 5. Cloudinary Staging Storage Wiping
    if cloud_pub_id or cloud_thumb_id:
        logger.info("Waiting 3 min for Meta processing nodes before storage cleanup...")
        time.sleep(180)
        if cloud_pub_id:
            cleanup_cloudinary(cloud_pub_id, resource_type="video")
        if cloud_thumb_id:
            cleanup_cloudinary(cloud_thumb_id, resource_type="image")

    return results

# ... [REST OF YOUR EXISTING FUNCTIONS (post_to_facebook_via_url, etc) REMAIN AS IS] ...
