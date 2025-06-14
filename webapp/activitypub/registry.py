"""
https://raw.githubusercontent.com/justquick/django-activity-stream/main/actstream/registry.py
"""

from inspect import isclass

from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.base import ModelBase
from django.core.exceptions import ImproperlyConfigured

import logging
logger = logging.getLogger(__name__)


class RegistrationError(Exception):
    pass


def setup_generic_relations(model_class):
    """
    Set up GenericRelations for actionable models.
    """
    Action = apps.get_model("activitypub", "action")

    if Action is None:
        raise RegistrationError(
            "Unable get webapp.Action. Potential circular imports "
            "in initialisation. Try moving actstream app to come after the "
            "apps which have models to register in the INSTALLED_APPS setting."
        )

    related_attr_name = "related_query_name"
    related_attr_value = "actions_with_%s" % label(model_class, "_")

    relations = {}
    for field in ("actor", "target", "action_object"):
        attr = "%s_actions" % field
        attr_value = "{}_as_{}".format(related_attr_value, field)
        kwargs = {
            "content_type_field": "%s_content_type" % field,
            "object_id_field": "%s_object_id" % field,
            related_attr_name: attr_value,
        }
        rel = GenericRelation("activitypub.Action", **kwargs)
        rel.contribute_to_class(model_class, attr)
        relations[field] = rel

        # @@@ I'm not entirely sure why this works
        setattr(Action, attr_value, None)
    return relations


def label(model_class, sep="."):
    """
    Returns a string label for the model class. eg auth.User
    """
    if hasattr(model_class._meta, "model_name"):
        model_name = model_class._meta.model_name
    else:
        model_name = model_class._meta.module_name
    return "{}{}{}".format(model_class._meta.app_label, sep, model_name)


def is_installed(model_class):
    """
    Returns True if a model_class is installed.
    model_class._meta.installed is only reliable in Django 1.7+
    """
    return model_class._meta.app_config is not None


class ActorRegistry(dict):
    """
    A dictionary that stores the models that
    can be `Actor`s have been registered
    with webapp activity.

    .. todo::
        document this.
    """

    def _validate(self, model_class, exception_class=ImproperlyConfigured):
        """
        Validate that the model is a Model class and is not abstract.

        :param model_class: The model class to validate.
        :param exception_class: The exception class to raise if the model is
        invalid. Defaults to ImproperlyConfigured.
        """
        if isinstance(model_class, str):
            """
            If model_class is a string, try to import the model class by name.
            """
            model_class = apps.get_model(*model_class.split("."))

        if not isinstance(model_class, ModelBase):
            raise exception_class(
                f"Object {model_class} is not a Model class."
            )  # noqa: E501

        if model_class._meta.abstract:
            raise exception_class(
                "The model %r is abstract, so it cannot be registered with "
                "actstream." % model_class
            )

        if not is_installed(model_class):
            raise exception_class(
                "The model %r is not installed, please put the"
                "app '%s' in your 'INSTALLED_APPS' setting."
                % (model_class, model_class._meta.app_label)  # noqa: E501
            )
        return model_class

    def register(self, *model_classes_or_labels):
        """
        Register one or more models with the registry.
        """
        for class_or_label in model_classes_or_labels:
            logger.error("trying to register %s" % class_or_label)
            model_class = self._validate(class_or_label)
            logger.error("Got model_class %s" % model_class)

            if model_class not in self:
                logger.error("not in self: %s" % model_class)
                self[model_class] = setup_generic_relations(model_class)
                logger.error("Successfully registered: %s" % model_class)

    def unregister(self,*model_classes_or_labels):
        for class_or_label in model_classes_or_labels:
            model_class = self._validate(class_or_label)
            if model_class in self:
                del self[model_class]

    def check(self, model_class_or_object):
        if getattr(model_class_or_object, "_deferred", None):
            model_class_or_object = model_class_or_object._meta.proxy_for_model
        if not isclass(model_class_or_object):
            model_class_or_object = model_class_or_object.__class__
        model_class = self._validate(model_class_or_object, RuntimeError)
        if model_class not in self:
            raise ImproperlyConfigured(
                f"The model {model_class.__name__} is not registered."
                "Please use webapp.activitypub.registry to register it."
                "Registered are the following models:"
                f"{', '.join([model.__name__ for model in self])}"
            )
        logger.error("Successfully registered %s", model_class.__name__)





registry = ActorRegistry()
register = registry.register
unregister = registry.unregister
check = registry.check
