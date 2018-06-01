from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from tumblpy import Tumblpy, TumblpyAuthError

from blogger import settings
from tumblr.models import TumblrToken


def auth(request):
    t = Tumblpy(app_key=settings.TUMBLR_CONSUMER_KEY, app_secret=settings.TUMBLR_SECRET_KEY)
    auth_props = t.get_authentication_tokens(callback_url='/')
    auth_url = auth_props['auth_url']

    oauth_token = auth_props['oauth_token']
    oauth_token_secret = auth_props['oauth_token_secret']

    request.session["oauth_token"] = oauth_token
    request.session["oauth_token_secret"] = oauth_token_secret

    return redirect("http://www.tumblr.com/oauth/authorize?oauth_token=%s" % oauth_token)


def callback(request):
    t = Tumblpy(app_key=settings.TUMBLR_CONSUMER_KEY, app_secret=settings.TUMBLR_SECRET_KEY,
                oauth_token=request.session["oauth_token"],
                oauth_token_secret=request.session["oauth_token_secret"])

    oauth_verifier = request.GET.get('oauth_verifier')
    authorized_tokens = t.get_authorized_tokens(oauth_verifier)

    # save token locally.
    token, created = TumblrToken.objects.get_or_create(user=request.user, apikey=settings.TUMBLR_CONSUMER_KEY)
    token.access_token = authorized_tokens['oauth_token']
    token.access_token_secret = authorized_tokens['oauth_token_secret']
    token.save()
    return HttpResponse("Tumblr Oauth Passed.")


def post(request):
    user = request.user
    # check access token. If no access token, redirect to Oauth page.
    try:
        token = TumblrToken.objects.get(user=user, apikey=settings.TUMBLR_CONSUMER_KEY)
    except TumblrToken.DoesNotExist:
        return HttpResponseRedirect(reverse("tumblr_auth"))

    final_oauth_token, final_oauth_token_secret = token.get_oauth_token()

    t = Tumblpy(app_key=settings.TUMBLR_CONSUMER_KEY, app_secret=settings.TUMBLR_SECRET_KEY,
                oauth_token=final_oauth_token,
                oauth_token_secret=final_oauth_token_secret)
    try:
        # get default blog url.
        blog_url = t.post('user/info')
        blog_url = blog_url['user']['blogs'][0]['url']

        # post blog
        post = t.post('post', blog_url=blog_url, params={'title': 'A new blog', 'body': 'This is blog content.'})
    except TumblpyAuthError:
        return HttpResponseRedirect(reverse("tumblr_auth"))

    return HttpResponse("Blog post successfully.")
