#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
All `Angry Planet Cloud` Base Views.

These are generic to UserProfiles and all other Applications.
"""

import logging
from base64 import b64encode, b64decode
import json
from django.views.generic import View, TemplateView, ListView, DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db import DatabaseError, connection
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from pages.models import HomePage

from .models import Profile
from .forms import ProfileForm

# from newsfeed.models import Website


logger = logging.getLogger(__name__)
User = get_user_model()


class HomeView(TemplateView):
    """
    Display the `Project Homepage`.

    Static Pages, does not change often.

    However, includes a dynamic header that displays account information.
    """

    template_name = "home.html"

    def get_context(self, request):
        """
        get context for this request.
        """
        homepages = HomePage.objects.filter()

        # Update template context
        context = super().get_context(request)  # pylint: disable=E1101
        context["blogpages"] = homepages
        return context


# pylint: disable=R0201
class HealthCheckView(View):
    """
    Checks to see if the site is healthy.
    """
    def _check(self, cursor):
        cursor.execute("select 1")
        one = cursor.fetchone()[0]
        if one != 1:
            raise DatabaseError("Site did not pass health check")

    def get(self, *args, **kwargs):  # pylint: disable=W0613
        """
        Return OK if Site is OK.
        """

        with connection.cursor() as cursor:
            self._check(cursor)

        if False:  # Don't actually test the 'new' DB from here.
            with connections["new"].cursor() as cursor:
                self._check(cursor)

        return HttpResponse("ok")

    def post(self, *args, **kwargs):  # pylint: disable=W0613
        return HttpResponse("ok")


class StatusView(LoginRequiredMixin, TemplateView):
    """Say aha!."""

    template_name = "status.html"


# pylint: disable=R0901
class AccountView(LoginRequiredMixin, UpdateView):
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
class ProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View and update Profile.

    Enables users to view and edit their own profile.
    It is required to consent.
    """

    model = get_user_model()
    template_name = "account/profile.html"
    form_class = ProfileForm
    success_url = "/accounts/profile/"

    def test_func(self):
        """This view requires a verfied profile."""
        return self.request.user.is_verified

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
class ProfileDetailView(UserPassesTestMixin, DetailView):
    """
    Public View for Profile Page.

    This view requiresa the following:
    - User consent.
    - A verified Profile.
    - A public Profile.
    """

    model = Profile
    template_name = "account/profile.html"

    def test_func(self):
        return True


