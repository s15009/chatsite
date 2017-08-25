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


def index(request):
    """
    サイトのトップページ
    チャット部屋のリストを表示
    """
    latest_board_list = Board.objects.order_by('-pub_date')[:10]
    user = request.user
    if not user.is_authenticated:
        user = None
    print('user :', user)

    context = {
        'latest_board_list': latest_board_list,
        'user': user,
    }

    return render(request, 'chats/index.html', context)


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
            return HttpResponseRedirect(reverse('chats:board', args=(board.id, )))
    else:
        form = BoardForm()

    user = request.user
    context = {
        'form': form,
        'user': user,
    }

    return render(request, 'chats/create_board.html', context)


@login_required
def board(request, board_id):
    """
    個別のチャット部屋表示
    """

    board = Board.objects.get(id=board_id)
    login_users = board.login_users.all()
    profile = request.user
    message_max = 10

    # 部屋が死んでいたら墓場ページへ
    if board.is_status == 1 or not board.is_alive():
        comment_list = Message.objects.filter(board_id__id=board_id)
        context = {'board': board, 'comment_list': comment_list}
        return render(request, 'chats/tomb.html', context)

    # 部屋別ログイン処理
    if profile in login_users:
        print('{}は{}に既にログインしています'.format(profile.username, board.board_name))
    else:
        board.login_users.add(profile)
        print('{}は{}にログインしました'.format(profile.username, board.board_name))
    
    message_total = Message.objects.filter(board_id__id=board_id).count()

    # メッセージ取得、ヘイトがあるのは除く
    message_list = Message.objects.filter(board_id__id=board_id).exclude(message_hate__gt=10).order_by('-pub_date')[:message_max]

    context = {
        'message_list': message_list,
        'board': board,
        'profile': profile,
        'login_users': login_users,
        'message_total': message_total,
    }
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
    if board.is_status == 1 or not board.is_alive():
        data = {'is_alive' : False}
        return JsonResponse({'data': data}, safe=False)

    if request.method == 'POST':
        # 更新分メッセージリスト取得
        latest_message_id = request.POST.get('latest_message_id')
        lmpdt = request.POST.get('latest_message_pub_date')
        hates = json.loads(request.POST.get('hates'))

        #クリック時の削除ステータス更新
        for target in hates:
            mess = Message.objects.get(id=target)
            mess.message_hate += hates[target]
            mess.save()
            hates[target] = mess.message_hate

        updated_message_list = []
        if latest_message_id and lmpdt:
            # DBから最新のメッセージのみを取得
            latest_message_pub_date = datetime.strptime(lmpdt, Message.DATETIME_FORMAT)
            updated_message_list = Message.objects\
                    .filter(board_id__id=board_id)\
                    .filter(pub_date__gt=latest_message_pub_date)\
                    .exclude(id=latest_message_id)\
                    .exclude(message_hate__gt=10)
        else:
            updated_message_list = Message.objects.filter(board_id__id=board_id)

        # Jsonへの変換
        board = Board.objects.get(id=board_id)

        # 更新分投稿リスト
        message_list = []
        for message in updated_message_list:
            # テキストのHTMLタグ変換
            message_text = message.message.replace('\n', '<br>')
            image_url = message.image.url if message.image else None
            message_list.append({
                'id': message.id,
                'user_name': message.profile.username,
                'message': message_text,
                'image_url': image_url,
                'vibes': message.vibes,
                'pub_date': message.get_formated_pub_date(),
                'message_hate': message.message_hate,
            })
            hates[message.id] = message.message_hate

        # チャット部屋情報
        board_info = {
           'board_name': board.board_name,
        }

        # ログインユーザーリスト
        login_users = []
        for login_user in board.login_users.all():
            login_users.append({
                'user_name': login_user.username,
            })

        # ユーザー情報
        user_info = {
            'user_vibes': request.user.get_vibes()
        }

        data = {
            'message_list': message_list,
            'board_info': board_info,
            'user_info': user_info,
            'login_users': login_users,
            'message_hate': hates,
        }
        return JsonResponse({'data': data}, safe=False)

    return HttpResponse('failed', content_type='text/plain')

@login_required
def post_message(request, board_id):
    '''メッセージをDBに追加
    '''
    if request.method == 'POST':
        if request.FILES:
            image = request.FILES['file']
        else:
            image = None
        board = Board.objects.get(id=request.POST.get('board_id'))
        user = Twitter.objects.get(id=request.POST.get('profile_id'))
        text = request.POST.get('text')
        pub_date = timezone.now()
        vibes = user.get_vibes()

        message = Message(board_id=board, profile=user, message=text, pub_date=pub_date, image=image, vibes=vibes)
        message.save()

        image_url = message.image.url if message.image else None
        mess = {
            'id': message.id,
            'image_url': image_url,
            'vibes': message.vibes,
            'pub_date': message.get_formated_pub_date(),
        }

        data = {
            'message': mess,
        }

        return JsonResponse({'data': data}, safe=False)

    return HttpResponse('failed', content_type='text/plain')

def get_status(request, board_id):
    '''ステータスを見て、墓ページに移行'''
    if request.method == 'POST':
        pass

@login_required
def make_tomb(request):
    return render(request, 'chats/tomb.html')

