from twitter.models import Twitter

class LoginBackend(object):
    def authenticate(self, request, user):
        return twitter

    def get_user(self, user_id):
        try:
            return Twitter.objects.get(pk=user_id)
        except Twitter.DoesNotExist:
            return None
