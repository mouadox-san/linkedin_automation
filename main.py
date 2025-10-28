import json
import datetime
import os
import requests

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
PROFILE_URN = os.getenv("LINKEDIN_PROFILE_URN")  # e.g., "urn:li:person:xxxxxxxx"

def post_to_linkedin(content):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "author": PROFILE_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(response.status_code, response.text)

def main():
    today = datetime.date.today().isoformat()
    with open("posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    for post in posts:
        if post["date"] == today:
            post_to_linkedin(post["content"])

if __name__ == "__main__":
    main()
