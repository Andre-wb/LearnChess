document.addEventListener("DOMContentLoaded", function () {
    if (!window.Telegram || !window.Telegram.WebApp || !Telegram.WebApp.initDataUnsafe) {
        console.warn("Telegram WebApp API недоступен");
        return;
    }

    const tg = window.Telegram.WebApp;
    const user = tg.initDataUnsafe.user;

    // Проверяем, что мы на нужной странице
    if (window.location.pathname === '/account' && user && !sessionStorage.getItem('userSent')) {
        fetch('/set_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: user.id,
                first_name: user.first_name,
                username: user.username,
                photo_url: user.photo_url || null
            })
        }).then(res => {
            if (res.ok) {
                sessionStorage.setItem('userSent', 'true');
                location.reload();
            } else {
                console.error("Ошибка при отправке данных", res);
            }
        }).catch(err => {
            console.error("Ошибка сети:", err);
        });
    }
});