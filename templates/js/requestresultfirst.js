$(document).ready(function(){
    var id = document.querySelectorAll(".OrderingId")[0].value;
    var item = document.querySelectorAll(".DetailItemNumber")[0].value;
    var texthtml = '';

	$('#list').empty();

	// Ajax通信を開始
	$.ajax({
		url: "/requestresult/edit/exec_result",
		method: "GET",
		dataType: 'json',
		data: {
			param: id,
		},
		timeout: 5000,
	})
	// 通信成功時の処理を記述
	.done(function(response) {
        if(response.list.length==0){
			// 項番作成
			item = parseInt(item ,10);
			var result = item.toString().padStart( 4, '0');
			//HTML要素
			texthtml = ''
			texthtml = texthtml + '<tr class="list_var">';
			texthtml = texthtml + '	<td id="detail"> ';
			texthtml = texthtml + '		<input type="hidden" data-id-format="id_OrderingId-%d-id" data-name-format="OrderingId-%d-id" name="OrderingId-0-id" id="id_OrderingId-0-id">';
			texthtml = texthtml + '		<input type="hidden" class="OrderingDetailId" data-id-format="id_OrderingId-%d-OrderingDetailId" data-name-format="OrderingId-%d-OrderingDetailId" name="OrderingId-0-OrderingDetailId" id="id_OrderingId-0-OrderingDetailId" value="' + id + '">';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '	<td class="text-center">';
			texthtml = texthtml + '		<div class="form-check">';
			texthtml = texthtml + '			<input type="checkbox" class="form-check-input position-static" data-id-format="id_OrderingId-%d-DELETE" data-name-format="OrderingId-%d-DELETE" id="id_OrderingId-0-DELETE" name="OrderingId-0-DELETE">';
			texthtml = texthtml + '		</div>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '	<td><input type="tel" class="form-control ResultItemNumber" autocomplete="new-password" style="text-align: right;" data-id-format="id_OrderingId-%d-ResultItemNumber" data-name-format="OrderingId-%d-ResultItemNumber" name="OrderingId-0-ResultItemNumber" id="id_OrderingId-0-ResultItemNumber" value=' + result + '></td>';
			texthtml = texthtml + '	<td><input type="tel" class="form-control ResultDate" autocomplete="new-password" data-id-format="id_OrderingId-%d-ResultDate" data-name-format="OrderingId-%d-ResultDate" name="OrderingId-0-ResultDate" id="id_OrderingId-0-ResultDate" value=""></td>';
			texthtml = texthtml + '	<td><input type="tel" class="form-control ShippingDate" autocomplete="new-password" data-id-format="id_OrderingId-%d-ShippingDate" data-name-format="OrderingId-%d-ShippingDate" name="OrderingId-0-ShippingDate" id="id_OrderingId-0-ShippingDate" value=""></td>';                                  
			texthtml = texthtml + '	<td><input type="tel" step="0.1" class="form-control ShippingVolume text-right" autocomplete="new-password" data-id-format="id_OrderingId-%d-ShippingVolume" data-name-format="OrderingId-%d-ShippingVolume" name="OrderingId-0-ShippingVolume" id="id_OrderingId-0-ShippingVolume" data-empty-val="false" onchange="financial_shipp(this);" value="0.00"></td>';
			texthtml = texthtml + '	<td><input type="tel" class="form-control SlipNumber text-right" autocomplete="new-password" data-id-format="id_OrderingId-%d-SlipNumber" data-name-format="OrderingId-%d-SlipNumber" name="OrderingId-0-SlipNumber" id="id_OrderingId-0-SlipNumber" value=""></td>';
			texthtml = texthtml + '	<td><input type="text" class="form-control" autocomplete="new-password" data-id-format="id_OrderingId-%d-ResultSummary" data-name-format="OrderingId-%d-ResultSummary"	name="OrderingId-0-ResultSummary" id="id_OrderingId-0-ResultSummary" value=""}}></td>';
			texthtml = texthtml + '	<td class="text-center">';
			texthtml = texthtml + '		<div class="form-check">';
			texthtml = texthtml + '			<input type="checkbox" class="form-check-input ResultMoveDiv" data-id-format="id_OrderingId-%d-ResultMoveDiv" data-name-format="OrderingId-%d-ResultMoveDiv" id="id_OrderingId-0-ResultMoveDiv" name="OrderingId-0-ResultMoveDiv">';
			texthtml = texthtml + '		</div>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '	<td class="text-center">';
			texthtml = texthtml + '		<div class="form-check">';
			texthtml = texthtml + '			<input type="checkbox" class="form-check-input ResultGainDiv" data-id-format="id_OrderingId-%d-ResultGainDiv" data-name-format="OrderingId-%d-ResultGainDiv" id="id_OrderingId-0-ResultGainDiv" name="OrderingId-0-ResultGainDiv">';
			texthtml = texthtml + '		</div>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '	<td class="text-center">';
			texthtml = texthtml + '		<div class="form-check">';
			texthtml = texthtml + '			<input type="checkbox" class="form-check-input ResultDecreaseDiv" data-id-format="id_OrderingId-%d-ResultDecreaseDiv" data-name-format="OrderingId-%d-ResultDecreaseDiv" id="id_OrderingId-0-ResultDecreaseDiv" name="OrderingId-0-ResultDecreaseDiv">';
			texthtml = texthtml + '		</div>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '	<td>';
			texthtml = texthtml + '		<span class="list_del"><button type="button" class="btn btn-outline-danger btn-sm">削除</button></span>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '</tr>';
			$('#list').empty();
			$('#list').append(texthtml);
			// Formの値を書き換える
			$('input:hidden[name="OrderingId-TOTAL_FORMS"]').val(1);
			$('input:hidden[name="OrderingId-INITIAL_FORMS"]').val(0);
			// 出荷日datepicker
			var ShippingDate = document.getElementsByClassName('ShippingDate');
			var fp = flatpickr(ShippingDate, {
				'locale': 'ja',
				allowInput: true,
				// onCloseは入力フォームが閉じられた時に発火する
				onClose: (selectedDates, dateStr, instance) => {
					if (selectedDates.length === 1) {
						// プロパティにユーザーが選択した日付を代入
						this.dateProps = selectedDates[0];
					}
				}
			});
			// 実績日datepicker
			var ResultDate = document.getElementsByClassName('ResultDate');
			var fp = flatpickr(ResultDate, {
				'locale': 'ja',
				allowInput: true,
				// onCloseは入力フォームが閉じられた時に発火する
				onClose: (selectedDates, dateStr, instance) => {
					if (selectedDates.length === 1) {
						// プロパティにユーザーが選択した日付を代入
						this.dateProps = selectedDates[0];
					}
				}
			});
		}
		$.each(response.list, function(index, list) {
			texthtml = '';
			texthtml = texthtml + '<tr class="list_var">';
			texthtml = texthtml + '	<td id="detail"> ';
			texthtml = texthtml + '		<input type="hidden" data-id-format="id_OrderingId-%d-id" data-name-format="OrderingId-%d-id" name="OrderingId-' + index + '-id" id="id_OrderingId-' + index + '-id" value=' + list.id + '>';
			texthtml = texthtml + '		<input type="hidden" class="OrderingDetailId" data-id-format="id_OrderingId-%d-OrderingDetailId" data-name-format="OrderingId-%d-OrderingDetailId" name="OrderingId-' + index + '-OrderingDetailId" id="id_OrderingId-' + index + '-OrderingDetailId" value=' + id + '>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '	<td class="text-center">';
			texthtml = texthtml + '		<div class="form-check">';
			texthtml = texthtml + '			<input type="checkbox" class="form-check-input position-static" data-id-format="id_OrderingId-%d-DELETE" data-name-format="OrderingId-%d-DELETE" id="id_OrderingId-' + index + '-DELETE" name="OrderingId-' + index + '-DELETE">';
			texthtml = texthtml + '		</div>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '	<td><input type="tel" class="form-control ResultItemNumber" autocomplete="new-password" style="text-align: right;" data-id-format="id_OrderingId-%d-ResultItemNumber" data-name-format="OrderingId-%d-ResultItemNumber" name="OrderingId-' + index + '-ResultItemNumber" id="id_OrderingId-' + index + '-ResultItemNumber" value="' + list.ResultItemNumber + '"></td>';
			texthtml = texthtml + '	<td><input type="tel" class="form-control ResultDate" autocomplete="new-password" data-id-format="id_OrderingId-%d-ResultDate" data-name-format="OrderingId-%d-ResultDate" name="OrderingId-' + index + '-ResultDate" id="id_OrderingId-' + index + '-ResultDate" value="' + list.ResultDate + '"></td>';
			texthtml = texthtml + '	<td><input type="tel" class="form-control ShippingDate" autocomplete="new-password" data-id-format="id_OrderingId-%d-ShippingDate" data-name-format="OrderingId-%d-ShippingDate" name="OrderingId-' + index + '-ShippingDate" id="id_OrderingId-' + index + '-ShippingDate" value="' + list.ShippingDate + '"></td>';                                  
			texthtml = texthtml + '	<td><input type="tel" step="0.1" class="form-control ShippingVolume text-right" autocomplete="new-password" data-id-format="id_OrderingId-%d-ShippingVolume" data-name-format="OrderingId-%d-ShippingVolume" name="OrderingId-' + index + '-ShippingVolume" id="id_OrderingId-' + index + '-ShippingVolume" onchange="financial_shipp(this);" value="' + list.ShippingVolume + '"></td>';
			texthtml = texthtml + '	<td><input type="tel" class="form-control SlipNumber text-right" autocomplete="new-password" data-id-format="id_OrderingId-%d-SlipNumber" data-name-format="OrderingId-%d-SlipNumber" name="OrderingId-' + index + '-SlipNumber" id="id_OrderingId-' + index + '-SlipNumber" value="' + list.SlipNumber + '"></td>';
			texthtml = texthtml + '	<td><input type="text" class="form-control" autocomplete="new-password" data-id-format="id_OrderingId-%d-ResultSummary" data-name-format="OrderingId-%d-ResultSummary"	name="OrderingId-' + index + '-ResultSummary" id="id_OrderingId-' + index + '-ResultSummary" value="' + list.ResultSummary + '"></td>';
			texthtml = texthtml + '	<td class="text-center">';
			texthtml = texthtml + '		<div class="form-check">';
			if(list.ResultMoveDiv===true){
				texthtml = texthtml + '			<input type="checkbox" class="form-check-input position-static ResultMoveDiv" data-id-format="id_OrderingId-%d-ResultMoveDiv" data-name-format="OrderingId-%d-ResultMoveDiv" id="id_OrderingId-' + index + '-ResultMoveDiv" name="OrderingId-' + index + '-ResultMoveDiv" checked="checked">';
			}else{
				texthtml = texthtml + '			<input type="checkbox" class="form-check-input position-static ResultMoveDiv" data-id-format="id_OrderingId-%d-ResultMoveDiv" data-name-format="OrderingId-%d-ResultMoveDiv" id="id_OrderingId-' + index + '-ResultMoveDiv" name="OrderingId-' + index + '-ResultMoveDiv">';
			}
			texthtml = texthtml + '		</div>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '	<td class="text-center">';
			texthtml = texthtml + '		<div class="form-check">';
			if(list.ResultGainDiv===true){
				texthtml = texthtml + '			<input type="checkbox" class="form-check-input position-static ResultGainDiv" data-id-format="id_OrderingId-%d-ResultGainDiv" data-name-format="OrderingId-%d-ResultGainDiv" id="id_OrderingId-' + index + '-ResultGainDiv" name="OrderingId-' + index + '-ResultGainDiv" checked="checked">';
			}else{
				texthtml = texthtml + '			<input type="checkbox" class="form-check-input position-static ResultGainDiv" data-id-format="id_OrderingId-%d-ResultGainDiv" data-name-format="OrderingId-%d-ResultGainDiv" id="id_OrderingId-' + index + '-ResultGainDiv" name="OrderingId-' + index + '-ResultGainDiv">';

			}
			texthtml = texthtml + '		</div>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '	<td class="text-center">';
			texthtml = texthtml + '		<div class="form-check">';
			if(list.ResultDecreaseDiv===true){
				texthtml = texthtml + '			<input type="checkbox" class="form-check-input position-static ResultDecreaseDiv" data-id-format="id_OrderingId-%d-ResultDecreaseDiv" data-name-format="OrderingId-%d-ResultDecreaseDiv" id="id_OrderingId-' + index + '-ResultDecreaseDiv" name="OrderingId-' + index + '-ResultDecreaseDiv"  checked="checked">';
			}else{
				texthtml = texthtml + '			<input type="checkbox" class="form-check-input position-static ResultDecreaseDiv" data-id-format="id_OrderingId-%d-ResultDecreaseDiv" data-name-format="OrderingId-%d-ResultDecreaseDiv" id="id_OrderingId-' + index + '-ResultDecreaseDiv" name="OrderingId-' + index + '-ResultDecreaseDiv">';
			}
			texthtml = texthtml + '		</div>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '	<td>';
			texthtml = texthtml + '		<span class="list_del"><button type="button" class="btn btn-outline-danger btn-sm">削除</button></span>';
			texthtml = texthtml + '	</td>';
			texthtml = texthtml + '</tr>';

			$('#list').append(texthtml);
			// Formの値を書き換える
			$('input:hidden[name="OrderingId-INITIAL_FORMS"]').val([index +1]);
			// 出荷日datepicker
			var ShippingDate = document.getElementsByClassName('ShippingDate');
			var fp = flatpickr(ShippingDate, {
				'locale': 'ja',
				allowInput: true,
				// onCloseは入力フォームが閉じられた時に発火する
				onClose: (selectedDates, dateStr, instance) => {
					if (selectedDates.length === 1) {
						// プロパティにユーザーが選択した日付を代入
						this.dateProps = selectedDates[0];
					}
				}
			});
			// 実績日datepicker
			var ResultDate = document.getElementsByClassName('ResultDate');
			var fp = flatpickr(ResultDate, {
				'locale': 'ja',
				allowInput: true,
				// onCloseは入力フォームが閉じられた時に発火する
				onClose: (selectedDates, dateStr, instance) => {
					if (selectedDates.length === 1) {
						// プロパティにユーザーが選択した日付を代入
						this.dateProps = selectedDates[0];
					}
				}
			});

            var table = document.querySelector("table");
            var tr = table.querySelectorAll("tr");       
            table.addEventListener("load", function(e) {
                console.log('LOAD');
                if(e.target.tagName.toLowerCase() === "td") {
                    //まずは全て背景色白
                    for(var i = 0; i < tr.length; i++) {
                        tr[i].style.backgroundColor = "#f5f8fa";
                    }
                    var col = e.target.parentNode.rowIndex;
                    //選択行だけ色を変える
                    col.style.backgroundColor = "#eef";
                }
            }, false);       
		});
	})
	.fail(function() {
		// 通信失敗時の処理を記述
		$('#resultGET').text('GET処理失敗.');
	});
})
