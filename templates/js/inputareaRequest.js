$(function(){
    $('#form').submit(function(event) {
        //フォームを送信する直前 tableの行数を取得
        var row = tblrow.rows.length -1;                    //表題分差引く
        $('[name=OrderingId-TOTAL_FORMS]').val(row);        // 行数を書き換えてPOST

        //明細行選択チェック
        var table = document.querySelector("table");
        var tr = table.querySelectorAll("tr");
        for(var i = 0; i < tr.length; i++) {
            var item = tr[i].style.backgroundColor;
        }

        if(item==''){
            alert("明細行が選択されていません.");
            return false;   
        }

        event.preventDefault();
        var form = $(this);
        $.ajax({
            url: form.prop('action'), 
            method: form.prop('method'), 
            data: form.serialize(), 
            timeout: 10000, 
            dataType: 'json', 
        })
        .done(function(received_data) {
            var answer = received_data['answer'];

            html = '';
            html = html + '<li class="alert alert-success list-unstyled alert-dismissible fade show" role="alert" id="fadeout">' + answer ;
            html = html + '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
            html = html + '<span aria-hidden="true">&times;</span>';
            html = html + '</button>';
            html = html + '</li>';

            $('#answer').html(html);

            window.setTimeout("$('#fadeout').fadeOut()", 2000);
        })

        .fail(function(xhr) {
            var answer = xhr.responseText;

            html = '';
            html = html + '<li class="alert alert-danger list-unstyled alert-dismissible fade show" role="alert" id="fadeout">' + answer ;
            html = html + '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
            html = html + '<span aria-hidden="true">&times;</span>';
            html = html + '</button>';
            html = html + '</li>';
            $('#answer').html(html);

        });
    });

    $('#list').addInputArea({
        after_add: function () {
            var tbl = document.querySelector('#tblrow');
            var num = tbl.querySelectorAll('.ResultItemNumber').length;
            var item = tbl.querySelectorAll('.ResultItemNumber')[num -2].value;
                item = parseInt(item ,10);

            // 項番に前ゼロ付加
            var result = item.toString().padStart( 4, '0');
            tbl.querySelectorAll('.ResultItemNumber')[num -1].value = result;

            // OrderingDetailId取得し、追加行に設定する
            var id = document.getElementById('id_OrderingId-' + [num -2] + '-OrderingDetailId').value;
            document.getElementById('id_OrderingId-' + [num -1] + '-OrderingDetailId').value = id;

            // id値削除
            list = document.getElementById('id_OrderingId-' + [num -1] + '-id');
            list.remove();

            // 初期値に0を送信
            tbl.querySelectorAll('.ShippingVolume')[num -1].value = '0.00';

            // flatpickr
            const config = {
                'locale' : 'ja',
                allowInput : true,
                dateFormat : 'Y-m-d', 
            }
            flatpickr('.flatpickr',config);
        }
    });
});
