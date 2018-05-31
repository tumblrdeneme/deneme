from django.contrib.auth.models import User
from django.db import models


class TumblrToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apikey = models.CharField(max_length=50)
    access_token = models.CharField(max_length=50)
    access_token_secret = models.CharField(max_length=50)

    def get_oauth_token(self):
        return self.access_token, self.access_token_secret
