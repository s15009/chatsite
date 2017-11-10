$(function() {
    // メッセージ熱量処理
    updateMessageVibes();

    // フォームの動き処理
    $('#text').on('click', function() {
        $('#submitBtn').show();
        if ($(this).prop('rows') < 2) {
            $(this).prop('rows', 2);
        }
    });

    // テキストボックスに文字が入力されるとそれに合わせて行数を増やす
    $('#text').on('keyup', function() {
        if ($(this).val() == '') {
            $('#submitBtn').prop('disabled', true);

            // 添付ファイルが有る場合は送信ボタンを表示する
            if ($('#file').prop('files')[0]) {
                $('#submitBtn').prop('disabled', false);
            }
        }
        else {
            $('#submitBtn').prop('disabled', false);
        }
        // テキストボックスのrowsの調整
        var return_num = $(this).val().match(/\n/gm);
        if (return_num) {
            $(this).prop('rows', (return_num.length + 2));
        }
        else {
            $(this).prop('rows', 2);
        }
    });

    // 添付ファイルを付けると送信可能にする
    $('#file').on('change', function(e) {
        if ($(this).prop('files')[0]) {
            $('#submitBtn').show();
            $('#submitBtn').prop('disabled', false);
        }
    });

    // フォーム以外をクリックするとフォームを縮小する
    $(document).on('click', function(e) {
        // テキストボックスが空の場合にテキストボックスを1行にする
        if (!$.contains($('#messageForm')[0], e.target)
                && $('#text').val() == '') {
            $('#text').prop('rows', 1);

            // 添付ファイルがない場合送信ボタンを消す
            if ($('#file').prop('files')[0] == null) {
                $('#submitBtn').hide();
            }
        }
    });


    // 寿命のカウントダウン処理
    var timer = setInterval(function() {
        var b_pub_date = new Date(board_pub_date.slice(0, -9));
        var elapsed_time = (Date.now() - b_pub_date) / 1000;
        var timelimit = (board_lifespan - Math.floor(elapsed_time));

        // 寿命が-1になるとリダイレクトする
        if (timelimit <= 0) {
            clearInterval(timer);
            window.location.href = window.location.href;
        }
        $('#timelimit').text('残り時間 : ' + timelimit);
    }, 100);

    // 定期処理
    var check = setInterval('updateMessage()', 3000);

    // 読み込まれた時メッセージリストのid ヘイトのオブジェクト
    $(document).ready(function(){
        $('.message').each(function(i){
            hates[$(this).children('input[name=id]').val()]
                = parseInt($(this).children('input[name=hate]').val());
        }); 
    });

    // メッセージ送信ボタンクリック処理
    $('#messageForm').submit(function(e) {
        console.log('ボタン押下');
        var formData = new FormData();
        formData.append('board_id', board_id);
        formData.append('profile_id', profile_id);
        formData.append('text', $('#text').val());
        formData.append('file', $('#file').prop('files')[0]);

        // submitクリック時のページ更新防止
        e.preventDefault();

        // メッセージ送信
        console.log('送信');
        $.ajax({
            url: $('#messageForm').attr('action'),
            type: 'post',
            datatype: 'json',
            cache: 'false',
            processData: false,
            contentType: false,
            data: formData,
            timeout: 10000,
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader('X-CSRFToken', $("input[name='csrfmiddlewaretoken']").val());
            },
        }).done(function(res, textStatus, jqXHR) {
            console.log('送信完了');
            // 投稿メッセージ要素を追加
            var message = new Message(
                parseInt(res.data['message'].id),
                $('#text').val(),
                res.data['message'].image_url,
                parseInt(res.data['message'].vibes),
                0
            );
            $('#message_list ul').prepend(createMessageLi(message)
				.css({right:"-100px", opacity:"0.0"})
				.animate({right:"0", opacity:"1.0"}, 500));

            // 最新メッセージ情報の更新
            latest_message_pub_date = res.data['message'].pub_date;
            latest_message_id = message.id;
            //hates[res.data['message'].id] = 0;
            console.log(hates);

            // 投稿メッセージのスタイル更新
            updateMessageVibes();

            // テキストフォームの初期化
            var text = $('#text');
            text.val('');
            text.prop('rows', 2);
            $('#submitBtn').prop('disabled', true);
            $('#file').val('');
        }).fail(function(jqXHR, testStatus, errorThrown) {
            // 投稿失敗
        });
    });
});

