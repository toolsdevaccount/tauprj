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

// 手配先と仕入先を連動する（手配先を選択したら仕入先にも同様のコードをセットする
$('input[id=id_DestinationCode]').on('change', function () {
    // 手配先
    DestVal = $(this).val();
    Destlbl = $("#Destination option[value='" + $(this).val() + "']").prop('label');
    // 仕入先へ
    $("#id_SupplierCode").val(DestVal);
    $('input:hidden[id="id_SupplierCode"]').val(Destlbl);
});

// 出荷先と得意先を連動する（出荷先を選択したら得意先にも同様のコードをセットする
$('input[id=id_ShippingCode]').on('change', function () {
    id = document.getElementById('id_OutputDiv').value;                     //出力区分
    if(id != '3'){
        // 出荷先
        ShipVal = $(this).val();
        Shiplbl = $("#Shipping option[value='" + $(this).val() + "']").prop('label');
        // 得意先へ
        $("#id_CustomeCode").val(ShipVal);
        $('input:hidden[id="id_CustomeCode"]').val(Shiplbl);
    }
});

// 製品受発注入力の手配先と仕入先を連動する（手配先を選択したら仕入先にも同様のコードをセットする
$('input[id=id_ProductOrderDestinationCode]').on('change', function () {
    // 手配先
    DestVal = $(this).val();
    Destlbl = $("#ProductOrderDestination option[value='" + $(this).val() + "']").prop('label');
    // 仕入先へ
    $("#id_ProductOrderSupplierCode").val(DestVal);
    $('input:hidden[id="id_ProductOrderSupplierCode"]').val(Destlbl);
});

// 製品受発注入力の出荷先と得意先を連動する（出荷先を選択したら得意先にも同様のコードをセットする
$('input[id=id_ProductOrderShippingCode]').on('change', function () {
    // 出荷先
    ShipVal = $(this).val();
    Shiplbl = $("#ProductOrderShipping option[value='" + $(this).val() + "']").prop('label');
    // 得意先へ
    $("#id_ProductOrderCustomeCode").val(ShipVal);
    $('input:hidden[id="id_ProductOrderCustomeCode"]').val(Shiplbl);
});