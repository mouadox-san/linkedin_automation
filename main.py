import json
import datetime
import os
import requests

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

def upload_image(image_url):
    """
    Downloads an image from a URL, uploads it to LinkedIn, and returns the media asset URN.
    """
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202309"
    }

    # Step 1: Register the upload
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": PERSON_URN,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
    reg_response = requests.post(register_url, headers=headers, json=register_payload)
    if reg_response.status_code != 200:
        print(f"Error registering upload: {reg_response.status_code} {reg_response.text}")
        return None
    
    upload_data = reg_response.json()["value"]
    upload_url = upload_data["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = upload_data["asset"]

    # Step 2: Download the image and upload it
    image_response = requests.get(image_url, stream=True)
    if image_response.status_code != 200:
        print(f"Failed to download image from URL: {image_url}")
        return None

    upload_headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    up_response = requests.put(upload_url, data=image_response.content, headers=upload_headers)
    
    if up_response.status_code != 201 and up_response.status_code != 200:
        print(f"Error uploading image: {up_response.status_code} {up_response.text}")
        return None

    return asset_urn

def post_to_linkedin(content, image_asset_urn=None):
    """
    Posts content to LinkedIn, with an optional image.
    """
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202309"
    }

    share_content = {
        "shareCommentary": {"text": content},
        "shareMediaCategory": "NONE"
    }

    if image_asset_urn:
        share_content["shareMediaCategory"] = "IMAGE"
        share_content["media"] = [{
            "status": "READY",
            "media": image_asset_urn
        }]

    payload = {
        "author": PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": share_content},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"Post response: {response.status_code} {response.text}")

def main():
    today = datetime.date.today().isoformat()
    try:
        with open("posts.json", "r", encoding="utf-8") as f:
            posts = json.load(f)
    except FileNotFoundError:
        print("Error: posts.json not found.")
        return

    for post in posts:
        if post.get("date") == today:
            content = post.get("content", "")
            image_url = post.get("image")
            asset_urn = None

            if image_url:
                print(f"Found image for today's post: {image_url}")
                asset_urn = upload_image(image_url)
            
            if content or asset_urn:
                post_to_linkedin(content, asset_urn)
            else:
                print("No content or image found for today's post.")
            
            break # Exit after finding and processing today's post

if __name__ == "__main__":
    main()
