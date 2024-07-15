from django.db import models


class ActorField(models.URLField):
    def __init__(self, *args, **kwargs):
        super(ActorField, self).__init__(*args, **kwargs)
