from django.db import models


class FedIDField(models.URLField):
    """
    A Field that represents a FedID.

    .. seealso::
        Activity Pub <Object Identifiers https://www.w3.org/TR/activitypub/#obj-id>_`

    **id**:
        The object's unique global identifier (unless the object is transient, in which case the id MAY be omitted).

    """
    def __init__(self, *args, **kwargs):
        super(ActorField, self).__init__(*args, **kwargs)
