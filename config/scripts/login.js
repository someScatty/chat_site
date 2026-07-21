console.log("yup, this fires")

const usernameField = document.getElementById("user");
const passwordField = document.getElementById("password");

const loginButton = document.getElementById("login");
const signupButton = document.getElementById("signup");

const errorMessageText = document.getElementById("errors");

import "/scripts/api.js";
document.chatAPI = new Chatify();

console.log(document.chatAPI.baseURL);

function redirect(extension) {
    window.location.href = document.chatAPI.baseURL + extension;
}
function setCookies(tokanic) {
    document.cookie = "V2token=" + tokanic.session_token;
    document.cookie = "userID=" + tokanic.id; // theres GOTTA be a better way
    console.log(document.cookie)
}

async function Login() {
    // console.log("attempt1");
    const username = usernameField.value;
    const password = passwordField.value;

    const loginWait = await document.chatAPI.login(username, password);
    console.log(loginWait);

    if (loginWait.success) {
        // console.log("LOGGED IN! you can move on now, " + username);
        setCookies(loginWait);
        // console.log(document);
        redirect("/chat");
    } else {
        console.error(loginWait.error);
        errorMessageText.innerHTML = loginWait.error;
    }
}
async function SignUp() {
    // console.log("irony lives and breathes in rest in grief its her or me");
    const username = usernameField.value;
    const password = passwordField.value;

    const signupWait = await document.chatAPI.signUp(username, password);
    console.log(signupWait);

    if (signupWait.success) {
        // console.log("nice one, " + username);
        setCookies(signupWait);
        redirect("/chat");
    } else {
        console.error(signupWait.error);
        errorMessageText.innerHTML = signupWait.error;
    }
}

loginButton.addEventListener("click", Login);
signupButton.addEventListener("click", SignUp);
// console.log(document);