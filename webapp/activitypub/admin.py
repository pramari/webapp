import json

from django.contrib import admin
from .models import Follow
from .models import Note
from .models import Action
from .models import Like
from .models import Actor

from django.conf import settings
from django.utils.encoding import force_str as force_text  # Django >= 4.0
from django.utils.text import capfirst
from django.http import HttpResponse, HttpResponseNotAllowed
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.widgets import url_params_from_lookup_dict
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.options import (
    StackedInline as GenericStackedInline,
    TabularInline as GenericTabularInline,
)
from django.urls import path
from functools import update_wrapper
from django.http import Http404

JS_PATH = getattr(settings, "GENERICADMIN_JS", "genericadmin/js/")


class BaseGenericModelAdmin(object):
    class Media:
        js = ()

    content_type_lookups = {}
    generic_fk_fields = []
    content_type_blacklist = []
    content_type_whitelist = []

    def __init__(self, model, admin_site):
        try:
            media = list(self.Media.js)
        except AttributeError:
            media = []
        media.append("admin/js/jquery.init.js")  # Django >= 2.2, no support for Django < 2.2
        media.append(JS_PATH + "genericadmin.js")
        self.Media.js = tuple(media)

        self.content_type_whitelist = [
            s.lower() for s in self.content_type_whitelist
        ]  # noqa: E501
        self.content_type_blacklist = [
            s.lower() for s in self.content_type_blacklist
        ]  # noqa: E501

        super(BaseGenericModelAdmin, self).__init__(model, admin_site)

    def get_generic_field_list(self, request, prefix=""):
        if hasattr(self, "ct_field") and hasattr(self, "ct_fk_field"):
            exclude = [self.ct_field, self.ct_fk_field]
        else:
            exclude = []

        field_list = []
        if hasattr(self, "generic_fk_fields") and self.generic_fk_fields:
            for fields in self.generic_fk_fields:
                if (
                    fields["ct_field"] not in exclude
                    and fields["fk_field"] not in exclude  # noqa: E501
                ):
                    fields["inline"] = prefix != ""
                    fields["prefix"] = prefix
                    field_list.append(fields)
        else:
            try:
                virtual_fields = self.model._meta.virtual_fields
            except AttributeError:
                virtual_fields = (
                    self.model._meta.private_fields
                )  # Django >= 2.0  # noqa: E501

            for field in virtual_fields:
                if (
                    isinstance(field, GenericForeignKey)
                    and field.ct_field not in exclude
                    and field.fk_field not in exclude  # noqa: E501
                ):
                    field_list.append(
                        {
                            "ct_field": field.ct_field,
                            "fk_field": field.fk_field,
                            "inline": prefix != "",
                            "prefix": prefix,
                        }
                    )

        if hasattr(self, "inlines") and len(self.inlines) > 0:
            for FormSet, inline in zip(
                self.get_formsets_with_inlines(request),
                self.get_inline_instances(request),
            ):
                if hasattr(inline, "get_generic_field_list"):
                    prefix = FormSet.get_default_prefix()
                    field_list = field_list + inline.get_generic_field_list(
                        request, prefix
                    )

        return field_list

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        custom_urls = [
            path(
                r"obj-data/",
                wrap(self.generic_lookup),
                name="admin_genericadmin_obj_lookup",
            ),
            path(
                r"genericadmin-init/",
                wrap(self.genericadmin_js_init),
                name="admin_genericadmin_init",
            ),
        ]
        return custom_urls + super(BaseGenericModelAdmin, self).get_urls()

    def genericadmin_js_init(self, request):
        if request.method == "GET":
            obj_dict = {}
            for c in ContentType.objects.all():
                val = force_text("%s/%s" % (c.app_label, c.model))
                params = self.content_type_lookups.get(
                    "%s.%s" % (c.app_label, c.model), {}
                )
                params = url_params_from_lookup_dict(params)
                if self.content_type_whitelist:
                    if val in self.content_type_whitelist:
                        obj_dict[c.id] = (val, params)
                elif val not in self.content_type_blacklist:
                    obj_dict[c.id] = (val, params)

            data = {
                "url_array": obj_dict,
                "fields": self.get_generic_field_list(request),
                "popup_var": IS_POPUP_VAR,
            }
            resp = json.dumps(data, ensure_ascii=False)
            return HttpResponse(resp, content_type="application/json")
        return HttpResponseNotAllowed(["GET"])

    def generic_lookup(self, request):
        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])

        if "content_type" in request.GET and "object_id" in request.GET:
            content_type_id = request.GET["content_type"]
            object_id = request.GET["object_id"]

            obj_dict = {
                "content_type_id": content_type_id,
                "object_id": object_id,
            }

            content_type = ContentType.objects.get(pk=content_type_id)
            obj_dict["content_type_text"] = capfirst(force_text(content_type))

            try:
                obj = content_type.get_object_for_this_type(pk=object_id)
                obj_dict["object_text"] = capfirst(force_text(obj))
            except ObjectDoesNotExist:
                raise Http404

            resp = json.dumps(obj_dict, ensure_ascii=False)
        else:
            resp = ""
        return HttpResponse(resp, content_type="application/json")


class GenericTabularInline(BaseGenericModelAdmin, GenericTabularInline):
    """Model admin for generic tabular inlines."""


class GenericStackedInline(BaseGenericModelAdmin, GenericStackedInline):
    """Model admin for generic stacked inlines."""


class TabularInlineWithGeneric(BaseGenericModelAdmin, admin.TabularInline):
    """ "Normal tabular inline with a generic relation"""


class StackedInlineWithGeneric(BaseGenericModelAdmin, admin.StackedInline):
    """ "Normal stacked inline with a generic relation"""


class GenericAdminModelAdmin(BaseGenericModelAdmin, admin.ModelAdmin):
    """Model admin for generic relations."""


# Register your models here.
class FollowInline(admin.TabularInline):
    model = Follow
    fk_name = "actor"
    list_display = ("object",)


class ActorAdmin(admin.ModelAdmin):
    model = Actor
    list_display = ("id", "type", "profile", "remote")
    inlines = [FollowInline]


admin.site.register(Actor, ActorAdmin)


class NoteAdmin(admin.ModelAdmin):
    model = Note
    list_display = (
        "__str__",
        "published",
    )


admin.site.register(Note, NoteAdmin)


class ActionAdmin(GenericAdminModelAdmin):
    date_hierarchy = "timestamp"
    list_display = (
        "__str__",
        "timestamp",
        "actor",
        "activity_type",
        "action_object",
        "target",
        "public",
    )
    # list_editable = ("activity_type",)
    list_filter = ("timestamp",)  # "activity_type")
    # raw_id_fields = (
    #     "actor_content_type",
    #     "target_content_type",
    #     "action_object_content_type",
    # )


admin.site.register(Action, ActionAdmin)


class LikeAdmin(admin.ModelAdmin):
    model = Like
    list_display = ("actor", "object", "created_at")


admin.site.register(Like, LikeAdmin)
