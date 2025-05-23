import logging
import hashlib
import urllib.parse

from allauth.account.models import EmailAddress  # type: ignore
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist

# from webapp.models import User

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


class ProfileManager(models.Manager):
    """
    Custom Manager for the Profile Model
    """

    def get_queryset(self):
        """
        Custom Queryset for the Profile Model
        """
        return super().get_queryset().filter(public=True)

    def actors(self):
        """
        Return all actors

        .. todo::
            probably tricky
        """
        return self.get_queryset().filter(actor__isnull=False)


class Profile(models.Model):
    """
    Also: ActivityPub Profile
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(null=True, help_text=_("Slug"))

    public = models.BooleanField(
        default=False, help_text=_("Make Profile Profile public?")
    )
    consent = models.BooleanField(
        default=False, help_text=_("Consent to store and use data.")
    )
    dob = models.DateField(
        blank=True, null=True, help_text=_("Date of Birth (DOB)")
    )  # noqa: E501

    publish_to_linkedin = models.BooleanField(default=False)

    gravatar = models.BooleanField(
        default=True, help_text=_("Use Gravatar profile image.")
    )
    bio = models.TextField(blank=True, help_text=_("Short Bio"))

    public_key_pem = models.TextField(blank=True, help_text=_("Public Key"))
    private_key_pem = models.TextField(blank=True, help_text=_("Private Key"))

    USER_ICONS = [
        ("0s", "0-square"),
    ]
    icon = models.CharField(max_length=2, choices=USER_ICONS, default="0s")

    # Other Profiles # Consider
    mastodon = models.URLField(blank=True)

    img = models.ImageField(
        upload_to="mediafiles/user/",
        default="/user/default.png",  # noqa: E501
    )

    ## The following is deprecated and has been moved to the Actor model

    # follows = models.ManyToManyField(
    #     "self", related_name="followed_by", symmetrical=False, blank=True
    # )

    # ap_id = models.CharField(
    #    max_length=255,
    #    blank=True,
    #    help_text=_("ActivityPub ID"),
    #    unique=True,
    # )  # noqa: E501

    @property
    def imgurl(self):
        """
        Return the URL of the profile image.

        First, if the user is not verified, the user will not be allowed
        to have a custom gravatar. Instead, a default image will be used.

        Second, if the user is verified, the user will be allowed to have
        a custom avatar. The user can choose to use a gravatar or a custom
        image.

        .. todo::
            make this work
        """
        size = 80

        if self.user.is_verified:  # noqa: no-member
            email = EmailAddress.objects.get(
                user=self.user, verified=True, primary=True
            )
        else:
            """
            No Image for unverified users
            """
            return "user/default.png"  # noqa: E501

        # construct the url
        if self.gravatar:
            hashvalue = hashlib.md5(
                str(email).lower().encode("utf-8")
            ).hexdigest()  # noqa: E501
            size = urllib.parse.urlencode({"d": email, "s": str(size)})
            return f"https://www.gravatar.com/avatar/{hashvalue}?{size}"
        return staticfiles_storage.url(self.img)

    def __str__(self):
        """
        Default Python Method/Best Practice for String Representation
        """
        return self.user.username  # pylint: disable=E1101

    def save(self, *args, **kwargs):
        """
        Profile.save()

        Create a slug from the username if none is provided.

        see::
          signals.py:createUserProfile, connected to User.post_save
        """
        if not self.slug:
            self.slug = slugify(self.user.username)  # pylint: disable=E1101
        return super().save(*args, **kwargs)  # Call save()

    @property
    def get_absolute_url(self):
        """
        Default Django Method/Best Practice
        Returns the URL of the object-detail view.
        """
        return reverse("profile-detail", args=[str(self.slug)])

    @property
    def actor(self):
        """
        return the actual actor object
        """
        try:
            result = self.actor_set.get()
        except ValueError:
            logger.debug("ValueError with actor %s (will return None)", self)
            result = None
        except ObjectDoesNotExist:
            logger.debug("No actor found for %s (will return None)", self)
            result = None
        return result

    def old_public_key(self, base: str) -> dict[str, str]:
        """
        Return the public key as JSON-LD.

        .. todo::
            refactor this live as part of the actor class
        """
        actorid = f"{self.actor.id}"
        public_key_data = {
            "id": f"{self.actor.keyID}",
            "owner": actorid,
            "publicKeyPem": self.public_key_pem,
        }
        return public_key_data
