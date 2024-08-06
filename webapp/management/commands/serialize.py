from django.core.management.base import BaseCommand
from rest_framework.renderers import JSONRenderer

testactor = {"@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/security/v1"], "id": "https://pramari.de/@andreas", "type": "Person", "name": "andreas", "preferredUsername": "andreas", "summary": "planet earth.", "inbox": "https://pramari.de/@andreas/inbox", "outbox": "https://pramari.de/accounts/andreas/outbox", "followers": "https://pramari.de/accounts/andreas/followers", "following": "https://pramari.de/accounts/andreas/following", "liked": "https://pramari.de/accounts/andreas/likes", "publicKey": {"id": "https://pramari.de/@andreas#main-key", "owner": "https://pramari.de/@andreas", "publicKeyPem": "-----BEGIN PUBLIC KEY-----\r\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnqWjWxU5kKR1rpBjHXwl\r\nRKzfkrjlukb1a4sCSnoIM9UDi8SoXQ7k41A+PkM2iQBW9Xk15aVRSLYAn/EJsOBT\r\n3zVOe0QceeGFf0pxfxFY0mAoGMzfly/DUYNqvGciyyeE1POVizsCduU0HWIX7+ga\r\npBrzHQEp0drZtH6VXoa4Y+Wi8YHmAX+k/r8LBLIX7Ryfm9dD1UfvbqckWgaby5Eu\r\nSic4rpjGr24qE+hzBSi5vVGIc7Mb4bztIsyHHjxl7sbkXldk9Uo/b3XlJ9iTO6ZA\r\nCR+YPr+Zk9R4DyITS9yRsyb0FWtSO33ZC9fES7YBz+p8rYH83K7+v0gs8Sl7VUwX\r\nhwIDAQAB\r\n-----END PUBLIC KEY-----"}, "image": {"type": "Image", "mediaType": "image/jpeg", "url": "https://www.gravatar.com/avatar/ea40827a8e13e6ed3c434abec73f40e5?d=andreas%40neumeier.org&s=80"}, "icon": {"type": "Image", "mediaType": "image/png", "url": "0s"}}

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
        parser.add_argument("id", nargs="+", type=str)

    def handle(self, *args, **options):
        """
        handle the command

        args:
            args: arguments
            options: options
        """
        for id in options["id"]:
            self.stdout.write(f"Serializing {id}...")

            from webapp.serializers.actor import ActorSerializer
            from webapp.models import Actor
            from pyld import jsonld

            profile = Actor.objects.filter(id=id)
            serializer = ActorSerializer(profile, many=True)
            jsld = jsonld.expand(testactor)

            print(profile)
            print(repr(serializer))
            print(serializer.data)
            print(jsld)
            print(JSONRenderer().render(serializer.data))
