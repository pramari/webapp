"""
validators.py

This module contains custom validators for the application.

def validate_iri(url):
    This function validates the IRI of a URL.
"""


from rfc3987 import parse
from django.core.exceptions import ValidationError


def validate_iri(iri: str) -> bool:
    try:
        parse(iri, rule='IRI')
    except ValueError:
        raise ValidationError('Invalid IRI')
