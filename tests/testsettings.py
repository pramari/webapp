SECRET_KEY = "fake-key"
MIDDLEWARE = [
    "allauth.account.middleware.AccountMiddleware"
]
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "webapp",
]
