from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name) -> bool:
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:  # pylint: disable=E1101
        return False
    return bool(group in user.groups.all())
