let websocket;

function connectWebSocket() {
    const wsUrl = `ws://${host}:${port}/ws`;
    websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
        showToast('WebSocket connection established', 'is-success');
    };

    websocket.onerror = (error) => {
        showToast('WebSocket connection error', 'is-danger');
    };

    websocket.onclose = (event) => {
        showToast('WebSocket connection closed', 'is-danger');
    };

    websocket.onmessage = (event) => {
        const messages = document.getElementById('messages');
        const messageData = JSON.parse(event.data);

        const messageRow = document.createElement('tr');
        messageRow.dataset.expireTimeout = setTimeout(() => {
            messageRow.remove();
        }, 60000); // Set expiration timeout to 60 seconds

        // Method
        const methodCell = document.createElement('td');
        methodCell.innerText = messageData.method;
        messageRow.appendChild(methodCell);

        // URI
        const uriCell = document.createElement('td');
        uriCell.innerText = messageData.uri || '-';
        messageRow.appendChild(uriCell);

        // HTTP Code
        const httpCodeCell = document.createElement('td');
        httpCodeCell.classList.add('has-text-centered');
        httpCodeCell.innerText = messageData.status_code || '-';
        if (messageData.status_code >= 200 && messageData.status_code < 300) {
            httpCodeCell.classList.add('has-text-success');
        } else {
            httpCodeCell.classList.add('has-text-danger');
        }
        messageRow.appendChild(httpCodeCell);

        // Sender IP
        const senderIpCell = document.createElement('td');
        senderIpCell.innerText = messageData.sender || '-';
        messageRow.appendChild(senderIpCell);

        // Authorization Token
        const authTokenCell = document.createElement('td');
        authTokenCell.classList.add('has-text-centered');
        const authTokenButton = document.createElement('button');
        authTokenButton.classList.add('button', 'is-small');
        authTokenButton.classList.add(messageData.authorization_status === 'VALID' ? 'is-success' : 'is-danger');
        authTokenButton.innerHTML = '<span class="icon"><i class="fas fa-coins"></i></span>';
        authTokenButton.onclick = () => {
            clearTimeout(messageRow.dataset.expireTimeout);
            currentRow = messageRow;
            openTokenModal(messageData.authorization, messageData.authorization_status === 'VALID');
        };
        if (!messageData.authorization || messageData.authorization === '-') {
            authTokenButton.disabled = true;
            authTokenButton.classList.add('has-tooltip', 'has-tooltip-right');
            authTokenButton.setAttribute('data-tooltip', 'No data available');
        }
        authTokenCell.appendChild(authTokenButton);
        messageRow.appendChild(authTokenCell);

        // Authorization User
        const authUserCell = document.createElement('td');
        authUserCell.innerText = messageData.username || '-';
        messageRow.appendChild(authUserCell);

        // Request Body
        const requestBodyCell = document.createElement('td');
        requestBodyCell.classList.add('has-text-centered');
        const requestBodyButton = document.createElement('button');
        requestBodyButton.classList.add('button', 'is-small', 'is-link');
        requestBodyButton.innerHTML = '<span class="icon"><i class="fas fa-inbox"></i></span>';
        requestBodyButton.onclick = () => {
            clearTimeout(messageRow.dataset.expireTimeout);
            currentRow = messageRow;
            openModal(messageData.request_body);
        };
        if (!messageData.request_body || messageData.request_body === '-') {
            requestBodyButton.disabled = true;
            requestBodyButton.classList.add('has-tooltip', 'has-tooltip-right');
            requestBodyButton.setAttribute('data-tooltip', 'No data available');
        }
        requestBodyCell.appendChild(requestBodyButton);
        messageRow.appendChild(requestBodyCell);

        // Response Body
        const responseBodyCell = document.createElement('td');
        responseBodyCell.classList.add('has-text-centered');
        const responseBodyButton = document.createElement('button');
        responseBodyButton.classList.add('button', 'is-small', 'is-primary');
        responseBodyButton.innerHTML = '<span class="icon"><i class="fas fa-bullhorn"></i></span>';
        responseBodyButton.onclick = () => {
            clearTimeout(messageRow.dataset.expireTimeout);
            currentRow = messageRow;
            openModal(messageData.response_body);
        };
        if (!messageData.response_body || messageData.response_body === '-') {
            responseBodyButton.disabled = true;
            responseBodyButton.classList.add('has-tooltip', 'has-tooltip-right');
            responseBodyButton.setAttribute('data-tooltip', 'No data available');
        }
        responseBodyCell.appendChild(responseBodyButton);
        messageRow.appendChild(responseBodyCell);

        messages.appendChild(messageRow);
    };
}

let currentRow = null;

function resetExpireTimeout(row) {
    clearTimeout(row.dataset.expireTimeout);
    row.dataset.expireTimeout = setTimeout(() => {
        row.remove();
    }, 30000); // Reset expiration timeout to 30 seconds
}

function closeModal() {
    document.getElementById('body-modal').classList.remove('is-active');
    if (currentRow) {
        resetExpireTimeout(currentRow);
        currentRow = null;
    }
}

function closeTokenModal() {
    document.getElementById('token-modal').classList.remove('is-active');
    if (currentRow) {
        resetExpireTimeout(currentRow);
        currentRow = null;
    }
}

// Initialize WebSocket connection on page load
connectWebSocket();