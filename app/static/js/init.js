const tg = window.Telegram.WebApp;
const user = tg.initDataUnsafe.user;

if (user && !sessionStorage.getItem('userSent')) {
    fetch('/set_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: user.id,
            first_name: user.first_name,
            username: user.username,
            photo_url: user.photo_url || null
        })
    }).then(() => {
        sessionStorage.setItem('userSent', 'true');
        location.reload();
    });
}