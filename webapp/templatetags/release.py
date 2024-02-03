#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(name="release")
def release():
    from webapp import __version__, __date__

    try:
        with open("%s/release" % settings.BASE_DIR, "r") as f:
            return "%s - %s" % (__version__, str(f.read()))
    except IOError:
        return "%s - %s" % (__version__, __date__)
