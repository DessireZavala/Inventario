
document.addEventListener("DOMContentLoaded", function () {
    sessionStorage.setItem("sessionActive", "true");
});

window.addEventListener("beforeunload", function (event) {
    if (!sessionStorage.getItem("sessionActive")) {
        navigator.sendBeacon("/logout");
    }
});

document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") {
        sessionStorage.removeItem("sessionActive");
    }
});

window.addEventListener("pageshow", function (event) {
    sessionStorage.setItem("sessionActive", "true");
});
