from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
#from django.contrib.auth.models import User

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
		
	username = models.CharField(verbose_name = 'username', max_length=40, unique=True)	
	email = models.CharField(verbose_name = 'email', max_length=40, unique=True)
	#social = User.social_auth.get(provider='twitter')
	#twitter_token = social.extra_data['access_token']
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	objects = TwitterUserManager()

	USERNAME_FIELD = 'username'
	EMAIL_FIELD = 'email'
	REQUIRED_FIELDS = ['email']

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



