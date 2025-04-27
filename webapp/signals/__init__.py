#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# noqa: E501

"""
.. module:: signals

"""

import logging

from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.utils.translation import gettext as _

from .linkedin import postToLinkedIn

__all__ = [
    "User",
    "signalLogger",
    "signalHandler",
    "createUserProfile",
    "postToLinkedIn",
]


logger = logging.getLogger(__name__)

action = Signal()
"""Action signal."""

User = get_user_model()
"""User model."""


def signalLogger(sender, **kwargs):
    """
    Generic signal logger.

    This function logs the request and any additional keyword arguments.


    :param request: The request object.
    :param \*\*kwargs: Additional keyword arguments.  # noqa: W605
    """
    logger.error(sender)
    logger.error(kwargs)


async def send_to_social(sender, **kwargs):
    """
    Callback function to send a message to a channel.
    """

    await postToLinkedIn(sender, **kwargs)
    logger.debug("Sent to LinkedIn")


def emailConfirmed(request, emailaddress, **kwargs):
    """ """
    from allauth.account.models import EmailAddress

    email = EmailAddress.objects.get(email=emailaddress)
    from django.contrib.auth.models import Group

    confirmed, created = Group.objects.get_or_create(name="confirmed email")
    email.user.groups.add(confirmed)


def checkEmailVerified(sender, request, **kwargs):
    verified = request.user.emailaddress_set.filter(verified=True).exists()
    if not verified:
        from django.contrib import messages

        messages.error(_("Please verify your email!"))
        return False



"""
@receiver(user_logged_in, sender=User)
def userLogin(sender, request, user, signal, *args, **kwargs):
    pass
"""


def createUserProfile(sender, instance, created, **kwargs):
    """
    create a new profile instance for every user created.

    leverage `Django Signals` for this purpose.
    """
    if created:  # not user.profile:
        from webapp.models import Profile

        assert isinstance(instance, User)

        Profile.objects.create(user=instance, slug=instance.username)

        logger.debug("Created profile for %s", instance.username)
