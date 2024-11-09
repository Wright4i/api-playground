document.getElementById('admin-password').addEventListener('input', function() {
    const userPass = this.value;
    const buttons = document.querySelectorAll('#reset-employee, #reset-department, #reset-token');
    if (userPass === adminPass) {
        buttons.forEach(button => {
            button.disabled = false;
            button.removeAttribute('data-tooltip');
            button.classList.remove('is-inverted');
        });
        document.getElementById('password-field').style.display = 'none';
    } else {
        buttons.forEach(button => {
            button.disabled = true;
            button.setAttribute('data-tooltip', 'Unauthorized');
            button.classList.add('is-inverted');
        });
    }
});

function openAdminModal() {
    document.getElementById('admin-modal').classList.add('is-active');
}

function closeAdminModal() {
    document.getElementById('admin-modal').classList.remove('is-active');
    const buttons = document.querySelectorAll('#reset-employee, #reset-department, #reset-token');
    buttons.forEach(button => {
        button.disabled = true;
        button.setAttribute('data-tooltip', 'Unauthorized');
        button.classList.add('is-inverted');
    });
    document.getElementById('admin-password').value = '';
    document.getElementById('password-field').style.display = 'block';
}

function resetEmployee() {
    fetch('/admin/reset-employee', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showToast(data.message, 'is-success');
            if (!document.getElementById('employee').classList.contains('is-hidden')) {
                refreshEmployees();
            }
        });
}

function resetDepartment() {
    fetch('/admin/reset-department', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showToast(data.message, 'is-success');
            if (!document.getElementById('department').classList.contains('is-hidden')) {
                refreshDepartments();
            }
        });
}

function resetToken() {
    fetch('/admin/reset-token', { method: 'POST' })
        .then(response => response.json())
        .then(data => showToast(data.message, 'is-success'));
}