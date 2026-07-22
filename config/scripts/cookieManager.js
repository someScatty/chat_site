export const setCookie = function(name = String, value) {
    document.cookie = name + "=" + value;
};
export const getCookie = function(name = String) {
    let cookies = document.cookie.split("; ");
    for (let i = 0; i < cookies.length; i++) { // no way i looked up how to do a for loop im in for a WILD time
        let nameCookies = cookies[i]
        if (nameCookies.startsWith(name)) {
            let cooker = nameCookies.slice(name.length + 1, nameCookies.length + 1); // first plus is to accomodate the =
            return cooker;
        }
    }
    return
};

export const verifyCookies = function() { // expiration check soon, but for now it just checks if it exists
    if (getCookie("V2token") && getCookie("userID")) {
        return true;
    }

    return false;
};