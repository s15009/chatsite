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

    # ボードのメッセージ総数
    def get_comment_total(self):
        return Message.objects.filter(board_id__id=self.id).count() 

	#ボードの平均熱量
    def get_message_vibe_average(self):
        mess_list = Message.objects.filter(board_id__id=self.id)
        allvibes = 0
        count = 0
        for mess in mess_list:
            allvibes += mess.vibes
            count+=1
        return allvibes / count
	#ボードの平均ヘイト
    def get_message_hate_average(self):
        mess_list = Message.objects.filter(board_id__id=self.id)
        allhates = 0
        count = 0
        for mess in mess_list:
            allhates += mess.message_hate
            count+=1
        return allhates / count
	#ボードの総参加人数
    def get_board_num(self):
        count = 0
        for mem in self.login_users.all():
            count+=1
        return count

	#一番ヘイトが集まった画像
    def get_most_hate_image(self):
        mess_list = Message.objects.filter(board_id__id=self.id)
        most_image = None
        count = 0
        for mess in mess_list:
            if(mess.image and count <= mess.message_hate):
                most_image = mess
                count = mess.message_hate 
        if most_image is None:
            return False
        return most_image.image.url

    def __str__(self):
        return self.board_name

class Message(models.Model):
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S:%f %z'
    
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)
    sequence_id = models.IntegerField(default=None, null=True)
    profile = models.ForeignKey(Twitter)
    message = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date publish')
    message_hate = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', null=True, default=None)
    vibes = models.IntegerField(default=0)

    
    class Meta:
        unique_together = (("board_id", "sequence_id"))

    def get_formated_pub_date(self):
	    jptime = self.pub_date + timedelta(hours = 9)
	    return self.pub_date.strftime(self.DATETIME_FORMAT)

    def __str__(self):
        return self.message

    #insert時のsave override
    def save(self):
	    #ルームにコメントがない場合の初期化
	    print("インサートっすよ")
	    comment_list = Message.objects.filter(board_id__id=self.board_id.id)
	    if len(comment_list) == 0:
	        self.sequence_id = 1
	    else:
	        self.sequence_id = Message.objects.filter(board_id__id=self.board_id.id).order_by('sequence_id').last().sequence_id + 1
	    super(Message, self).save()

    def update_save(self):
        print("アップデートです")
        super(Message, self).save()


