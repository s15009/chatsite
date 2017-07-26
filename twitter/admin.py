from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from twitter.models import Twitter

class UserCreationForm(forms.ModelForm):	
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
	
	class Meta:
		Model = Twitter
		fields = ('username', 'password', 'email')
	
	def clean_password2(self):
		# Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

	def save(self, commit=True):
        # Save the provided password in hashed format
		twitter = super(UserCreationForm, self).save(commit=False)
		twitter.set_password(self.cleaned_data["password1"])
		if commit:
			twitter.save()
		return twitter

class UserChangeForm(forms.ModelForm):
	password = ReadOnlyPasswordHashField()
	
	class Meta:
		model = Twitter
		fields = ('username', 'password', 'email', 'is_active', 'is_admin')

	def clean_password(self):
		return self.initial["password"]

class UserAdmin(BaseUserAdmin):
	form = UserChangeForm
	add_form = UserCreationForm

	list_display = ('username', 'email', 'is_admin')
	list_filter = ('is_admin',)
	fieldsets = (
        (None, {'fields': ('username','email', 'password')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )	

	search_fields = ('username',)
	ordering = ('username',)
	filter_horizontal = ()

admin.site.register(Twitter, UserAdmin)
admin.site.unregister(Group)
