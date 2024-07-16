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

from webapp.models import User

logger = logging.getLogger(__name__)


class Profile(models.Model):
    """
    Also: ActivityPub Profile
    """

    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(null=True, help_text=_("Slug"))

    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )

    public = models.BooleanField(
        default=False, help_text=_("Make Profile Profile public?")
    )
    consent = models.BooleanField(
        default=False, help_text=_("Consent to store and use data.")
    )
    dob = models.DateField(
        blank=True, null=True, help_text=_("Date of Birth (DOB)")
    )  # noqa: E501
    gravatar = models.BooleanField(
        default=True, help_text=_("Use Gravatar profile image.")
    )
    bio = models.TextField(blank=True, help_text=_("Short Bio"))

    ap_id = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("ActivityPub ID"),
        unique=True,
    )  # noqa: E501

    # key_id = models.CharField(
    #    max_length=255, blank=True, help_text=_("Key ID"), unique=True
    # )  # noqa: E501
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
        default="https://storage.cloud.google.com/media.pramari.de/user/default.png",  # noqa: E501
    )

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

        # Set your variables here
        if self.user.is_verified:  # noqa: no-member
            email = EmailAddress.objects.get(
                user=self.user, verified=True, primary=True
            )
        else:
            return "https://storage.cloud.google.com/media.pramari.de/user/default.png"  # noqa: E501

        # construct the url
        if self.gravatar is False:
            return staticfiles_storage.url(self.img)
        else:
            hashvalue = hashlib.md5(
                str(email).lower().encode("utf-8")
            ).hexdigest()  # noqa: E501
            size = urllib.parse.urlencode({"d": email, "s": str(size)})
            return f"https://www.gravatar.com/avatar/{hashvalue}?{size}"

    def __str__(self):
        """
        Default Python Method/Best Practice for String Representation
        """
        return self.user.username  # pylint: disable=E1101

    def notsave(self, *args, **kwargs):
        """
        Profile.save()

        Create a slug from the username if none is provided.
        
        see::
          signals.py:createUserProfile
        """
        if not self.slug:
            self.slug = slugify(self.user.username)  # pylint: disable=E1101
        if not self.ap_id:  # and self.user.is_verified:
            self.ap_id = f"https://pramari.de/@{self.slug}"
        result = super().save(*args, **kwargs)  # Call save()
        if not self.actor:
            from webapp.models import Actor

            Actor.objects.create(
                profile=self,
                id=self.slug,
                type="Person",
            )
        return result

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

    @property
    def get_actor_url(self):
        """
        Return the URL of the actor.
        Activity Streams 2.0

        .. todo::
            This is not the same as `get_absolute_url`, but the actor ID,
            that is stored in self.ap_id
            Currently only the `actor-view` does use this.
        """

        # return self.ap_id
        view = reverse("actor-view", args=[str(self.slug)])
        return f"{view}"

    @property
    def get_inbox_url(self):
        """
        Return the URL of the inbox.

        """
        return reverse(
            "profile-inbox",
            args=[self.slug],
        )

    @property
    def get_outbox_url(self):
        """
        Return the URL of the outbox.
        """
        return reverse(
            "profile-outbox",
            args=[self.slug],
        )

    @property
    def get_followers_url(self):
        """
        Return the URL of the followers.
        """
        return reverse(
            "profile-followers",
            args=[self.slug],
        )

    @property
    def get_following_url(self):
        """
        Return the URL of the following.
        """
        return reverse(
            "profile-following",
            args=[self.slug],
        )

    @property
    def get_key_id(self) -> str:
        """
        Return the key id.
        """
        return f"{self.ap_id}#main-key"

    def get_public_key(self, base: str) -> dict[str, str]:
        """
        Return the public key as JSON-LD.
        """
        actorid = f"{self.get_actor_url}"
        public_key_data = {
            "id": f"{self.get_key_id}",
            "owner": actorid,
            "publicKeyPem": self.public_key_pem,
        }
        return public_key_data

        #   @property
        #   def activities(self) -> list:
        """
        Return all activities of this profile.

        .. todo::
            Implement this.
        """

    #    return Action.objects.filter(actor=self)
