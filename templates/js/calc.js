// 指定したエレメント(input)が所属する行(tr)を取得
function detail(obj)
{
    // return obj.parentElement.parentElement.parentElement;
    return obj.parentElement.parentElement;
}

// 指定したエレメント(input)と同じ行にある数量を取得
function volume(obj)
{
    return removeComma(detail(obj).querySelectorAll(".DetailVolume")[0].value);
}

// 指定したエレメント(input)と同じ行にある仕入単価を取得
function UnitPrice(obj)
{
    return removeComma(detail(obj).querySelectorAll(".DetailUnitPrice")[0].value);
}

// 指定したエレメント(input)と同じ行にある単価を取得
function price(obj)
{
    return removeComma(detail(obj).querySelectorAll(".DetailPrice")[0].value);
}

// 指定したエレメント(input)と同じ行にあるUP分単価を取得
function overprice(obj)
{
    return removeComma(detail(obj).querySelectorAll(".DetailOverPrice")[0].value);
}

function comma(obj)
{
    //桁区切りして配置（仕入単価）
    detailunitprice = Number(UnitPrice(obj)).toLocaleString();
    detail(obj).querySelectorAll(".DetailUnitPrice")[0].value = detailunitprice;
}

// 指定したエレメント(input)の横計を再計算してから取得
function calc(obj)
{
    // 単価にカンマをつける
    detailprice = Number(price(obj)).toLocaleString();

    if (isNaN(price(obj))){
        detailprice=0;
    }else{
        detail(obj).querySelectorAll(".DetailPrice")[0].value = detailprice;
    }

    // UP分単価にカンマをつける
    detailoverprice = Number(overprice(obj)).toLocaleString(); 

    if (isNaN(overprice(obj))){
        detailoverprice=0;
    }else{
        detail(obj).querySelectorAll(".DetailOverPrice")[0].value = detailoverprice;
    }

    if(Number(overprice(obj))==0){       
        detail(obj).querySelectorAll(".DetailOverPrice")[0].value = 0; 
    } 

    // 計算
    result = Number(price(obj)) + Number(overprice(obj));

    if (isNaN(result)){
        result=0;
    }

    // 計算結果にカンマをつける
    detail(obj).querySelectorAll(".DetailSellPrice")[0].value = result.toLocaleString();

    return result ;
}

function removeComma(number) {
    var removed = number.replace(/,/g, '');
    return parseInt(removed, 10);
}

function removeCommaVolume(number) {
    var removed = number.replace(/,/g, '');
    return Number.parseFloat(removed).toFixed(2)
}

function order(obj)
{		
    var item = document.getElementById('id_OrderNumber').value ;
    result = item.toString().padStart( 7, '0');
    document.getElementById('id_OrderNumber').value = result;
}

function Productorder(obj)
{		
    var item = document.getElementById('id_ProductOrderOrderNumber').value ;
    result = item.toString().padStart( 7, '0');
    document.getElementById('id_ProductOrderOrderNumber').value = result;
}

function ItemNumber(obj)
{		
    var item = detail(obj).querySelectorAll(".DetailItemNumber")[0].value;
    var Result = item.toString().padStart( 4, '0'); 
    detail(obj).querySelectorAll(".DetailItemNumber")[0].value = Result;
}

function ResultItemNumber(obj)
{		
    var item = detail(obj).querySelectorAll(".ResultItemNumber")[0].value;
    var Result = item.toString().padStart( 4, '0'); 
    detail(obj).querySelectorAll(".ResultItemNumber")[0].value = Result;
}

function financial(obj) {

    var item = detail(obj).querySelectorAll(".DetailVolume")[0].value;
    var Result =  Number.parseFloat(item).toFixed(2);
    if (isNaN(Result)){
        Result=0;
    }

    detail(obj).querySelectorAll(".DetailVolume")[0].value = Result;
}

function financial_shipp(obj) {
    var num = detail(obj).querySelectorAll('.ShippingVolume').length;
    for (i = 0; i < num; i++) {
        var item = detail(obj).querySelectorAll('.ShippingVolume')[i].value;
        var Result =  Number.parseFloat(item).toFixed(2);
        detail(obj).querySelectorAll(".ShippingVolume")[i].value = Result;
    }
}

  const input = document.querySelector('input')

input.checked = true
