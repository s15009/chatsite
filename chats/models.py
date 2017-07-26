from django.db import models
#from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from twitter.models import Twitter


'''
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date publish', auto_now_add=True)

    def __str__(self):
        return self.user_name
'''

class Board(models.Model):
    board_name = models.CharField(max_length=100, verbose_name="部屋の名前")
    admin_id = models.ForeignKey(Twitter)
    pub_date = models.DateTimeField('date publish', auto_now=True)
    description = models.TextField(blank=True, null=True, verbose_name="説明")

    def __str__(self):
        return self.board_name

class Message(models.Model):
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S:%f %z'

    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)
    profile = models.ForeignKey(Twitter)
    message = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date publish')

    def get_formated_pub_date(self):
        return self.pub_date.strftime(self.DATETIME_FORMAT)

    def __str__(self):
        return self.message
