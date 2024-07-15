from behave import given, when, then


@given('They post a follow message to the actor inbox')
def step_given_user_with_username(context, username):
    # Implement the logic to create a user with the given username
    pass

@when('the message contains an actor and an object')
def step_when_user_follows_another_user(context, username):
    # Implement the logic for a user to follow another user with the given username
    pass

@then('the object will add the actor to its followers collection and acknowledge the request.')
def step_then_user_should_be_following_another_user(context, username):
    # Implement the logic to verify that the user is following another user with the given username
    pass
