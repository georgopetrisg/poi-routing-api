const API_URL = 'http://127.0.0.1:5000';

const registerBtn = document.getElementById('registerBtn');

if (registerBtn) {
    registerBtn.addEventListener('click', async () => {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMsg = document.getElementById('errorMsg');

        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                window.location.href = '/login';
            } else {
                const data = await response.json();
                throw new Error(data.message || 'Registration failed');
            }
        } catch (err) {
            errorMsg.textContent = err.message;
            errorMsg.style.display = 'block';
        }
    });
}

const loginBtn = document.getElementById('loginBtn');

if (loginBtn){
    loginBtn.addEventListener('click', async () => {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMsg = document.getElementById('errorMsg');

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                // Store API Key and Username
                localStorage.setItem('apiKey', data.apiKey); // Adjust based on actual API response key
                localStorage.setItem('username', username);
                localStorage.setItem('userId', data.id);
                window.location.href = '/';
            } else {
                throw new Error('Invalid credentials');
            }
        } catch (err) {
            errorMsg.textContent = err.message;
            errorMsg.style.display = 'block';
        }
    });
}