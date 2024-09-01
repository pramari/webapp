"""
admin.py for apc.

Define Admin-Views for `User`-Objects.
"""

import json
from functools import update_wrapper

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django import VERSION
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.core.exceptions import PermissionDenied
from django.db import router, transaction
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape

# from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from .forms import UserChangeForm, UserCreationForm
from .models import Action, Actor, Note, Profile, User, Like
from webapp.models.activitypub.actor import Follow
from .tasks import generateProfileKeyPair

try:
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path as url  # Django >= 4.0

try:
    from django.contrib.contenttypes.generic import (
        GenericForeignKey,
        GenericStackedInline,
        GenericTabularInline,
    )
except ImportError:
    from django.contrib.contenttypes.admin import (
        GenericStackedInline,
        GenericTabularInline,
    )
    from django.contrib.contenttypes.fields import GenericForeignKey

from django.contrib.admin.widgets import url_params_from_lookup_dict
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils.encoding import force_str as force_text  # Django >= 4.0
from django.utils.text import capfirst

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
        if VERSION >= (2, 2):
            media.append("admin/js/jquery.init.js")  # Django >= 2.2
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
            url(
                r"^obj-data/$",
                wrap(self.generic_lookup),
                name="admin_genericadmin_obj_lookup",
            ),
            url(
                r"^genericadmin-init/$",
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


class GenericAdminModelAdmin(BaseGenericModelAdmin, admin.ModelAdmin):
    """Model admin for generic relations."""


class GenericTabularInline(BaseGenericModelAdmin, GenericTabularInline):
    """Model admin for generic tabular inlines."""


class GenericStackedInline(BaseGenericModelAdmin, GenericStackedInline):
    """Model admin for generic stacked inlines."""


class TabularInlineWithGeneric(BaseGenericModelAdmin, admin.TabularInline):
    """ "Normal tabular inline with a generic relation"""


class StackedInlineWithGeneric(BaseGenericModelAdmin, admin.StackedInline):
    """ "Normal stacked inline with a generic relation"""


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = (
        "__str__",
        "user",
        "consent",
        "public",
        # "ap_id",
    )
    prepopulated_fields = {"slug": ["user",]}


admin.site.register(Profile, ProfileAdmin)


class NoteAdmin(admin.ModelAdmin):
    model = Note
    list_display = (
        "__str__",
        "published",
    )


admin.site.register(Note, NoteAdmin)


class LikeAdmin(admin.ModelAdmin):
    model = Like
    list_display = ("actor", "object", "created_at")


admin.site.register(Like, LikeAdmin)


class FollowInline(admin.TabularInline):
    model = Follow
    fk_name = "actor"
    list_display = ("object",)


class ActorAdmin(admin.ModelAdmin):
    model = Actor
    list_display = (
        "id",
        "type",
        "profile",
        "remote"
    )
    inlines = [FollowInline]


admin.site.register(Actor, ActorAdmin)


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


csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class SocialAccountInline(admin.TabularInline):
    """
    Inline Social Accounts.

    Use this to inline `SocialAccount`-Objects on `User`-Views.
    """

    model = SocialAccount


class EmailAddressInline(admin.TabularInline):
    """
    Inline EmailAddress.

    Use this to inline `EmailAddress`-Objects on `User`-Views.
    """

    model = EmailAddress


class ProfileInline(admin.TabularInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    """
    UserAdmin Class.

    Use this to define `User`-Objects AdminViews.
    """

    actions = [
        generateProfileKeyPair,
    ]
    add_form_template = "admin/auth/user/add_form.html"
    change_user_password_template = None
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Profile Information"), {"fields": ("public", "consent")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    list_display = (
        "username",
        "first_name",
        "last_name",
        "is_superuser",
        "is_staff",
        "is_active",
        "is_verified",
    )

    inlines = [ProfileInline, EmailAddressInline, SocialAccountInline]
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    def get_fieldsets(self, request, obj=None):
        """Get Fieldsets."""
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """Use special form during user creation."""
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_urls(self):
        return [
            path(
                "<id>/password/",
                self.admin_site.admin_view(self.user_change_password),
                name="auth_user_password_change",
            ),
        ] + super().get_urls()

    def lookup_allowed(self, lookup, value):
        """Don't allow lookups involving passwords."""
        return not lookup.startswith("password") and super().lookup_allowed(
            lookup, value
        )

    @sensitive_post_parameters_m
    @csrf_protect_m
    def add_view(self, request, form_url="", extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._add_view(request, form_url, extra_context)

    def _add_view(self, request, form_url="", extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    "order to add users, Django requires that your user "
                    'account have both the "Add user" and "Change user" '
                    "permissions set."
                )
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            "auto_populated_fields": (),
            "username_help_text": username_field.help_text,
        }
        extra_context.update(defaults)
        return super().add_view(request, form_url, extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=""):
        user = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(
                _("%(name)s object w/ primary key %(key)r does not exist.")
                % {
                    "name": self.model._meta.verbose_name,
                    "key": escape(id),
                }
            )
        if request.method == "POST":
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(
                    request, form, None
                )  # noqa: E501
                self.log_change(request, user, change_message)
                msg = _("Password changed successfully.")
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_change"
                        % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {"fields": list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            "title": _("Change password: %s") % escape(user.get_username()),
            "adminForm": adminForm,
            "form_url": form_url,
            "form": form,
            "is_popup": (
                IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET
            ),  # noqa: E501
            "add": True,
            "change": False,
            "has_delete_permission": False,
            "has_change_permission": True,
            "has_absolute_url": False,
            "opts": self.model._meta,
            "original": user,
            "save_as": False,
            "show_save": True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template
            or "admin/auth/user/change_password.html",  # noqa: E501
            context,
        )

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determine the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if (
            "_addanother" not in request.POST
            and IS_POPUP_VAR not in request.POST  # noqa: E501
        ):
            request.POST = request.POST.copy()
            request.POST["_continue"] = 1
        return super().response_add(request, obj, post_url_continue)


admin.site.register(User, UserAdmin)
