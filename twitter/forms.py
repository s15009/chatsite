from django import forms            
#from django.contrib.auth.models import Twitter #your custom model!
from twitter.models import Twitter
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

password = forms.RegexField(
		max_length = 16,
		min_length = 8,
		regex = r'^[a-zA-Z][a-zA-Z]+$',
		error_messages = {
			'invalid': _('先頭を半角英字から始めて、8〜16文字の半角英字で入力してください。'),
		},
		widget = forms.PasswordInput,
	)

class MyRegistrationForm(UserCreationForm):
	username = forms.RegexField(
        max_length = 8,
        min_length = 3,
        regex = r'^[a-z][a-zA-Z]+$',
        error_messages = {
            'invalid': _('先頭を小文字の半角英字から始めて、3〜8文字の半角英字で入力してください。'),
        },
	)
	
	password1 = password
	password2 = password
	email = forms.EmailField(required=True)

	class Meta:
		model = Twitter
		fields = ('username', 'email',)

	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			Twitter._default_manager.get(email = email)
		except Twitter.DoesNotExist:
			return email
		raise forms.ValidationError(
            '同じメールアドレスが既に登録済みです。'
        )
	
