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
    var row = document.getElementById(`id_order`).value;
    var array = [];

    TargetMonth = TargetMonth.replace(/年/g,'');
    TargetMonth = TargetMonth.replace(/月/g,'');
    TargetMonth = TargetMonth + '01';

    //オーダーNOを配列に格納
    var string = ""
    for (var i = 0; i < row; ++i) {
        array.push(document.getElementById(`inputform_` + i).value);
        if(array[i]!=''){
            string = string + "&row=" + array[i];
        }
    }

    //urlを加工
    var url = "/stock/list?Target=" + TargetMonth;

    url = url + string;
    location.href = url;
})

output.addEventListener('click', function() {
    var TargetMonth = document.getElementById('id_TargetMonth').value;

    TargetMonth = TargetMonth.replace(/年/g,'');
    TargetMonth = TargetMonth.replace(/月/g,'');
    TargetMonth = TargetMonth + '01';

    var url = "/stock/Excel?Target=" + TargetMonth;

    //console.log(url);
    location.href = url;
})
// Input追加
var i = 1 ;
function addForm() {
    var input_data = document.createElement('input');
    input_data.type = 'text';
    input_data.className = 'form-control text-right';
    input_data.name = 'area';
    input_data.id = 'inputform_' + i;
    input_data.placeholder = 'オーダーNo';
    input_data.autocomplete = 'new-password';
    var parent = document.getElementById('form_area');
    parent.appendChild(input_data);
    document.getElementById(`id_order`).value=i+1;
    i++ ;   
}
