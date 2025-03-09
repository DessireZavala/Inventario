document.addEventListener("DOMContentLoaded", function () {
    sessionStorage.setItem("sessionActive", "true");
});

// Solo cerrar sesión si se detecta un cierre real de la pestaña
window.addEventListener("beforeunload", function (event) {
    if (!sessionStorage.getItem("sessionActive")) {
        navigator.sendBeacon("/logout");
    }
});

// Mantener sesión si solo cambia de pestaña o minimiza
document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") {
        sessionStorage.setItem("sessionActive", "true");
    } else if (document.visibilityState === "hidden") {
        sessionStorage.removeItem("sessionActive");
    }
});

// Asegurar que la sesión se mantiene después de un refresh o navegación interna
window.addEventListener("pageshow", function (event) {
    sessionStorage.setItem("sessionActive", "true");
});
