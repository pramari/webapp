from django.core.management.base import BaseCommand


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
        from allauth.socialaccount.models import SocialToken, SocialApp
        from webapp.tasks import getGoogleContact

        accessToken = SocialToken.objects.filter(  # pylint: disable=no-member
            account__user=1, account__provider="google"  # hardcoded
        )[0]
        app = SocialApp.objects.filter(provider="Google")[0]

        print(getGoogleContact(accessToken, app))
