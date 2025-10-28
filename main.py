import json
import datetime
import os
import requests
import sys

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

def upload_image(local_image_path):
    """
    Uploads a local image file to LinkedIn and returns the media asset URN.
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

    # Step 2: Read the local image file and upload it
    try:
        with open(local_image_path, "rb") as f:
            image_data = f.read()
    except FileNotFoundError:
        print(f"Error: Local image file not found at {local_image_path}")
        return None

    upload_headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    up_response = requests.put(upload_url, data=image_data, headers=upload_headers)
    
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

def get_post_data_for_today():
    """
    Reads posts.json and returns content and image_url for today's post.
    """
    today = datetime.date.today().isoformat()
    try:
        with open("posts.json", "r", encoding="utf-8") as f:
            posts = json.load(f)
    except FileNotFoundError:
        print("Error: posts.json not found.")
        return None, None

    for post in posts:
        if post.get("date") == today:
            return post.get("content", ""), post.get("image")
    return None, None


if __name__ == "__main__":
    # This part will be executed when called from GitHub Actions
    # It expects content and optionally a local image path as arguments
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "get_data":
            content, local_image_path = get_post_data_for_today()
            print(f"CONTENT_TO_POST:::{content}")
            print(f"LOCAL_IMAGE_PATH:::{local_image_path}")
        elif action == "post":
            content = sys.argv[2]
            local_image_path = sys.argv[3] if len(sys.argv) > 3 else None
            
            asset_urn = None
            if local_image_path and os.path.exists(local_image_path):
                print(f"Uploading local image: {local_image_path}")
                asset_urn = upload_image(local_image_path)
            elif local_image_path:
                print(f"Warning: Local image path provided but file not found: {local_image_path}")

            if content or asset_urn:
                post_to_linkedin(content, asset_urn)
            else:
                print("No content or image asset to post.")
        else:
            print("Invalid action. Use 'get_data' or 'post'.")
    else:
        print("Usage: python main.py <action> [args]")
        print("  For getting data: python main.py get_data")
        print("  For posting: python main.py post \"<content>\" [local_image_path]")