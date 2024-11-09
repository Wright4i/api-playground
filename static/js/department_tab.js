(function() {
    let currentDepartmentPage = 1;
    let departmentRowsPerPage = 10;

    async function refreshDepartments(page = 1, showToastMessage = true) {
        currentDepartmentPage = page;
        try {
            const response = await fetch(`/departments?page=${page}&limit=${departmentRowsPerPage}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (!data.departments) {
                throw new Error('Invalid response structure');
            }
            const departments = data.departments;
            const totalPages = data.totalPages;
            const totalRows = data.totalRows;
            const departmentTableBody = document.getElementById('department-table-body');
            departmentTableBody.innerHTML = '';
            departments.forEach(department => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${department.DEPTNO}</td>
                    <td>${department.DEPTNAME}</td>
                    <td>${department.MGRNO}</td>
                    <td>${department.ADMRDEPT}</td>
                    <td>${department.LOCATION}</td>
                `;
                departmentTableBody.appendChild(row);
            });
            document.getElementById('department-total-rows').innerText = `Total Rows: ${totalRows !== undefined ? totalRows : 'N/A'}`;
            updateDepartmentPagination(totalPages, page);
            if (showToastMessage) {
                showToast('Departments data refreshed', 'is-success');
            }
        } catch (error) {
            console.error('Error fetching departments:', error);
            showToast('Error fetching departments', 'is-danger');
        }
    }

    function updateDepartmentPagination(totalPages, currentPage) {
        const paginationList = document.getElementById('department-pagination-list');
        paginationList.innerHTML = '';
        for (let i = 1; i <= totalPages; i++) {
            const pageItem = document.createElement('li');
            pageItem.innerHTML = `<a class="pagination-link ${i === currentPage ? 'is-current' : ''}" onclick="refreshDepartments(${i}, false)">${i}</a>`;
            paginationList.appendChild(pageItem);
        }

        const previousButton = document.getElementById('department-previous');
        const nextButton = document.getElementById('department-next');

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

    function previousDepartmentPage() {
        if (currentDepartmentPage > 1) {
            currentDepartmentPage--;
            refreshDepartments(currentDepartmentPage, false);
        }
    }

    function nextDepartmentPage() {
        const nextButton = document.getElementById('department-next');
        if (!nextButton.disabled) {
            currentDepartmentPage++;
            refreshDepartments(currentDepartmentPage, false);
        }
    }

    function changeDepartmentLimit() {
        const limitSelect = document.getElementById('department-limit');
        departmentRowsPerPage = parseInt(limitSelect.value, 10);
        refreshDepartments(1); // Reset to first page
    }

    // Expose functions to global scope
    window.refreshDepartments = refreshDepartments;
    window.previousDepartmentPage = previousDepartmentPage;
    window.nextDepartmentPage = nextDepartmentPage;
    window.changeDepartmentLimit = changeDepartmentLimit;
})();