class GithubView(LoginRequiredMixin, TemplateView):
    """
    Experiment with GitHub Tokens.
    """
    template_name = "github.html"

    def get_context_data(self, **kwargs):
        """
        .. todo::
            This is currently broken.

        ```
        from crmeta.services import GitHub
                g = Github(access_token[0].token)
                if not username and not repository:
                    # Get a list of repositories.
                    context['user_repos'] = g.get_user().get_repos()
                    return context
                else:
                    # Get details for a specific repository.
                    context['repository'] =
                    g.get_repo(f"{username}/{repository}")
                    return context
        ```
        """
        context = super().get_context_data(**kwargs)
        # username = kwargs.get('username', None)
        # repository = kwargs.get('repository', None)
        # access_token = SocialToken.objects.filter(# pylint: disable=no-member
        #    account__user=self.request.user, account__provider="github"
        # )
        return context


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = "calendar.html"

    def get_context_data(self, **kwargs):
        import datetime
        from django.utils.timezone import make_naive, is_aware
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from allauth.socialaccount.models import SocialToken, SocialApp

        context = super().get_context_data(**kwargs)
        access_token = SocialToken.objects.filter(  # pylint: disable=no-member
            account__user=self.request.user, account__provider="google"
        )[0]
        app = SocialApp.objects.filter(provider="Google")[0]

        expires_at = access_token.expires_at
        if is_aware(access_token.expires_at):
            """
            .. todo:
                this is a hack. it converts `expires_at` to the default
                timezone set in `settings.py` for the project.
                However, it should rather use the timezone in which Google
                issued this token. This **MAY** be contained in `access_token`.

                Actually, it seems to be the other way round...
            """  # pylint: ignore=W0105
            expires_at = make_naive(access_token.expires_at)

        creds = Credentials(
            token=access_token.token,
            refresh_token=access_token.token_secret,
            expiry=expires_at,  # make_aware to default timezone above
            token_uri="https://oauth2.googleapis.com/token",
            client_id=app.client_id,  # replace with yours
            client_secret=app.secret,
        )

        if not creds or not creds.valid or creds.expired:
            """
            .. todo::
                Accessing the Google API requires
                a (apparently not yet expired) access_token,
                that needs refreshing if it was.

                creds.Refresh is what teh Intarwebs say,
                but need to refer to actual documentation at some point.
            """
            logger.error("Hello, Google!")
            creds.refresh(Request())

        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indic. UTC
        logger.info("Getting the upcoming 10 events")
        events_result = (
            service.events()  # pylint: disable=no-member
            .list(  # pylint: disable=no-member
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        context["events"] = events_result.get("items", [])
        from io import BytesIO

        star = BytesIO(
            b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAABAAAAAwCAMAAAAvgQplAAAAyVBMVEX////8+sz8/vT8jiz8Zhz89vT8ejT86tT8zrz87kT8ukz88nT8/vzs6uz88lz81mz8liT09vT8egz8poT86rz8vpz8+tz87uT89qTc3tz87jT8rjT88mT8+sT8niT8/uz8/tz8jhT89tT8+qzk4uT8Ygz8phz89uz8eiT85sz8zrT87jz8vhz88mz8+vzk5uT87lT89sT8yiT8mhT08vT8bgz8+uz8nlT85sT84lz8spT8+tT8ghT88tT89pzc2tz87iz8shz8VgQWXPWyAAAAAXRSTlMAQObYZgAAATBJREFUKJGVkn1vgjAQh3HzZWhVOidSlJiZwnRoGY6p6JTO7/+hVo6WUaJ/7Gdy5nl63KUEw7gTjGuCUp1ZluktESFR9RwTkhHMAFBEiQglNBM1EhJTReLXgo1goMjBDEA4pob2C9P/W0oh5WKUQy6RukcUYYTyKkWSwBFKkntXv5mGVxOzmc4nl5800eO8V0Hb4y7nng3wMDB5Hjcv5mAu5rtuQeLPbcDAEECocCFHyIdMWw3dFB2bcovsCBXPBXykQu2k8LjpMOSYPJbCucARujj/eh9xXBNpqvNiuz1rYrheDyt4PvyIvBQ9u+40KDPtvhnGKvgsExzynpX1KmOtihGdx2+I1VFD98+Qfbll+QVZKp74vt9uizKR4v3aHDM2bl6fpDiO4GtsjY63rv0LjCMywYpy0lMAAAAASUVORK5CYII="
            )
        )
        context["chart"] = f"<img src='data:image/png;base64,{b64encode(star.read()).decode('utf-8')}'/>"

        return context


class ContactView(LoginRequiredMixin, TemplateView):
    template_name = "contact.html"

    def get_context_data(self, **kwargs):
        """
        .. args::
            resourceName (optional)

        .. reference::
            People API
            https://developers.google.com/people
        """
        context = super().get_context_data(**kwargs)
        from .tasks import getGoogleContact, getAppAndAccessToken

        app, accessToken = getAppAndAccessToken(self.request.user, "google")

        if not accessToken:
            from django.contrib import messages

            messages.add_message(
                self.request, messages.ERROR, "No access to Google Contacts."
            )
            return context

        contacts = getGoogleContact(accessToken, app)

        context["contacts"] = contacts

        return context


class GmailView(LoginRequiredMixin, TemplateView):
    template_name = "gmail.html"

    def get_context_data(self, **kwargs):
        """
        https://towardsdatascience.com/visualizing-networks-in-python-d70f4cbeb259
        """


"""
Search:
"""


class SearchView(ListView):
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


class AddonView(TemplateView):
    template_name = "addon.json"
    http_method_names = [
        "get",
        "post",
    ]

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AddonMsginfoView(View):
    http_method_names = [
        "get",
        "post",
    ]

    def post(self, request, *args, **kwargs):  # pylint: disable=W0613
        print(request.POST)
        response = {
            "action": {
                "navigations": [
                    {
                        "pushCard": {
                            "header": {"title": "AddonMsginfoView!"},
                            "sections": [
                                {"widgets": [{"textParagraph": {"text": ""}}]}
                            ],
                        }
                    }
                ]
            }
        }

        return HttpResponse(json.dumps(response))

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    