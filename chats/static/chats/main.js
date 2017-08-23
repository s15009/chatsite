$(function() {
    // フォームの動き処理
    $('#text').on('click', function() {
        $('#submitBtn').show();
        $('#text').prop('rows', 2);
    });

    $('#text').on('keyup', function() {
        var text = $('#text');
        if (text.val() == '') {
            $('#submitBtn').prop('disabled', true);
        }
        else {
            $('#submitBtn').prop('disabled', false);
        }
        // テキストボックスのrowsの調整
        var return_num = text.val().match(/\n/gm);
        if (return_num) {
            text.prop('rows', (return_num.length + 2));
        }
        else {
            text.prop('rows', 2);
        }
    });

    $(document).on('click', function(e) {
        if (!$.contains($('#messageForm')[0], e.target) && $('#text').val() == '') {
            $('#submitBtn').hide();
            $('#text').prop('rows', 1);
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
            console.log('timer : ' + timer);
            window.location.href = window.location.href;
        }
        $('#timelimit').text('残り時間 : ' + timelimit);
    }, 100);

    // 定期処理
    var check = setInterval('updateMessage()', 3000);

    // メッセージ送信ボタンクリック処理
    $('#messageForm').submit(function(e) {
        var formData = new FormData();
        formData.append('board_id', board_id);
        formData.append('profile_id', profile_id);
        formData.append('text', $('#text').val());
        formData.append('file', $('#file').prop('files')[0]);

        // ページ更新防止
        e.preventDefault();

        // 2重クリック防止
        /*
        var self = this;
        $(':submit', self).prop('disabled', true);
        setTimeout(function() {
            $(':submit', self).prop('disabled', false);
        }, 1000);
        */

        // メッセージ送信
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
        }).done(function(data, textStatus, jqXHR) {
            // テキストフォームの初期化
            $('#text').val('');
            $('#submitBtn').prop('disabled', true);
            $('#text').prop('rows', 2);

            updateMessage();
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
        data: {latest_message_pub_date: latest_message_pub_date,
                latest_message_id: latest_message_id},
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
            latest_message_pub_date = latest_message.pub_date
            latest_message_id = latest_message.id;

            // メッセージ要素の追加
            $.each(message_list, function(index, message) {
                // メッセージ要素を生成
                // <li class="list-group-item my-2"><p></p></li>
                var messageLi = $("<li></li>", {
                    'class': 'list-group-item my-2'
                });
                messageLi.append('<p>' + AutoLink(message.message) + '</p>');
                if (message.image_url) {
                    messageLi.append('<img src="'+ message.image_url + '">');
                }

                // listのDOMに追加する
                $('#message_list ul').prepend(messageLi);
            });

            // メッセージ数のカウントアップ
            message_counter_num += message_list.length;
            $('#message_counter').text('総発言数 : ' + message_counter_num);
        }

        // チャット部屋情報更新処理
        var board_info = res.data['board_info'];

        // ログインユーザー更新処理
        var login_users = res.data['login_users'];
        $login_users_counter = $('#login_users_counter');
        $login_users_counter.text('ユーザー数 : ' + login_users.length);
    });

	function redirect(is_status) {	
		$.ajax({
			url: window.location.href + 'status',
			type:'post',	
			cache:'false',
			datatype: 'JSON',
            data:{
                is_status: is_status
            },
			beforeSend: function(xhr, settings) {
				xhr.setRequestHeader('X-CSRFToken', $("input[name='csrfmiddlewaretoken']").val());
			},
		}).done(function(res) {
			console.log(res);	
		});
	}
}

// 文字列からURLを判別してaタグに変換する
function AutoLink(str) {
    var regexp_url = /((h?)(ttps?:\/\/[a-zA-Z0-9.\-_@:/~?%&;=+#',()*!]+))/g; // ']))/;
    var regexp_makeLink = function(all, url, h, href) {
        return '<a href="h' + href + '">' + url + '</a>';
    }

    return str.replace(regexp_url, regexp_makeLink);
}
