import os
import sys
import requests

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

def check_post_status(post_urn):
    """
    Fetches the status of a specific LinkedIn post.
    """
    if not LINKEDIN_ACCESS_TOKEN:
        print("Error: LINKEDIN_ACCESS_TOKEN environment variable not set.")
        return

    # The API endpoint for ugcPosts uses the ID directly, not the full URN
    post_id = post_urn.split(":")[-1]
    url = f"https://api.linkedin.com/v2/ugcPosts/{post_id}"
    
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202309"
    }

    print(f"Querying API for post: {post_urn}")
    response = requests.get(url, headers=headers)

    print(f"Response Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_post.py <post_urn>")
        print("Example: python check_post.py urn:li:share:7388963697706094592")
    else:
        check_post_status(sys.argv[1])
