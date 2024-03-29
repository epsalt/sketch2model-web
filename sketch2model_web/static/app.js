$(document).ready(function () {
  $("img").error(function () {
    $(this).hide();
  });

  if (document.getElementById("example").checked) {
    $("#upload_form").hide();
    $("#upload_btn").hide();
  } else {
    $("#example_form").hide();
    $("#img_container").hide();
  }

  $("input[name$='options']").change(function () {
    $("#upload_form").toggle();
    $("#example_form").toggle();
    $("#img_container").toggle();
    $("#upload_btn").toggle();
    $("#img_preview").toggle();
  });

  $("#examples").change(function () {
    var selected = $(this).val();
    $("#img_example").attr("src", "/static/" + selected + ".png");
  });
});

var image_preview = function (event) {
  var preview = document.getElementById("img_preview");
  preview.src = URL.createObjectURL(event.target.files[0]);
  preview.style.display = "inline";
};

$("#app_form").submit(function (e) {
  $("#submit_button").html(
    '<span class="glyphicon glyphicon-cog" aria-hidden="true"></span> Working...'
  );
  $.ajax({
    url: "/app/post",
    type: "POST",
    data: new FormData(this),
    processData: false,
    contentType: false,
    success: function (response) {
      $("#submit_button").html("Submit");
      if (response.ok == true) {
        $("#img_output").attr("src", "data:image/png;base64," + response.img);
        $("#success_note").show();
        $("#img_output").show();
        $("#error_container").hide();
      } else {
        $("#error_note").text(response.error);
        $("#success_note").hide();
        $("#img_output").hide();
        $("#error_container").show();
      }
    },
  });
  e.preventDefault();
});
