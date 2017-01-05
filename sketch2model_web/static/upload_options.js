$(document).ready(function(){
    $("#upload_form").hide();

    $("input[name$='options']").click(function() {
        var selected = $(this).val();
        if(selected == "upload"){
            $("#upload_form").show();
            $("#example_form").hide();
            $("#img_container").hide();
        } else {
            $("#example_form").show();
            $("#img_container").show();
            $("#upload_form").hide();
        }
    });

    $("#examples").click(function() {
        var selected = $(this).val();
        var s3_url = "https://s3-us-west-2.amazonaws.com/sketch2model/examples/";
        $("#img_example").attr("src", s3_url + selected + ".png");
    });

});
