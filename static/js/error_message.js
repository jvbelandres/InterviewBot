$(function (){
    $('#register input[type="email"]').on("input", function(){
        $('.error_message').hide();
    });
});