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


    # 1メッセージで上昇する熱量
    VIBES_MAX = 100
    HOT_UP_VIBES_PER_MESSAGE = 10
    COOL_DOWN_VIBES_PER_SECOND = 0.1
    def get_vibes(self):
        from chats.models import Message

        now = timezone.now()

        # 熱量に影響を与えるメッセージの投稿時間の最小
        deadline = now - timedelta(seconds=(self.HOT_UP_VIBES_PER_MESSAGE / self.COOL_DOWN_VIBES_PER_SECOND))

        # 熱量に影響を与えるメッセージリスト
        valid_message_list = Message.objects.filter(profile=self).filter(pub_date__gt=deadline).order_by('pub_date')

        # 最新のメッセージ投稿がない場合は熱量0
        if valid_message_list.count() == 0:
            return 0

        total_vibes = 0
        for message in valid_message_list:
            # 現在時間からメッセージ投稿時間までの経過時間
            elapsed_time = (now - message.pub_date).total_seconds()
            # メッセージ単位での影響熱量
            vibes = self.HOT_UP_VIBES_PER_MESSAGE - (elapsed_time * self.COOL_DOWN_VIBES_PER_SECOND)
            total_vibes += vibes

        # TODO 差分の時間を出して足す(保留中)
        '''
        prev_message = None
        if valid_message_list[0].id != 1:
            prev_message = valid_message_list[0].get_next_by_pub_date()
        diff = valid_message_list[0].pub_date
        if prev_message:
            diff -= valid_message_list[0].pub_date - prev_message.pub_date if prev_message else 0

        (valid_message_list.count() * self.HOT_UP_VIBES_PER_MESSAGE) + (diff * self.COOL_DOWN_VIBES_PER_SECOND)
        '''
        return total_vibes

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



