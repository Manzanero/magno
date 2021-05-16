import base64

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse


def authenticate(username=None, password=None):
    try:
        user = User.objects.get(username__iexact=username)
        if user.check_password(password):
            return user
        return None
    except User.DoesNotExist:
        return None


def require_basic_auth(view):
    def wrapper(request, *args, **kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    uname, passwd = base64.b64decode(auth[1]).decode("utf8").split(':', 1)
                    user = authenticate(username=uname, password=passwd)
                    if user is not None and user.is_active:
                        request.user = user
                        return view(request, *args, **kwargs)
                    else:
                        message = '@require_basic_auth: HTTP_AUTHORIZATION not existing user'
                else:
                    message = '@require_basic_auth: HTTP_AUTHORIZATION not basic'
            else:
                message = '@require_basic_auth: HTTP_AUTHORIZATION bad format'
        else:
            message = '@require_basic_auth: HTTP_AUTHORIZATION not found'

        response = {'status': 401, 'message': message}
        return JsonResponse(response, safe=False, status=response['status'])

    return wrapper


def redirect_preflight(view):
    def wrapper(request, *args, **kwargs):
        response = HttpResponse() if request.method == 'OPTIONS' else view(request, *args, **kwargs)
        response['Access-Control-Allow-Origin'] = "http://localhost:64213"
        response['Access-Control-Allow-Credentials'] = "true"
        response['Access-Control-Allow-Headers'] = "Authorization, content-type"
        return response

    return wrapper
