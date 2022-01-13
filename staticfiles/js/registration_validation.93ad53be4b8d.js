var password = $("#pass")[0]
    , confirm_password = $("#pass2")[0];

function validatePassword(){
    if(password.value != confirm_password.value) {
        $("#pass2")[0].setCustomValidity("Your password must match.");
        $("#pass2")[0].reportValidity();
    } else {
        $("#pass2")[0].setCustomValidity('');
        $("#pass2")[0].reportValidity();
    }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;

function limit_input() {
    var field = document.getElementById("phone");
    var max_length = 11;
    if (field.value.length > max_length) {
        field.value = field.value.slice(0, max_length); 
    }
}