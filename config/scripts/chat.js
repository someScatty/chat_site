import * as CM from "/scripts/cookieManager.js";
import "/scripts/api.js";
document.chatAPI = new Chatify();

function redirect(extension) {
    window.location.href = document.chatAPI.baseURL + extension;
}
if (!CM.verifyCookies()) {
    redirect("/login");
}

// moving on..
const sendButton = document.getElementById("sendButton")
const otherVersion = document.getElementById("otherVersion")