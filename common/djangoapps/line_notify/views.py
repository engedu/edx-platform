from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from line_notify.models import LineToken
from django.contrib.auth.models import User
import requests


def line_login(request):
    uid = request.GET['uid']
    user = User.objects.get(id=uid)
    query = LineToken.objects.filter(user=user)
    url = "https://notify-bot.line.me/oauth/authorize"
    url = url + "?response_type=code"
    url = url + "&client_id=2FiajbKaqThu1rRS8CdJYM"
    url = url + "&redirect_uri=https://www.whale.education/notify/callback/?uid=" + uid
    url = url + "&scope=notify"
    url = url + "&state=mujxi7dKk"
    # check token for this uid
    if query:
        # have token then delete and return login page
        query.delete()
        return HttpResponseRedirect(url)
    else:
        # dont have token then return login page
        return HttpResponseRedirect(url)


def revoke_token(request):
    return HttpResponse('revoke-token')


def callback(request):
    code = request.GET['code']
    uid = request.GET['uid']
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
    user = User.objects.get(id=uid)
    LineToken.objects.get_or_create(user=user, token=access_token, status=1)
    return HttpResponseRedirect(reverse('complete'))


def complete(request):
    return HttpResponse('complete')


def post_message(request):
    return HttpResponse('post_message')


def check_status(request):
    return HttpResponse('check_status')
