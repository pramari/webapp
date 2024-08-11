"""
..todo::

    [ ] Add a description for the module.
    [ ] Add a description for the class.
    [ ] Add a description for the method.
    [ ] Add a description for the attribute.
    [ ] Add a description for the parameter.
    [ ] Add a description for the return value.
    [ ] Add a description for the exception.
    [ ] Basically everything. Do under no circumstances use this yet.

The idea of this is to be able to add a "FedID" to any model, that will
automatically be generated and stored, so objects creation and serialization
for ActivityPub can be done without having to worry about the ID.

"""
from django.db import models
from django.forms import CharField, URLInput, ValidationError, validators
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from urllib.parse import urlsplit, urlunsplit
import warnings
from django.utils.deprecation import RemovedInDjango60Warning

from webapp.validators import validate_iri


class URLField(CharField):
    widget = URLInput
    default_error_messages = {
        "invalid": _("Enter a valid URL."),
    }
    default_validators = [validators.URLValidator()]

    def __init__(self, *, assume_scheme=None, **kwargs):
        if assume_scheme is None:
            if settings.FORMS_URLFIELD_ASSUME_HTTPS:
                assume_scheme = "https"
            else:
                warnings.warn(
                    "The default scheme will be changed from 'http' to 'https' in "
                    "Django 6.0. Pass the forms.URLField.assume_scheme argument to "
                    "silence this warning, or set the FORMS_URLFIELD_ASSUME_HTTPS "
                    "transitional setting to True to opt into using 'https' as the new "
                    "default scheme.",
                    RemovedInDjango60Warning,
                    stacklevel=2,
                )
                assume_scheme = "http"
        # RemovedInDjango60Warning: When the deprecation ends, replace with:
        # self.assume_scheme = assume_scheme or "https"
        self.assume_scheme = assume_scheme
        super().__init__(strip=True, **kwargs)

    def to_python(self, value):
        def split_url(url):
            """
            Return a list of url parts via urlsplit(), or raise
            ValidationError for some malformed URLs.
            """
            try:
                return list(urlsplit(url))
            except ValueError:
                # urlsplit can raise a ValueError with some
                # misformatted URLs.
                raise ValidationError(self.error_messages["invalid"], code="invalid")

        value = super().to_python(value)
        if value:
            url_fields = split_url(value)
            if not url_fields[0]:
                # If no URL scheme given, add a scheme.
                url_fields[0] = self.assume_scheme
            if not url_fields[1]:
                # Assume that if no domain is provided, that the path segment
                # contains the domain.
                url_fields[1] = url_fields[2]
                url_fields[2] = ""
                # Rebuild the url_fields list, since the domain segment may now
                # contain the path too.
                url_fields = split_url(urlunsplit(url_fields))
            value = urlunsplit(url_fields)
        return value

class IRIField(models.CharField):
    default_validators = [validate_iri]
    description = _("IRI")

    def __init__(self, verbose_name=None, name=None, **kwargs):
        kwargs.setdefault("max_length", 200)
        super().__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get("max_length") == 200:
            del kwargs["max_length"]
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        # As with CharField, this will cause URL validation to be performed
        # twice.
        return super().formfield(
            **{
                "form_class": IRIField,
                **kwargs,
            }
        )
