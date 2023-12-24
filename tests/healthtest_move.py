#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
"""

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse


class HealthTest(TestCase):
    """
    Baseline Tests for this Django Webapp
    """

    def test_health_https(self):
        """
        Test `/health/`


        """
        result = self.client.get('/health/', secure=True)
        self.assertEqual(result.status_code, 200)  # only Secure connection


