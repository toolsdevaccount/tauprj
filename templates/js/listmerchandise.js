function merchandiseedit(id,row){
	var url = "/merchandise/edit/123456/456789/";
	url = url.replace(/123456/,id);
	url = url.replace(/456789/,row);

	location.href = url;
}

function merchandisedelete(id,row){
	var url = "/merchandise/delete/123456/456789/";
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
