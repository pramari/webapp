SECRET_KEY = "fake-key"
INSTALLED_APPS = [
    "webapp",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]
MIDDLEWARE = [
    "allauth.account.middleware.AccountMiddleware",
]
AUTH_USER_MODEL = "webapp.User"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
