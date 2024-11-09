$(function(){
    $('#form').submit(function(event) {
        event.preventDefault();
        var form = $(this);
        $.ajax({
            url: "/unpaid/update", 
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
});