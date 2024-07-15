#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf8
"""
schema.py

Currently unused.  This file is a placeholder for a future implementation
https://github.com/digitalbazaar/pyld

"""

from django.utils.translation import gettext as _

# https://www.w3.org/TR/activitystreams-vocabulary/#actor-types

# https://www.w3.org/TR/activitystreams-vocabulary/#activity-types

ACTOR_TYPES = {
    "Application": _("Application"),
    "Group": _("Group"),
    "Organization": _("Organization"),
    "Person": _("Person"),
    "Service": _("Service"),
}

ACTIVITY_TYPES = {
    "accept": _("Accept"),
    "add": _("Add"),
    "announce": _("Announce"),
    "arrive ": _("Arrive"),
    "block": _("Block"),
    "create": _("Create"),
    "delete": _("Delete"),
    "dislike": _("Dislike"),
    "flag": _("Flag"),
    "follow": _("Follow"),
    "ignore": _("Ignore"),
    "invite": _("Invite"),
    "join": _("Join"),
    "leave": _("Leave"),
    "like": _("Like"),
    "listen": _("Listen"),
    "move": _("Move"),
    "offer": _("Offer"),
    "question": _("Question"),
    "reject": _("Reject"),
    "read": _("Read"),
    "remove": _("Remove"),
    "tentativereject": _("TentativeReject"),
    "tentativeaccept": _("TentativeAccept"),
    "travel": _("Travel"),
    "undo": _("Undo"),
    "update": _("Update"),
    "view": _("View"),
}

context = {
    "@context": "https://www.w3.org/ns/activitystreams",
}

# EOF