// メッセージ受信処理
function updateMessage() {
    $form = $('#messageForm');
    $.ajax({
        url: window.location.href + 'get',
        type: 'post',
        dateType: 'JSON',
        cache: 'false',
        data: {
            latest_message_pub_date: latest_message_pub_date,
            latest_message_id: latest_message_id,
            hates: JSON.stringify(hates)
        },
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', $("input[name='csrfmiddlewaretoken']").val());
        },
    }).done(function(res) {
        // チャット部屋が死んでいたらリダイレクトする
        if (res.data['is_alive'] == false) {
            window.location.href = window.location.href;
        }
        
        // メッセージリスト更新処理
        var message_list = res.data['message_list'];
        if (message_list.length > 0) {
            // 最新メッセージ情報の更新
            latest_message = message_list[message_list.length - 1];
            latest_message_pub_date = latest_message.pub_date;
            latest_message_id = latest_message.id;

            // メッセージ要素の追加
            $.each(message_list, function(index, message) {
                // 例) <li class="list-group-item my-2"><p></p><img></li>
                var messageLi = $("<li></li>", {
                    'class': 'list-group-item my-2 message',
                });
                messageLi.append('<p>' + AutoLink(message.message) + '</p>');
                // 画像添付があれば<img>要素を追加
                if (message.image_url) {
                    messageLi.append($('<img>', {
                        'src': message.image_url,
                        'class': 'img-thumbnail',
                    }));
                }
                // 熱量のメタデータ要素を追加
                messageLi.append($('<input></input>', {
                    'type': 'hidden',
                    'name': 'vibes',
                    'value': String(message.vibes),
                }));
				messageLi.append('<input type="hidden" name="hate" value="' + message.message_hate + '"/>');
				messageLi.append('<input type="hidden" name="id" value="' + message.id + '"/>');

                // listのDOMに追加する
                $('#message_list ul').prepend(messageLi.hide().fadeIn(1000));
            });
            
            // メッセージ数のカウントアップ
            message_counter_num += message_list.length;
            $('#message_counter').text('総発言数 : ' + message_counter_num);
        }
        
        // チャット部屋情報更新処理
        var board_info = res.data['board_info'];

        // ユーザー情報更新処理
        user_vibes = res.data['user_info'].user_vibes;
        updateUserInfo();

        // ヘイトの更新
        //メッセージのの件数を絞る
        var message_hate = res.data['message_hate'];

		//メッセージの件数取得
        var len = 0;
		$('.message').each(function(i){
			len++;
		});		

		// n件以下になるまで削除
        while(len > 20){
            target = $('.message').filter(":last");
            id = target.val();
            delete message_hate[id];
			target.css({left:"0", opacity:"1.0"}).animate({left:"-100px", opacity:"0.0"}, 500).queue(function(){
				target.remove();
			});
            len--;
        }

        // ヘイトの更新.削除
        $('.message').each(function(i){
            id = $(this).children("input[name=id]").val();
            $(this).children("input[name=hate]").val(message_hate[id]);
            hate = $(this).children("input[name=hate]").val();
            if(hate > 10){
                $(this).css({left:"0", opacity:"1.0"}).animate({left:"-100px", opacity:"0.0"}, 500).queue(function(){
					$(this).remove();
				});
                delete message_hate[id];
            }
        });
                
        //ヘイト初期化
        for(var value in message_hate){
            message_hate[value] = 0;
        }
        hates = message_hate; 

        // ログインユーザー更新処理
        var login_users = res.data['login_users'];
        $login_users_counter = $('#login_users_counter');
        $login_users_counter.text('ユーザー数 : ' + login_users.length);

        // 熱量更新
        updateMessageVibes();
    });
}

//メッセージにクリックイべ追加 動的に追加したものにも対応
var timeout;
$(document).on("click", ".message", function(){
    hate = $(this).children("input[name=id]").val();
		if(!hates[hate]){
			hates[hate] = 1; 
		} else {
			hates[hate] += 1;
		}
    $this = $(this);
    $this.jrumble();
    clearTimeout(timeout);
    $this.trigger('startRumble');
    timeout = setTimeout(function(){$this.trigger('stopRumble');}, 1500)
    console.log("なう");
});

// メッセージクラス
class Message {
    constructor(id, message, image_url, vibes, message_hate) {
        this.id = id;
        this.message = message;
        this.image_url = image_url;
        this.vibes = vibes;
        this.message_hate = message_hate;
    }
}

// メッセージ<li>要素の生成
// 返り値が<li>要素なので好きな<ul>に追加してね
function createMessageLi(message) {
    // 例) <li class="list-group-item my-2"><p></p><img></li>
    var messageLi = $('<li></li>', {
        'class': 'list-group-item my-2 message',
    });

    // テキスト要素を追加
    messageLi.append('<p>' + AutoLink(message.message) + '</p>');

    // 画像添付があれば<img>要素を追加
    if (message.image_url) {
        messageLi.append($('<img>', {
            'src': message.image_url,
            'class': 'img-thumbnail',
        }));
    }

    // 熱量のメタデータ要素を追加
    messageLi.append($('<input></input>', {
        'type': 'hidden',
        'name': 'vibes',
        'value': String(message.vibes),
    }));

    // クリック数のメタデータ要素を追加
    messageLi.append($('<input></input>', {
        'type': 'hidden',
        'name': 'hate',
        'value': String(message.message_hate),
    }));

    // クリック数のメタデータ要素を追加
    messageLi.append($('<input></input>', {
        'type': 'hidden',
        'name': 'id',
        'value': String(message.id),
    }));

    // クリック数加算イベント
    messageLi.on('click', function(){
        hate = $(this).children('input[name=id]').val();
        if(!hates[hate]){
            hates[hate] = 1;
        } else {
            hates[hate] += 1;
        }
    });

    return messageLi;
}

// ユーザー情報の更新処理
function updateUserInfo() {
    // 熱量の更新
    $('#user_vibes').text('熱量: ' + Math.floor(user_vibes));
    //ゲージ変動のアニメーション
    $('#gauge').animate({})
}

// メッセージの熱量に応じてメッセージのスタイルを変更
function updateMessageVibes() {
    var message_list = $('.message');
    $.each(message_list, function(index, message) {
        var vibes = $(message).find('input[name="vibes"]').val();

        if (vibes > 0) {
            if (vibes < 10) {
                //vibes = '0' + vibes;
            }
            var color = '#' + vibes + '00';
            $(message).animate({
                'fontSize': '2em',
                'color': color,
            }, 1000);
        }
    });
}

// 文字列からURLを判別してaタグに変換する
function AutoLink(str) {
    var regexp_url = /((h?)(ttps?:\/\/[a-zA-Z0-9.\-_@:/~?%&;=+#',()*!]+))/g; // ']))/;
    var regexp_makeLink = function(all, url, h, href) {
        return '<a href="h' + href + '">' + url + '</a>';
    }

    return str.replace(regexp_url, regexp_makeLink);
}
