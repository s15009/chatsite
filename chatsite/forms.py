from django.contrib.auth import authenticate, login, logout
from djnago.shortcuts import redirect, render

def my_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		# ログイン成功
	else:
        # ログインに失敗しました

	#if not request.user.is_authenticated:
		#return render(request, 'html')



def logout_view(request):
    logout(request)
    # トップに戻す。
