from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from line_notify.models import LineToken, CourseNotify
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from opaque_keys.edx.keys import CourseKey
import requests
import uuid
from .tasks import send_line_notify


def line_login(request):
    uid = request.GET['uid']
    user = User.objects.get(id=uid)
    query = LineToken.objects.filter(user=user)
    # check token for this uid
    if query:
        query.delete()
    # create state unique param for checking callback uid
    state = uuid.uuid4()
    create = LineToken(user=user, token="0", state=state)
    create.save()
    url = "https://notify-bot.line.me/oauth/authorize"
    url = url + "?response_type=code"
    url = url + "&client_id=2FiajbKaqThu1rRS8CdJYM"
    url = url + "&redirect_uri=https://www.whale.education/notify/callback/?uid=" + uid
    url = url + "&scope=notify"
    url = url + "&state=" + str(state)
    return HttpResponseRedirect(url)


def revoke_token(request):
    uid = request.GET['uid']
    try:
        user = User.objects.get(id=uid)
        query = LineToken.objects.get(user=user)
    except ObjectDoesNotExist:
        return JsonResponse({
                'status': 'failed',
                'message': 'Data does not exist.'
            },
            status=404)
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Bearer " + query['token']}
    res = requests.post('https://notify-api.line.me/api/revoke', headers=headers).json()
    if res['status'] == 200:
        query.delete()
        return JsonResponse({
            'status': 'successful'
        })
    else:
        return JsonResponse({
            'status': 'failed',
            'message': 'Cannot revoke token from Line API'
        }, status=400)
    


def callback(request):
    code = request.GET['code']
    uid = request.GET['uid']
    state = request.GET['state']
    try:
        query_user = User.objects.get(id=uid)
        query_state = LineToken.objects.get(user=query_user, state=state)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('failed'))
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    res = requests.post('https://notify-bot.line.me/oauth/token', data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://www.whale.education/notify/callback/?uid=" + uid,
        "client_id": "2FiajbKaqThu1rRS8CdJYM",
        "client_secret": "vTDF9Wi1tWzhM79PQpSp7pqDUhoK6Bx5jF8vGDOD9l0"
    }, headers=headers).json()
    access_token = res.get("access_token")
    # store access token and uid in db to use in another API
    LineToken.objects.filter(user=query_user, state=state).update(token=access_token, status=1)
    return HttpResponseRedirect('/')


def failed(request):
    return HttpResponse('failed: User not match')


@api_view(['POST'])
def post_message(request):
    _data = request.POST
    message = _data['message']
    uid = _data['uid']
    user = User.objects.get(id=uid)
    # get access_token from db by uid
    # access_token = 'oYW2nJlmUyyucuI3uSNci9OWyerUa2e9Cf30b4Qn16Y'
    query = LineToken.objects.get(user=user)
    # result = line_token_schema.dump(query)
    access_token = query.token
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Bearer " + access_token}
    res = requests.post('https://notify-api.line.me/api/notify', data={
        "message": message
    }, headers=headers).json()
    return HttpResponse(res)


def check_status(request):
    return HttpResponse('check_status')

def save_config(request):
    send_line_notify.delay()
    uid = request.GET['uid']
    course_id = request.POST
    courses = course_id.dict()
    try:
        user = User.objects.get(id=uid)
        token = LineToken.objects.get(user=user)
    except ObjectDoesNotExist:
        return JsonResponse(
            {
                'status': 'failed',
                'message': 'Data does not exist.'
            },
            status=404
        )
    for item in course_id:
        id = CourseKey.from_string(item)
        CourseNotify.objects.filter(course_id=id, line_token=token).update(status=courses[item])
    return JsonResponse(
        {
            'status': 'successful'
        }
    )
