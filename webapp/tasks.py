from celery import shared_task
from crmeta import getSecret
from pprint import pprint

from django.conf import settings
from django.contrib.auth import get_user_model

import json
import requests

import logging

from allauth.socialaccount.models import SocialToken, SocialApp

from typing import List
from typing import Tuple

logger = logging.getLogger(__name__)

User = get_user_model()


fieldmapping_google_to_hubspot = {
    "Prefix": "Salutation",
    "First Name": "First Name",
    "Last Name": "Last Name",
    "Company": "Associated Company Name",
    "Job Title": "Job Title",
    "Emails": "Primary Email",
    "Phones": "Phone Number",
    "Phones (mobile)": "Mobile Phone",
    "Phones (fax)": "Fax",
    "Websites": "Website URL",
    "Addresses": "Address",
}


@shared_task
def insertContactFromHubspotToGoogle():
    """
    syncContacts from Hubspot to Google

    .. todo::
        Implement
    """
    try:
        import hubspot
        from hubspot.crm.contacts import ApiException
    except ImportError:
        raise NotImplementedError

    api_key = getSecret("pramari-de", "dbdetail", "19").get("KEYS")
    client = hubspot.Client.create(api_key=api_key["HUBSPOT"])

    try:
        api_response = client.crm.contacts.basic_api.get_page(limit=10,
                                                              archived=False)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling basic_api->get_page: %s\n" % e)


@shared_task
def insertContactFromGoogleToHubspot(googleContact):
    """
    syncContacts from Google to HubSpot

    .. todo::
        Implement
    """
    if not settings.HUBSPOT_API_KEY:
        raise NotImplementedError
    hapi = "https://api.hubapi.com/contacts/v1/contact/?hapikey="
    endpoint = f"{hapi}{settings.HUBSPOT_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(
        {
            "properties": [
                {"property": "email", "value": "testingapis@hubspot.com"},
                {"property": "firstname", "value": "test"},
                {"property": "lastname", "value": "testerson"},
                # {
                #  "property": "website", "company", "phone","address", "city",
                # "state", "zip",
                #    "value": "http://hubspot.com"
                #    },
            ]
        }
    )

    r = requests.post(url=endpoint, data=data, headers=headers)
    print(r.text)


@shared_task
def getAppAndAccessToken(
    user: User, provider: str = "google"
) -> Tuple[SocialApp, SocialToken]:
    try:
        app = SocialApp.objects.get(provider=provider)
    except SocialApp.DoesNotExist:
        app = None
    
    try:
        accessToken = SocialToken.objects.get(  # pylint: disable=no-member
            account__user=user, account__provider=app  # provider
        )
    except SocialToken.DoesNotExist:
        accessToken = None

    return (app, accessToken)

@shared_task
def generateProfileKeyPair(
    modeladmin: str,
    request,
    queryset,
    verbose=True
) -> bool:
    """
    """
    from cryptography.hazmat.primitives import (
        serialization as crypto_serialization
    )
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import (
        default_backend as crypto_default_backend
    )
    for user in queryset.all():
        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=2048
        )

        user.profile.private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption()
        ).decode('utf-8')

        user.profile.public_key = key.public_key().public_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        print(type(user.profile.private_key))
        print(user.profile.private_key)
        print(type(user.profile.public_key))
        print(user.profile.public_key)
        user.profile.save()
        user.save()
        user.profile.save()
    return True


@shared_task
def getGoogleContact(
    accessToken: SocialToken,
    googleApp: SocialApp,
    resourceName: str = "people/me",
    googleContact: int = 0,
) -> List:
    from google.oauth2.credentials import Credentials
    from django.utils.timezone import make_naive, is_aware
    from googleapiclient.discovery import build

    expires_at = accessToken.expires_at
    if is_aware(accessToken.expires_at):
        """
        .. todo:
            this is a hack. it converts `expires_at` to the default
            timezone set in `settings.py` for the project.
            However, it should rather use the timezone in which Google
            issued this token. This **MAY** be contained in `access_token`.

            Actually, it seems to be the other way round...
        """
        expires_at = make_naive(accessToken.expires_at)

    creds = Credentials(
        token=accessToken.token,
        refresh_token=accessToken.token_secret,
        expiry=expires_at,  # make_aware to default timezone above
        token_uri="https://oauth2.googleapis.com/token",
        client_id=googleApp.client_id,  # replace with yours
        client_secret=googleApp.secret,
    )

    service = build("people", version="v1", credentials=creds)
    people = service.people()  # pylint: disable=no-member  # E1101
    connections = people.connections()
    contacts = connections.list(
        resourceName=resourceName,
        personFields="addresses,ageRanges,biographies,birthdays,calendarUrls,clientData,coverPhotos,emailAddresses,events,externalIds,genders,imClients,interests,locales,locations,memberships,metadata,miscKeywords,names,nicknames,occupations,organizations,phoneNumbers,photos,relations,sipAddresses,skills,urls,userDefined",
    )
    result = contacts.execute()

    return result.get("connections", [])


@shared_task
def updateGoogleContact(contact: dict):
    """
    """


# @shared_task
# def updateHubspotContact(contact: dict):
    """
    update a contact in crm

    .. input::
      contact details

    .. todo::
        implement
    """

    # logger.error("Implement this!")

@shared_task
def syncPramariToHubspot(contact: dict):
    """
    """
    logger.error("Implement this!")