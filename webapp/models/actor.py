#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4
# pylint: disable=invalid-name

"""
Activitypub models for `Angry Planet Cloud`.

"""
import logging
from django.db import models
from webapp.models.profile import Profile
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class Actor(models.Model):
    """
    Activity Streams 2.0

    Actor
    """

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True
    )

    id = models.CharField(
        max_length=255, primary_key=True, unique=True, blank=False
    )  # noqa: E501
    type = models.CharField(max_length=255, default="Person")
    slug = models.SlugField(null=True, help_text=_("Slug"))
    preferredUsername = models.CharField(max_length=255, blank=True, null=True)

    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )

    class Meta:
        verbose_name = _("Actor (Activity Streams 2.0)")
        verbose_name_plural = _("Actors (Activity Streams 2.0)")
        unique_together = ("id", "type", "profile")

    def __str__(self):
        return self.id
