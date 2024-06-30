// my_flask_app/app/static/js/togglePassword/js//

function togglePassword() {
    var passwordField = document.getElementById("password");
    if (passwordField) {
        if (passwordField.type === "password") {
            passwordField.type = "text";
        } else {
            passwordField.type = "password";
        }
    } else {
        console.error("Password field not found!");
    }
}
