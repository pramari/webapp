"""
validators.py

This module contains custom validators for the application.

def validate_iri(url):
    This function validates the IRI of a URL.
"""

from rfc3987 import parse
from django.core.exceptions import ValidationError
import urllib.parse


def uri_validator(x):
    try:
        result = urllib.parse.urlparse(x)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False


def validate_iri(iri: str) -> bool:
    try:
        parse(iri, rule="IRI")
    except ValueError:
        raise ValidationError("Invalid IRI")
