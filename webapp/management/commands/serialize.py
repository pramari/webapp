from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "serialize an object to jsonjd"

    def add_arguments(self, parser):
        """
        add arguments to the command

        args:
            ID to follow.

        use like this:
            parser.add_argument('serialize', nargs='+', type=int)
        """
        parser.add_argument("slug", nargs="+", type=str)

    def handle(self, *args, **options):
        """
        handle the command

        args:
            args: arguments
            options: options
        """
        for slug in options["slug"]:
            self.stdout.write(f"Serializing {slug}...")

            from webapp.serializers.actor import ActorSerializer
            from webapp.models import Profile

            profile = Profile.objects.get(slug=slug)
            serializer = ActorSerializer(profile.actor)
            print(profile.actor)
            print(serializer.data)
