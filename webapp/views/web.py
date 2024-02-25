#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
All `Angry Planet Cloud` Base Views.

These are generic to UserProfiles and all other Applications.
"""

import logging
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import UpdateView, FormView
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django import forms

# from pages.models import HomePage

from ..models import Profile
from ..forms import ProfileForm

# from newsfeed.models import Website


logger = logging.getLogger(__name__)
User = get_user_model()


class ContactForm(forms.Form):
    email = forms.EmailField()
    consent = forms.BooleanField()

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass


class HomeView(FormView):
    """
    Display the `Project Homepage`.

    Static Pages, does not change often.

    However, includes a dynamic header that displays account information.
    """

    template_name = "home.html"
    form_class = ContactForm

    def get_context(self, request):
        """
        get context for this request.
        """
        context = super().get_context(request)  # pylint: disable=E1101
        # context["blogpages"] = homepages  # add whatever you need here
        return context

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)


class StatusView(LoginRequiredMixin, TemplateView):
    """Say aha!."""

    template_name = "status.html"


# pylint: disable=R0901
class AccountView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View and update Account.

    Account includes username and password.
    """

    model = get_user_model()
    template_name = "account/account.html"
    success_url = "/accounts/account/"
    fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "password",
    ]

    def get_object(self, *args, **kwargs):
        """
        Get user object.

        Overriding super() implementation.
        """
        try:
            return super().get_object(*args, **kwargs)
        except AttributeError as error:
            logger.error(error)
            return self.model.objects.get(pk=self.request.user.pk)


# pylint: disable=R0901
class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View and update Profile.

    Enables users to view and edit their own profile.
    It is required to consent.
    """

    model = Profile
    template_name = "account/profile.html"
    form_class = ProfileForm
    success_url = "/accounts/profile/"
    success_message = _("Profile successfully saved!")

    def get_object(self, *args, **kwargs):
        """
        Get user object.

        Overriding super() implementation.
        """
        try:
            return super().get_object(*args, **kwargs)
        except AttributeError as error:
            logger.error(error)
            return self.model.objects.get(pk=self.request.user.pk)  # noqa


# pylint: disable=R0901
class ProfileDetailView(UserPassesTestMixin, DetailView):
    """
    Public View for Profile Page.

    This view requiresa the following:
    - User consent.
    - A verified Profile.
    - A public Profile.
    """

    model = Profile
    template_name = "account/profile_detail.html"

    def test_func(self):
        """This view requires a verfied profile."""
        if self.request.user.is_authenticated:
            return self.request.user.is_verified
        return False


class SearchView(ListView):
    """
    Search:
    """

    # model = Website
    template_name = "search_results.html"

    def get_queryset(self):  # new
        query = self.request.GET.get("q")
        if not query:  # no search term
            return []  # no results. easy.
        return []

    """
        from django.db.models import Q
        object_list = Website.objects.filter(  # pylint: disable=E1101
            Q(url__icontains=query)  # pylint: disable=E1131
            | Q(title__icontains=query)  # pylint: disable=E1131
            | Q(description__icontains=query)  # pylint: disable=E1131
        )
        return object_list
    """
