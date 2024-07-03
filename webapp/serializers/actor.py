from django.core import serializers

from webapp.models import Actor


if __name__ == "__main__":
    print("This is the actor module")
    print(serializers.serialize("json", Actor.objects.all()))
