// Tab functionality
function showTab(tab) {
    const tabs = ['send', 'receive', 'employee', 'department'];
    tabs.forEach(t => {
        document.getElementById(t).classList.add('is-hidden');
        document.getElementById(t + '-tab').classList.remove('is-active');
    });
    document.getElementById(tab).classList.remove('is-hidden');
    document.getElementById(tab + '-tab').classList.add('is-active');

    // Call refresh functions when the respective tabs are activated
    if (tab === 'employee') {
        refreshEmployees();
    } else if (tab === 'department') {
        refreshDepartments();
    }
}

// Open and close modals
function openAuthModal() {
    fetchTokens();
    document.getElementById('auth-modal').classList.add('is-active');
}

function closeAuthModal() {
    document.getElementById('auth-modal').classList.remove('is-active');
}

function openAdminModal() {
    document.getElementById('admin-modal').classList.add('is-active');
}

function closeAdminModal() {
    document.getElementById('admin-modal').classList.remove('is-active');
}

// Show toast notification
let toastZIndex = 25; // Initialize z-index for toasts

function showToast(message, type) {
    const originalToast = document.getElementById('toast');
    const toast = originalToast.cloneNode(true);
    toast.classList.add(`${type}`);
    toast.classList.add('is-flex');
    toast.innerText = message;
    toast.style.zIndex = toastZIndex-- // Decrement z-index for each new toast
    toast.style.width = '33%';
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => {
            toast.remove();
            toastZIndex++ // Increment z-index after removal
        }, (500 - (toastZIndex*10)) * 1); // Remove after 250ms
        }, (500 - (toastZIndex*10)) * 12); // Start fade-out after 3 seconds
}

window.showToast = showToast;

// Create and append the "return to top" button
const returnToTopButton = document.createElement('button');
returnToTopButton.classList.add('button', 'is-primary', 'is-hidden', 'has-tooltip-top');
returnToTopButton.setAttribute('data-tooltip', 'Return to Top');
returnToTopButton.style.position = 'fixed';
returnToTopButton.style.bottom = '20px';
returnToTopButton.style.right = '20px';
returnToTopButton.style.fontSize = '1.5em';
returnToTopButton.innerHTML = '<span class="icon"><i class="fas fa-arrow-up"></i></span>';
returnToTopButton.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
document.body.appendChild(returnToTopButton);

// Show/hide the button based on scroll position
window.addEventListener('scroll', () => {
    if (window.scrollY > (window.innerHeight/2)) {
        returnToTopButton.classList.remove('is-hidden');
    } else {
        returnToTopButton.classList.add('is-hidden');
    }
});