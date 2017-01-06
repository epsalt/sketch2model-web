$(document).ready(function(){

    $("#img_preview").error(function () {
        $(this).hide();
    });

    if(document.getElementById('example').checked){
        $("#upload_form").hide();
        $("#upload_btn").hide();
    } else {
        $("#example_form").hide();
        $("#img_container").hide();
    }

    $("input[name$='options']").change(function() {
        $("#upload_form").toggle();
        $("#example_form").toggle();
        $("#img_container").toggle();
        $("#upload_btn").toggle();
        $("#img_preview").toggle();

    });

    $("#examples").click(function() {
        var selected = $(this).val();
        var s3_url = "https://s3-us-west-2.amazonaws.com/sketch2model/examples/";
        $("#img_example").attr("src", s3_url + selected + ".png");
    });

});

var image_preview = function(event) {
    var preview = document.getElementById('img_preview');
    preview.src = URL.createObjectURL(event.target.files[0]);
    preview.style.display = "inline";
};
