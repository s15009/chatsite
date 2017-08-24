from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone 
from datetime import timedelta

from twitter.models import Twitter



class Board(models.Model):
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S:%f %z'
    DISPLAY_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    board_name = models.CharField(max_length=100, verbose_name="ルーム名")
    admin_id = models.ForeignKey(Twitter)
    pub_date = models.DateTimeField('date publish', auto_now=True)
    is_status = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True, verbose_name="説明")
    lifespan = models.IntegerField(default=60) 
    login_users = models.ManyToManyField(Twitter, related_name='login_user')

    def is_alive(self):
        life =  self.pub_date + timedelta(seconds = self.lifespan)
        if life >= timezone.now():
            return True
        else:
            return False

    def get_formated_pub_date(self):
        jptime = self.pub_date + timedelta(hours = 9)
        return jptime.strftime(self.DATETIME_FORMAT)

    def get_display_pub_date(self):
        jptime = self.pub_date + timedelta(hours = 9)
        return jptime.strftime(self.DISPLAY_DATETIME_FORMAT)
    
    def get_display_dead_time(self):
        dead_time = self.pub_date + timedelta(hours = 9, seconds = self.lifespan)
        return dead_time.strftime(self.DISPLAY_DATETIME_FORMAT)

    def __str__(self):
        return self.board_name

class Message(models.Model):
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S:%f %z'

    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)
    profile = models.ForeignKey(Twitter)
    message = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date publish')
    message_hate = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', null=True, default=None)
    vibes = models.IntegerField(default=0)

    def get_formated_pub_date(self):
        jptime = self.pub_date + timedelta(hours = 9)
        return self.pub_date.strftime(self.DATETIME_FORMAT)

    def __str__(self):
        return self.message
