import base64
from json import JSONDecodeError

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from utils.exceptions import get_stacktrace_str


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


def api_response(view):
    @csrf_exempt
    @redirect_preflight
    @require_basic_auth
    def wrapper(request, *args, **kwargs):
        try:
            response = view(request, *args, **kwargs)
            status = {'GET': 200, 'POST': 200, 'PUT': 201, 'DELETE': 204}[request.method]
            return JsonResponse(response, safe=False, status=status)
        except Http404 as e:
            return JsonResponse({'message': f'{e}'}, safe=False, status=404)
        except JSONDecodeError as e:
            return JsonResponse({'message': f'JSONDecodeError: {e}'}, safe=False, status=400)
        except Exception as e:
            return JsonResponse({'message': get_stacktrace_str(e)}, safe=False, status=500)

    return wrapper
