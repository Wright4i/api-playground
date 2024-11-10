(function() {
    let currentEmployeePage = 1;
    let employeeRowsPerPage = 10;

    async function refreshEmployees(page = 1, showToastMessage = true) {
        currentEmployeePage = page;
        try {
            const response = await fetch(`/employees?page=${page}&limit=${employeeRowsPerPage}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const { employees, totalPages, totalRows } = await response.json();
            const employeeTableBody = document.getElementById('employee-table-body');
            employeeTableBody.innerHTML = '';
            employees.forEach(employee => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${employee.id}</td>
                    <td>${employee.first}</td>
                    <td>${employee.last}</td>
                    <td>${employee.job}</td>
                    <td>${employee.workdept}</td>
                    <td>${employee.salary}</td>
                `;
                employeeTableBody.appendChild(row);
            });
            document.getElementById('employee-total-rows').innerText = `Total Rows: ${totalRows !== undefined ? totalRows : 'N/A'}`;
            updateEmployeePagination(totalPages, page);
            if (showToastMessage) {
                showToast('Employees data refreshed', 'is-success');
            }
        } catch (error) {
            console.error('Error fetching employees:', error);
            showToast('Error fetching employees', 'is-danger');
        }
    }

    function updateEmployeePagination(totalPages, currentPage) {
        const paginationList = document.getElementById('employee-pagination-list');
        paginationList.innerHTML = '';
        for (let i = 1; i <= totalPages; i++) {
            const pageItem = document.createElement('li');
            pageItem.innerHTML = `<a class="pagination-link ${i === currentPage ? 'is-current' : ''}" onclick="refreshEmployees(${i}, false)">${i}</a>`;
            paginationList.appendChild(pageItem);
        }

        const previousButton = document.getElementById('employee-previous');
        const nextButton = document.getElementById('employee-next');

        if (currentPage === 1) {
            previousButton.classList.remove('is-link', 'is-light');
            previousButton.disabled = true;
        } else {
            previousButton.classList.add('is-link', 'is-light');
            previousButton.disabled = false;
        }

        if (currentPage === totalPages) {
            nextButton.classList.remove('is-link', 'is-dark');
            nextButton.disabled = true;
        } else {
            nextButton.classList.add('is-link', 'is-dark');
            nextButton.disabled = false;
        }
    }

    function previousEmployeePage() {
        if (currentEmployeePage > 1) {
            currentEmployeePage--;
            refreshEmployees(currentEmployeePage, false);
        }
    }

    function nextEmployeePage() {
        const nextButton = document.getElementById('employee-next');
        if (!nextButton.disabled) {
            currentEmployeePage++;
            refreshEmployees(currentEmployeePage, false);
        }
    }

    function changeEmployeeLimit() {
        const limitSelect = document.getElementById('employee-limit');
        employeeRowsPerPage = parseInt(limitSelect.value, 10);
        refreshEmployees(1); // Reset to first page
    }

    // Expose functions to global scope
    window.refreshEmployees = refreshEmployees;
    window.previousEmployeePage = previousEmployeePage;
    window.nextEmployeePage = nextEmployeePage;
    window.changeEmployeeLimit = changeEmployeeLimit;
})();