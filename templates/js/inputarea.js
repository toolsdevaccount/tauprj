$(function(){
    $('#form').submit(function() {  	 // フォームを送信する直前 tableの行数を取得
        //数量のカンマを取り除く
        $(".DetailVolume").each(function() {
            $(this).val(removeCommaVolume($(this).val()));
        });

        //仕入単価のカンマを取り除く
        $(".DetailUnitPrice").each(function() {
            $(this).val(removeComma($(this).val()));
        });

        //通常単価のカンマを取り除く
        $(".DetailPrice").each(function() {
            $(this).val(removeComma($(this).val()));
        });

        //UP分単価のカンマを取り除く
        $(".DetailOverPrice").each(function() {
            $(this).val(removeComma($(this).val()));
        });

        //販売単価のカンマを取り除く
        $(".DetailSellPrice").each(function() {
            $(this).val(removeComma($(this).val()));
        });

        var row = tblrow.rows.length -1; //表題分差引く
        $('[name=OrderingTableId-TOTAL_FORMS]').val(row); // 行数を書き換えてPOST
    });

    $('#list').addInputArea({
        after_add: function () {
            var tbl = document.querySelector('#tblrow');
            var num = tbl.querySelectorAll('.DetailItemNumber').length;
            var item = tbl.querySelectorAll('.DetailItemNumber')[num -2].value;
                item = parseInt(item ,10) +1;
            var result = item.toString().padStart( 4, '0');

            tbl.querySelectorAll('.DetailItemNumber')[num -1].value = result;
            // 初期値に0を送信
            tbl.querySelectorAll('.DetailVolume')[num -1].value = 0;
            tbl.querySelectorAll('.DetailUnitPrice')[num -1].value = 0;
            tbl.querySelectorAll('.DetailPrice')[num -1].value = 0;
            tbl.querySelectorAll('.DetailOverPrice')[num -1].value = 0;
            tbl.querySelectorAll('.DetailSellPrice')[num -1].value = 0;

            tbl.querySelectorAll('.PrintDiv')[num -1].checked = true;

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

$('.DeliveryManageDiv').click(function() {
    if($(".DeliveryManageDiv").prop('checked')){
        $(".DeliveryManageDiv").val(1);
    } else {
        $(".DeliveryManageDiv").val(0);
    }           
});

$('.PrintDiv').click(function() {
    if($(".PrintDiv").prop('checked')){
        $(".PrintDiv").val(1);
    } else {
        $(".PrintDiv").val(0);
    }           
});