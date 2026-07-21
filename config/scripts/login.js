console.log("yup, this fires")

const usernameField = document.getElementById("user");
const passwordField = document.getElementById("password");

const loginButton = document.getElementById("login");
const signupButton = document.getElementById("signup");

import "/scripts/api.js";
const chatAPI = new Chatify();

async function Login() {
    console.log("attempt1");
    const username = usernameField.value;
    const password = passwordField.value;

    const loginWait = await chatAPI.login(username, password);
    console.log(loginWait);

    if (loginWait.success) {
        console.log("LOGGED IN! you can move on now, " + username);
        // document.cookie = "V2token=" + loginWait.session_token;
        // document.cookie = "userID=" + loginWait.id; // theres GOTTA be a better way
    } else {
        console.error(loginWait.error);
    }
}
async function SignUp() {
    console.log("irony lives and breathes in rest in grief its her or me");
    const username = usernameField.value;
    const password = passwordField.value;

    const signupWait = await chatAPI.signUp(username, password);
    console.log(signupWait);

    if (signupWait.success) {
        console.log("nice one, " + username);
        // document.cookie = "V2token=" + signupWait.session_token
        // document.cookie = "userID=" + signupWait.id;
    } else {
        console.error(signupWait.error);
    }
}

loginButton.addEventListener("click", Login);
signupButton.addEventListener("click", SignUp);