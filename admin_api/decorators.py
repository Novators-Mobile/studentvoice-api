from django.contrib.auth.models import AnonymousUser
from rest_framework.response import Response
from rest_framework import status


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if type(request.user) is AnonymousUser:
            return Response('access denied', status=status.HTTP_403_FORBIDDEN)
        if request.user.user_type == 'admin':
            return view_func(request, *args, **kwargs)
        else:
            return Response('access denied', status=status.HTTP_403_FORBIDDEN)
    return wrapper

