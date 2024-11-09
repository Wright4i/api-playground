// Authentication functions
document.getElementById('auth-form').addEventListener('submit', function(event) {
    event.preventDefault();
    generateToken();
});

document.getElementById('name').addEventListener('input', function() {
    document.getElementById('generate-button').style.display = 'inline';
    document.getElementById('auth-result').innerText = '';
    document.getElementById('auth-result-message').className = 'message';
});

async function generateToken() {
    const name = document.getElementById('name').value.trim();
    if (!name) {
        document.getElementById('auth-result').innerText = 'Name must not be blank';
        document.getElementById('auth-result-message').className = 'message is-warning';
        return;
    }
    const response = await fetch('/auth/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name })
    });
    const data = await response.json();
    if (data.message) {
        document.getElementById('auth-result').innerText = data.message;
        document.getElementById('auth-result-message').className = 'message is-info';
    } else {
        const token = data.token;
        copyToClipboard(token);
        document.getElementById('auth-result').innerText = `Bearer ${token} copied to clipboard`;
        document.getElementById('auth-result-message').className = 'message is-success';
    }
    fetchTokens();
}

async function deleteToken(name) {
    const response = await fetch(`/auth/${name}`, {
        method: 'DELETE'
    });
    const data = await response.json();
    document.getElementById('auth-result').innerText = data.message;
    document.getElementById('auth-result-message').className = 'message is-danger';
    fetchTokens();
}

async function fetchTokens() {
    const response = await fetch('/auth/tokens');
    const tokens = await response.json();
    const tbody = document.getElementById('tokens-table').querySelector('tbody');
    tbody.innerHTML = '';
    tokens.forEach(token => {
        const encodedName = encodeURIComponent(token.name);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${decodeURIComponent(token.name)}</td>
            <td>${token.token}</td>
            <td>
                <button class="button is-danger is-small is-family-monospace" onclick="deleteToken('${encodedName}')">Delete</button>
                <button class="button is-info is-small is-family-monospace" onclick="copyToClipboard('${token.token}', this)">&nbsp;Copy&nbsp;</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function copyToClipboard(text, button) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);

    // Change button text to "Copied" temporarily
    if (button) {
        const originalText = button.innerText;
        button.innerText = 'Copied';
        button.classList.add('is-primary');
        button.classList.remove('is-info');
        setTimeout(() => {
            button.innerText = originalText;
            button.classList.remove('is-primary');
            button.classList.add('is-info');
        }, 2000); // Change back after 2 seconds
    }
}