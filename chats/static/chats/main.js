$(function() {
    // 定期処理
    var check = setInterval('updateMessage()', 3000);

    // メッセージ送信ボタンクリック処理
    $('#messageForm').submit(function(e) {
        $form = $('#messageForm');

        // ページ更新防止
        e.preventDefault();

        // 2重クリック防止
        var self = this;
        $(':submit', self).prop('disabled', true);
        setTimeout(function() {
            $(':submit', self).prop('disabled', false);
        }, 1000);

        // メッセージ送信
        $.ajax({
            url: $form.attr('action'),
            type: 'post',
            data: {
                board_id: board_id,
                profile_id: profile_id,
                text: $('#text').val(),
            },
            timeout: 10000,
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader('X-CSRFToken', $("input[name='csrfmiddlewaretoken']").val());
            },
        }).done(function(data, textStatus, jqXHR) {
            var $data = $(data);
            var $root = $('#contents');
            $root.empty();
            $root.append($data);
            updateMessage();
            $data.ready(function() {
            });
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
                var messageDiv = $("<div></div>", {
                    'class': 'message'
                });
                console.log(typeof message.pub_date, message.pub_date);
                console.log(typeof new Date(message.pub_date), new Date(message.pub_date));
                messageDiv.append('<p>投稿時間 : ' + message.pub_date + '</p>').append('<p>メッセージ : ' + message.message + '</p>');

                // listのDOMに追加する
                $('#message_list ul').prepend(messageDiv);
            });

            // メッセージ数のカウントアップ
            message_counter_num += message_list.length;
            $('#message_counter').text('総発言数 : ' + message_counter_num);
        }

        // チャット部屋情報更新処理
        var board_info = res.data['board_info'];
		console.log(board_info);

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

