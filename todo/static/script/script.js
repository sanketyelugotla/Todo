document.addEventListener("DOMContentLoaded", function () {
    const loginBtn = document.getElementById('loginBtn');
    const loginDialog = document.getElementById('loginDialog');


    loginBtn.addEventListener('click', () => {
        loginDialog.classList.toggle('open');
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const signupBtn = document.getElementById('signupBtn');
    const signupDialog = document.getElementById('signupDialog');


    signupBtn.addEventListener('click', () => {
        signupDialog.classList.toggle('open');
    });
});


function login_closeDialog() {
    const loginDialog = document.getElementById('loginDialog');
    loginDialog.classList.remove('open');
}

function signup_closeDialog() {
    const signupDialog = document.getElementById('signupDialog');
    signupDialog.classList.remove('open');
}

function logout() {
    window.location.replace("/");
}