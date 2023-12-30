"""
Scenario: somebody anonymously surfs to the pramari homepage and chose to register for the newsletter.
     Given they are surfing to the homepage.
      When they find the registration form.
      Then they can provide their email, consent and submit to register.

  Scenario: somebody follows a link to register.
     Given from a remote page, somebody only follows a link.
      When they arrive at the registration page
      Then they can provide their email, consent and submit to register.

  Scenario: a partner page wants to embed a registration form.
    Given they use an iframe to embed a registration form.
    When the registration form shows embedded on the remote page
    Then they can provide their email, consent and submit to register.
"""

from behave import given, when, then


@given('they are surfing to the homepage.')
def step_impl(context):  # noqa: W0404
    assert True is False

@when('they find the registration form.')
def step_impl(context):  # noqa: W0404
    assert True is False

@then('they can provide their email, consent and submit to register.')
def step_impl(context):  # noqa: W0404
    print(f"context: {context}")
    print(f"context.failed: {context.failed}")
    assert context.failed is False
