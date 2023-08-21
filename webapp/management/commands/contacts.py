from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "get all contacts for "

    def add_arguments(self, parser):
        """
        Unused right now.

        use like this:
            parser.add_argument('feeds', nargs='+', type=int)
            parser.add_argument('--force', type=bool, default=False)
        """

    def handle(self, *args, **options):

        from allauth.socialaccount.models import SocialToken, SocialApp, SocialAccount
        from webapp.tasks import getGoogleContact

        accessToken = SocialToken.objects.filter(  # pylint: disable=no-member
            account__user=1,  # hardcoded
            account__provider="google"
        )[0]
        app = SocialApp.objects.filter(provider="Google")[0]

        print(getGoogleContact(accessToken, app))


        app = SocialApp.objects.filter(provider="Hubspot")[0]
        accessToken = SocialAccount.objects.get(  # pylint: disable=no-member
                                                 user_id=1,  # hardcoded
                                                 provider=app
                                                 )
        print(accessToken.extra_data)
        from hubspot import HubSpot

        api_client = HubSpot(access_token=accessToken.extra_data['token'])
        all_contacts = api_client.crm.contacts.get_all()
        print(all_contacts)
