function orderingedit(id,row){
	var url = "/ordering/edit/123456/456789/";
	url = url.replace(/123456/,id);
	url = url.replace(/456789/,row);

	location.href = url;
}

function orderingdelete(id,row){
	var url = "/ordering/delete/123456/456789/";
	url = url.replace(/123456/,id);
	url = url.replace(/456789/,row);

	location.href = url;
}

function orderingpdf(id){
	var url = "/ordering/pdf/123456/";
	url = url.replace(/123456/,id);

	//location.href = url;
	window.open(url, '_blank');
}

function requestedit(id,row){
	var url = "/requestresult/edit/123456/456789/";
	url = url.replace(/123456/,id);
	url = url.replace(/456789/,row);

	location.href = url;
}

document.addEventListener("DOMContentLoaded", function() {
    var url = new URL(window.location.href);
    // URLSearchParamsオブジェクトを取得
    var params = url.searchParams;
    // getメソッド
    row=params.get('row');
    for(var i = 0; i < tr.length; i++) {
        if(i==row){
            // 画面遷移前に選択した行の背景色を変更する
            tr[i].style.backgroundColor = "#eef";
        }
    }
});
