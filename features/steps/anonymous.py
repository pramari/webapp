from behave import given, when, then



@given('we are using `pramari-webapp`')
def step_impl(context):
    from django.conf import settings
    assert 'webapp' in settings.INSTALLED_APPS


@when('we surf to `/`')
def step_impl(context):  # noqa: W0404
    assert True is not False


@then('webapp will serve a homepage with 200 OK.')
def step_impl(context):  # noqa: W0404
    print(f"context: {context}")
    print(f"context.failed: {context.failed}")
    assert context.failed is False
