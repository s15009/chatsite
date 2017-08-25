from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

from datetime import timedelta


class TwitterUserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if not username:
            raise ValueError('Your username is must be key!')       
        twitter = self.model(username=username, email=email)    
        twitter.set_password(password)
        twitter.save(using=self._db)    
        return twitter

    def create_superuser(self, username, email, password=None):
        twitter = self.create_user(username, email,  password)
        twitter.is_admin = True
        twitter.save(using=self._db)
        return twitter

class Twitter(AbstractBaseUser):
            
    username = models.CharField(verbose_name = 'ユーザー名', max_length=40, unique=True)    
    email = models.CharField(verbose_name = 'email', max_length=40, unique=True)
    #social = User.social_auth.get(provider='twitter')
    #twitter_token = social.extra_data['access_token']
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = TwitterUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']


    # 熱量のマックス値
    VIBES_MAX = 100
    # 1メッセージで上昇する熱量
    HOT_UP_VIBES_PER_MESSAGE = 10
    # 1秒間に下降する熱量
    COOL_DOWN_VIBES_PER_SECOND = 1

    def get_vibes(self):
        """
        熱量取得
        """
        from chats.models import Message

        # プランD
        now = timezone.now()
        latest_message = Message.objects.filter(profile=self).order_by('pub_date').last()
        if not latest_message:
            return 0
        old_vibes = latest_message.vibes + self.HOT_UP_VIBES_PER_MESSAGE
        elapsed_time = (now - latest_message.pub_date).total_seconds()
        vibes = old_vibes - (elapsed_time * self.COOL_DOWN_VIBES_PER_SECOND)
        if vibes < 0:
            vibes = 0

        return vibes

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def get_email_field_name(self):
        return self.username
    
    def __str__(self):
        return self.username
            
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # permission 関係
        return True
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # permission
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # admin 権限確認
        return self.is_admin



