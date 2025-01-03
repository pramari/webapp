"""
https://blog.futuresmart.ai/how-to-automate-your-linkedin-posts-using-python-and-the-linkedin-api#heading-steps-for-making-linkedin-api-requests

"""

import requests

api_url = "https://api.linkedin.com/v2/ugcPosts"
access_token = "<your>"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Connection": "Keep-Alive",
    "Content-Type": "application/json",
}

post_body = {
    "author": "urn:li:person:<your_linkedin_id>",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Check out our latest blog post!",
            },
            "shareMediaCategory": "ARTICLE",
            "media": [
                {
                    "status": "READY",
                    "description": {
                        "text": "Read our latest blog post about LinkedIn API!",
                    },
                    "originalUrl": "<your_blog_post_url>",
                },
            ],
        },
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC",
    },
}


def send_to_channel(sender, **kwargs):
    instance = kwargs["instance"]
    user = instance.owner

    """
    .. todo::
        Figure out which channel `user` wants to send the message to.
        For the time being, assume that the user wants to send the message to LinkedIn.
        At least, when the channel is connected to `user`.
    """


if __name__ == "__main__":
    response = requests.post(api_url, headers=headers, json=post_body)
    if response.status_code == 201:
        print("Post successfully created!")
    else:
        print(
            f"Post creation failed with status code {response.status_code}: {response.text}"
        )
