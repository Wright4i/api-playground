let interval; // Define interval in a higher scope

function startProgressBar() {
    const progressBar = document.getElementById('send-progress-bar');

    progressBar.style.display = 'block';
    progressBar.className = 'progress is-primary';

    const sendButton = document.getElementById('send-request-button');

    sendButton.disabled = true;
    sendButton.className = 'button is-primary is-fullwidth is-light is-outlined';
    sendButton.innerText = 'Sending...';

    let progress = 0;
    interval = setInterval(() => {
        progress += 1;
        progressBar.value = progress;
        if (progress >= 90) {
            progressBar.className = 'progress is-danger';
        } else if (progress >= 50) {
            progressBar.className = 'progress is-warning';
        }
        if (progress >= 100) {
            clearInterval(interval);
        }
    }, 100);
}

function stopProgressBar() {
    clearInterval(interval);
    const progressBar = document.getElementById('send-progress-bar');
    const sendButton = document.getElementById('send-request-button');
    progressBar.value = 100;
    setTimeout(() => {
        sendButton.disabled = false;
        sendButton.className = 'button is-link is-fullwidth';
        sendButton.innerText = 'Send Request';
        progressBar.style.display = 'none';
        progressBar.value = 0;
        progressBar.className = 'progress is-primary';
    }, 500);
}

// Handle reverse form submission
document.getElementById('reverse-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const url = document.getElementById('url').value;
    const method = document.getElementById('method').value;
    const reversetype = document.getElementById('content-type').value;
    let body = document.getElementById('body').value.trim();
    let headers = {
        'Content-Type': 'application/json'
    };

    startProgressBar(); 

    console.log(`URL: ${url}`);
    console.log(`Method: ${method}`);
    console.log(`Reverse-Type: ${reversetype}`);
    console.log(`Body: ${body}`);

    if (reversetype === 'json') {
        if (body === '') {
            showToast('Body cannot be blank for JSON content type', 'is-danger');
            stopProgressBar(); 
            return;
        } else {
            try {
                JSON.parse(body);  
            } catch (e) {
                showToast('Invalid JSON in body', 'is-danger');
                stopProgressBar();  
                return;
            }
        }
    } else {
        body = body || '';
    }

    body = method === 'GET' ? null : body;

    const requestBody = JSON.stringify({ url, method, reversetype, headers: {}, body });

    console.log(`Request Body: ${requestBody}`);

    try {
        const response = await Promise.race([
            fetch('/reverse/', {
                method: 'PUT',
                headers: headers,
                body: requestBody
            }),
            new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 10000))
        ]);

        const result = await response.json();
        const statusCode = result.status_code || 400;
        const content = result.content || result.detail;     

        showToast(`HTTP Status Code: ${statusCode}`, statusCode >= 200 && statusCode < 300 ? 'is-success' : 'is-danger');

        document.getElementById('status-code').innerText = `HTTP Status Code: ${statusCode}`;
        document.getElementById('status-code').className = statusCode >= 200 && statusCode < 300 ? 'tag is-success' : 'tag is-danger';

        if (typeof content === 'object') {
            document.getElementById('response-content').textContent = JSON.stringify(content, null, 2);
            hljs.highlightAll(); // Apply syntax highlighting
        } else {
            document.getElementById('response-content').textContent = content;
        }

        try {
            console.log(`Response: ${JSON.stringify(result, null, 2)}`);
        } catch (error) {
            console.log(`Response: ${result}`);
        }
    } catch (error) {
        console.error(`Error: ${error}`);
        showToast(`Error: ${error.message}`, 'is-danger');
        document.getElementById('response-content').textContent = `Error: ${error.message}`;

    } finally {
        stopProgressBar();
    }
});