from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views import generic

from .models import Message, Board
from .forms import BoardForm
from twitter.models import Twitter

import json
from datetime import datetime

from django.urls import reverse


#@method_decorator(login_required, name='dispatch')
class IndexView(generic.ListView):
    """
    チャット部屋のリスト表示
    暫定でのもの
    """
    template_name = 'chats/index.html'
    context_object_name = 'latest_board_list'

    def get_queryset(self):
        return Board.objects.order_by('-pub_date')[:10]

@login_required
def create_board(request):
    """
    チャット部屋作成フォーム
    """
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.admin_id = request.user
            board.save()
            return HttpResponseRedirect('/chats/')
    else:
        form = BoardForm()

    return render(request, 'chats/create_board.html', {'form': form})


@login_required
def board(request, board_id):
    """
    個別のチャット部屋表示
    """
    message_list = Message.objects.filter(board_id__id=board_id).order_by('-pub_date')
    board = Board.objects.get(id=board_id)
    profile = request.user

    context = {'message_list': message_list, 'board': board, 'profile': profile}
    return render(request, 'chats/board.html', context)

@login_required
def get_message(request, board_id):
    '''
    個別のチャット部屋表示更新処理
    更新分のメッセージのみを送信
    メッセージはJsonで送信
    latest_message_id, latest_message_pub_dateが空のリクエストの場合は
    1件もメッセージが投稿されていない
    '''
    
    board = Board.objects.get(id=board_id)
		
	#掲示板の寿命がなくなっていればステータスに応じてリダイレクトさせる
    if board.is_status == 1:
        #return HttpResponse(json.dumps(response))
        #return HttpResponseRedirect(reverse('chats:make_tomb'))
        return render(request, 'chats/tomb.html')


    if request.method == 'POST':
        latest_message_id = request.POST.get('latest_message_id')
        lmpdt = request.POST.get('latest_message_pub_date')

        updated_message_list = []
        if latest_message_id and lmpdt:
            # DBから最新のメッセージのみを取得
            latest_message_pub_date = datetime.strptime(lmpdt, Message.DATETIME_FORMAT)
            updated_message_list = Message.objects\
                .filter(board_id__id=board_id)\
                .filter(pub_date__gt=latest_message_pub_date)\
                .exclude(id=latest_message_id)
        else:
            updated_message_list = Message.objects.filter(board_id__id=board_id)

        # Jsonへの変換
        data = []
        for message in updated_message_list:
            data.append({'id': message.id,
                'user_name': message.profile.username,
                'message': message.message,
                'pub_date': message.get_formated_pub_date(),
				'is_status': board.is_status})
        return JsonResponse({'data': data}, safe=False)

    return HttpResponse('failed', content_type='text/plain')

@login_required
def post_message(request, board_id):
    '''メッセージをDBに追加
    '''
    if request.method == 'POST':
        board = Board.objects.get(id=request.POST.get('board_id'))
        user = Twitter.objects.get(id=request.POST.get('profile_id'))
        text = request.POST.get('text')
        pub_date = timezone.now()

        mess = Message(board_id=board, profile=user, message=text, pub_date=pub_date)
        mess.save()

        return HttpResponse('successful', content_type="text/plain")

    return HttpResponse('failed', content_type='text/plain')

def get_status(request, board_id):
	'''ステータスを見て、墓ページに移行'''
	if request.method == 'POST':
		pass	    

@login_required
def make_tomb(request):
	return render(request, 'chats/tomb.html')




