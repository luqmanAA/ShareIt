from django import template

register = template.Library()


def filter_query(value, arg):
    # returns on the value that matches the arg
    if value.filter(user_id=arg).exists():
        return True
    return False


register.filter('filter_query', filter_query)
