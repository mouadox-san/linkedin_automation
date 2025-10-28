# LinkedIn Auto Poster

This project automates posting content, including text and images, to your LinkedIn personal profile using GitHub Actions.

## ✨ Features

- **Automated Posting:** Schedule posts to go out daily via GitHub Actions cron jobs.
- **Manual Trigger:** Manually run the posting workflow whenever needed.
- **Content Management:** Define your posts (text, image, source link) in a simple `posts.json` file.
- **Image Support:** Uploads local images stored in your repository directly to LinkedIn.
- **Personal Profile Posting:** Configured to post to your LinkedIn personal profile.

## 🚀 Setup Guide

Follow these steps to get your LinkedIn Auto Poster up and running.

### 1. Prerequisites

- A GitHub account.
- A LinkedIn account.
- A LinkedIn Developer Application.
- Basic understanding of Git and GitHub Actions.

### 2. LinkedIn Developer App Configuration

1.  **Create a LinkedIn App:** Go to the [LinkedIn Developer Portal](https://developer.linkedin.com/) and create a new application.
2.  **Add Product:** In your app's dashboard, navigate to the **Products** tab and add the **"Share on LinkedIn"** product.
3.  **Configure OAuth 2.0 Scopes:** Go to the **Auth** tab of your app.
    - Ensure the following scope is added:
        - `w_member_social`: Allows your app to create posts on your behalf.
    - *(Optional: If you ever want to use tools like `check_post.py` to read post statuses, you would also need `r_member_social`.)*
4.  **Generate an Access Token:** Obtain a long-lived OAuth 2.0 access token for your personal profile. This token must be generated with the `w_member_social` scope (and `r_member_social` if you added it).
    - *Note: LinkedIn access tokens have an expiration. You will need to refresh or re-generate them periodically.*

### 3. GitHub Repository Setup

1.  **Clone this Repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/linkedin_automation.git
    cd linkedin_automation
    ```
2.  **How to Find Your LinkedIn Person URN (via Postman)**

    Your LinkedIn Person URN (e.g., `urn:li:person:XXXXXXXXX`) uniquely identifies your LinkedIn profile. Here’s a simple step-by-step guide to obtain it using Postman and your LinkedIn app credentials:

    1.  **Open Postman** and create a new request.
    2.  Go to the **Authorization** tab and select:
        -   **Type:** OAuth 2.0
    3.  Then click **“Get New Access Token.”**
    4.  In the popup window, fill in the following details:
        -   **Token Name:** `LinkedIn`
        -   **Auth URL:** `https://www.linkedin.com/oauth/v2/authorization`
        -   **Access Token URL:** `https://www.linkedin.com/oauth/v2/accessToken`
        -   **Client ID:** (your LinkedIn app’s Client ID)
        -   **Client Secret:** (your LinkedIn app’s Client Secret)
        -   **Scope:** `openid profile email w_member_social`
        -   **Grant Type:** `Authorization Code`
        -   **Callback URL:** `https://www.linkedin.com/developers/tools/oauth/redirect`
    5.  Click **“Get New Access Token.”**
    6.  A LinkedIn login page will appear — log in and authorize the app.
    7.  Once successful, Postman will automatically retrieve your Access Token and ID Token.
    8.  Copy the `id_token` value returned by LinkedIn (it’s a long string of letters and numbers separated by dots, like a JWT).
    9.  Visit [https://jwt.io](https://jwt.io) (a safe online JWT decoder).
    10. Paste your `id_token` in the left-hand field.
    11. On the right-hand side, you’ll see a decoded JSON object.
    12. Look for the field `"sub"` — it should look like this:
        ```json
        "sub": "urn:li:person:XXXXXXXX"
        ```
        ✅ That value is your LinkedIn Person URN.

    Copy it and paste it into your GitHub repository secrets as:

    `LINKEDIN_PERSON_URN = urn:li:person:XXXXXXXX`

3.  **Set up GitHub Secrets:**
    - In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**.
    - Add the following repository secrets:
        -   `LINKEDIN_ACCESS_TOKEN`: Paste your LinkedIn OAuth 2.0 access token here.
        -   `LINKEDIN_PERSON_URN`: This is your LinkedIn personal URN, obtained from the steps above.

### 4. Local Project Setup

1.  **Create `images` Folder:** In the root of your project directory, create a new folder named `images`.
    ```bash
    mkdir images
    ```
2.  **Add Images:** Place your image files (e.g., `my_radiology_image.jpg`, `another_image.png`) into this `images` folder.
3.  **Update `posts.json`:**
    - Open the `posts.json` file in your project.
    - This file defines the content and schedule for your posts.
    - Each entry is a JSON object with `date`, `content`, `image`, and `source_link`.
    - **`date`**: The date the post should go out (e.g., `"2025-10-28"`).
    - **`content`**: The text content of your post.
    - **`image`**: The **local path** to your image file within the `images` folder (e.g., `"images/my_radiology_image.jpg"`).
    - **`source_link`**: A URL to the source of your news or topic.

    Example `posts.json` entry:
    ```json
    {
      "date": "2025-10-28",
      "content": "Your amazing post content here!",
      "image": "images/your_image_name.png",
      "source_link": "https://www.your-source.com"
    }
    ```

## ⚙️ How to Use

1.  **Update Content:** Modify `posts.json` with your desired posts and ensure your images are in the `images` folder.
2.  **Commit and Push:** Push your changes to your GitHub repository.
    ```bash
    git add posts.json images/
    git commit -m "Update: New posts and images"
    git push
    ```
3.  **Run Workflow:**
    - The workflow is scheduled to run daily at 08:00 UTC.
    - You can also trigger it manually:
        - Go to the **Actions** tab in your GitHub repository.
        - Select the "LinkedIn Auto Poster" workflow.
        - Click "Run workflow" on the right side.

4.  **Check Logs:** Monitor the workflow run in the GitHub Actions tab to ensure it completes successfully. Look for `Post response: 201` in the logs.

## ⚠️ Troubleshooting

-   **`403 ACCESS_DENIED`**: Check your `LINKEDIN_ACCESS_TOKEN` and ensure your LinkedIn app has the correct `w_member_social` scope.
-   **`File not found` for image**: Verify the path in `posts.json` matches the actual file name and location in the `images` folder (case-sensitive).
-   **Post not appearing on LinkedIn**: Ensure the workflow ran successfully (check logs for `201` response). There might be a slight delay on LinkedIn's side, or content moderation might be in effect.
-   **`xargs` or quoting errors**: Ensure your `posts.json` content doesn't have unescaped special characters that could break shell commands. The current workflow is designed to handle most common cases.

## 💡 Future Enhancements

-   Add error notifications (e.g., email, Slack) for failed posts.
-   Implement a mechanism to track already posted content to prevent accidental re-posts.
-   Support posting to LinkedIn Pages (organizations) by switching the URN and scope.
-   More dynamic content generation.
