"""
https://blog.futuresmart.ai/how-to-automate-your-linkedin-posts-using-python-and-the-linkedin-api#heading-steps-for-making-linkedin-api-requests

"""

import requests
from django.contrib.auth import get_user_model
from webapp.tasks import getAppAndAccessToken


def postToLinkedIn(linkedInID: str, shareText: str, contentUrl: str, accessToken: str):
    api_url = "https://api.linkedin.com/v2/ugcPosts"

    headers = {
        "Authorization": f"Bearer {accessToken}",
        "Connection": "Keep-Alive",
        "Content-Type": "application/json",
    }

    post_body = {
        "author": f"urn:li:person:{linkedInID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": f"{shareText}",
                },
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": "Read our latest blog post about LinkedIn API!",
                        },
                        "originalUrl": f"{contentUrl}",
                    },
                ],
            },
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC",
        },
    }
    response = requests.post(api_url, headers=headers, json=post_body)
    if response.status_code == 201:
        print("Post successfully created!")
    else:
        print(
            f"Post creation failed with status code {response.status_code}: {response.text}"
        )


def send_to_channel(sender, instance, channel: str, **kwargs):
    """
    .. todo::
        Figure out which channel `user` wants to send the message to.
        For the time being, assume that the user wants to send the message to LinkedIn.
        At least, when the channel is connected to `user`.
    """

    user = instance.owner

    if user.social_auth.exists() and user.profile.publish_to_linkedin:
        app, access_token = getAppAndAccessToken(user, channel)
        postToLinkedIn(
            linkedInID=app.social_auth.get(provider="linkedin-oauth2").uid,
            shareText=instance.title,
            contentUrl=instance.get_absolute_url(),
            accessToken=access_token,
        )


if __name__ == "__main__":
    User = get_user_model()
    user = User.objects.first()
    from pages.models import Page

    page = Page.objects.filter(owner=user).first()
    send_to_channel()
