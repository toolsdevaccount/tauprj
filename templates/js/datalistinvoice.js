// プルダウン(datalist)のlabel値をoutputに転記
document.addEventListener ('input', (event)=> {
    let
    e = event.target,
    list = e.list;

    if (list) {
    let
        option = list.querySelector (`option[value="${e.value}"]`),
        output = document.querySelector (`input[type=hidden][name="${e.name}"]`);
    if(option && output)
        output.value = option.label;
    }

}, true);

function loadFinished(){
    var item = document.getElementById('id_InvoiceCustomerCode_Max').value;
    document.getElementById('id_InvoiceCustomerCode_To').value=item;

    var result = document.getElementById('id_InvoiceCustomerid').value;
    document.querySelector (`input[type=hidden][name="InvoiceCustomerCode_To"]`).value=result;
}
window.addEventListener('load', loadFinished);