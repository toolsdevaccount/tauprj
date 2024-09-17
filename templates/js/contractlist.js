// Modalウィンドウを制御

var btn = document.getElementById('modalOpen');
var cls = document.getElementById('modalClose');
var ise = document.getElementById('issue');
var modal = document.getElementsByClassName('modal fade');

btn.addEventListener('click', function() {
    for(i=0;i<modal.length;i++){
        modal[i].style.opacity = '1';
        modal[i].style.visibility = 'visible';
    }
})

ise.addEventListener('click', function() {
    var TargetMonth = document.getElementById('id_TargetMonth').value;
    var ManagerCode = document.querySelector(`input[type=hidden][name="Manager"]`).value;

    if(ManagerCode=='' || ManagerCode==="undefined"){
        alert('担当者が選択されていません');
        return false;
    }

    var url = "/contract/list/123/456";

    TargetMonth = TargetMonth.replace(/年/g,'');
    TargetMonth = TargetMonth.replace(/月/g,'');
    TargetMonth = TargetMonth + '01';

    url = url.replace(/123/,TargetMonth);
    url = url.replace(/456/,ManagerCode);

    location.href = url;
})
// プルダウン選択後idをセット
$('input[name=Manager]').on('change', function () {
    document.querySelector(`input[type=hidden][name="Manager"]`).value = $("#ManagerCode option[value='" + $(this).val() + "']").prop('label');
});
output.addEventListener('click', function() {
    var TargetMonth = document.getElementById('id_TargetMonth').value;
    var ManagerCode = document.querySelector(`input[type=hidden][name="Manager"]`).value;

    if(ManagerCode=='' || ManagerCode==="undefined"){
        alert('担当者が選択されていません');
        return false;
    }

    var url = "/contract/Excel/123/456";

    TargetMonth = TargetMonth.replace(/年/g,'');
    TargetMonth = TargetMonth.replace(/月/g,'');
    TargetMonth = TargetMonth + '01';

    url = url.replace(/123/,TargetMonth);
    url = url.replace(/456/,ManagerCode);

    //console.log(url);
    location.href = url;
})
