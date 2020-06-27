var RSMP_CATEGORY = {"1":"Микропредприятие","2":"Малое предприятие","3":"Среднее предприятие"};

function getCategory(category){
    return RSMP_CATEGORY[category];
}

$(document).ready(function() {
    $("#query").change(function(){
        var number = $(this).val();
        var dataType = "";
        if (number.length == 13){
            dataType = "ОГРН";
        }
        else if (number.length == 10){
            dataType = "ИНН Юр. лица";
        }
        else if (number.length == 12){
            dataType = "ИНН физ. лица";
        }
        else{
            dataType = "некорректный номер";
        }
        $("#dataType").html("Вы ввели: " + dataType);
    });
    $("#submit").click(function(){
        if ($("#radio_get").prop("checked")) {
            $.get("search.html", function(data) {
                var results = JSON.parse(decodeURIComponent(escape(data)));
                var table_data = "";
                for (var t in results){
                    if(results[t]["status"] == 0){
                        table_data += `<tr class="bad">
                            <td>`+t+`</td>
                            <td>Нет</td>
                            <td>`+results[t]["dtQueryBegin"]+`</td>
                        </tr>`;
                    }
                    else{
                        var category = getCategory(results[t]["category"]);
                        var background_class = "good";
                        if (category == "Микропредприятие"){
                            background_class = "bad"
                        }
                        table_data += `<tr class="`+background_class+`">
                            <td>`+t+`</td>
                            <td>`+category+`</td>
                            <td>`+results[t]["dtQueryBegin"]+`</td>
                        </tr>`;
                    }
                }
                $("#searchResults").html(`<table border="1">
                    <caption>История поиска</caption>
                    <tr>
                    <th>Номер (ИНН или ОГРН)</th>
                    <th>Категория</th>
                    <th>Дата поиска</th>
                    </tr>`+table_data+`
                </table>`);
            });
        }
        else{
            var query_len = $("#query").val().length;
            if ((query_len == 13 || query_len == 12 || query_len == 10) && parseInt($("#query").val()) >= 0){
                $.post("index.html", $("#query").val()).done(function( data ) {
                    if (data != "Не найдено"){
                        data = getCategory(data);
                    }
                    $("#searchResult").html("Результат поиска: " + data);
                });
            }
            else {
                alert("Некорректный ввод");
            }
        }
    });
});