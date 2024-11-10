# API Playground
<img width="1420" alt="image" src="https://github.com/user-attachments/assets/72c14348-e382-4fc9-a908-5ed577e39ed4">

## Overview
This API playground serves as a platform for users to test their API clients during a workshop. It is built using Python with the FastAPI library. The host features a simple yet robust frontend that provides the following functionalities:

### 1. User Authentication
- **Feature**: Allow users to generate their own authentication tokens.
- **Frontend**: A form where users can input their name.
- **Backend**: Generate and return a unique token for the user.
<img width="973" alt="image" src="https://github.com/user-attachments/assets/8d41c396-ce49-4165-a58f-5b7ac3edadf9">

### 2. Display Incoming Requests
- **Feature**: Stream incoming API requests to the browser in real-time.
- **Frontend**: A live feed that displays incoming requests as they are received.
- **Backend**: Capture and stream incoming requests to the frontend using WebSockets.
<img width="1484" alt="image" src="https://github.com/user-attachments/assets/c80fe9df-c918-4889-ac33-988d6d3a453f">

### 3. Reverse API Calls
- **Feature**: Allow users to call their own API hosts.
- **Frontend**: An input field for the endpoint URI, request type (GET/PUT/PATCH), content type, and request body (for PUT/PATCH).
- **Backend**: Send the specified request to the provided endpoint and display the response.
<img width="1404" alt="image" src="https://github.com/user-attachments/assets/8fdc1080-d6bf-4788-9cd8-7ced75378ccd">

### 4. Employee and Department Management
- **Feature**: Manage employee and department sample data.
- **Frontend**: Tables to display employee and department data with pagination.
- **Backend**: Endpoints to create, read, update, and delete employee and department records.
<img width="1384" alt="image" src="https://github.com/user-attachments/assets/ab87d890-8964-4eac-bb93-e0d567bfdf91">

### 5. Admin Panel
- **Feature**: Admin functionalities to reset employee, department, and token data.
- **Frontend**: Admin panel with password protection.
- **Backend**: Endpoints to reset employee, department, and token data.
<img width="662" alt="image" src="https://github.com/user-attachments/assets/34f8056c-036a-4fff-b8f0-31d1890f2822">

## Technical Requirements
- **Python Version**: 3.9+
- **Libraries**: FastAPI, SQLAlchemy, Jinja2, Uvicorn, more (see: `requirements.txt`)
- **Platform**: Designed on macOS for IBM i. Should run anywhere you can install the required python packages. Database is self-contained.

## API Endpoints

### Display Incoming Requests
- **GET /requests**: Serve the requests page that displays incoming requests in real-time.
  - **Response**: HTML page with a live feed of incoming requests.

### WebSocket Stream
- **/ws**: WebSocket endpoint to stream incoming requests to the frontend in real-time.

### Echo Endpoints
- **/echo**: Handle all HTTP methods and echo back the request details.
  - **Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD, CONNECT, TRACE
  - **Request Headers**:
    - **Authorization**: Bearer token (optional)
  - **Request Body**: Any valid JSON or text
  - **Response**:
    ```json
    {
        "uri": "string",
        "method": "string",
        "body": "string"
    }
    ```

### Employee Table
- **GET /employees**: Get a paginated list of employees.
  - **Response**:
    ```json
    {
        "employees": [],
        "totalPages": "integer",
        "totalRows": "integer"
    }
    ```
- **PUT /employees**: Create a new employee.
  - **Request Body**:
    ```json
    {
        "first": "string",
        "last": "string",
        "job": "string",
        "workdept": "string",
        "salary": "number"
    }
    ```
  - **Response**:
    ```json
    {
        "id": "string",
        "first": "string",
        "last": "string",
        "job": "string",
        "workdept": "string",
        "salary": "number"
    }
    ```

### Department Table
- **GET /departments**: Get a paginated list of departments.
  - **Response**:
    ```json
    {
        "departments": [],
        "totalPages": "integer",
        "totalRows": "integer"
    }
    ```
- **PUT /departments**: Create a new department.
  - **Request Body**:
    ```json
    {
        "id": "string",
        "name": "string",
        "manager": "string",
        "location": "string"
    }
    ```
  - **Response**:
    ```json
    {
        "id": "string",
        "name": "string",
        "manager": "string",
        "location": "string"
    }
    ```

### Catch-All Route
- **/{path:path}**: Handle unhandled methods and return appropriate HTTP error messages to websocket stream.
  - **Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD
  - **Response**: HTTP 405 Method Not Allowed or HTTP 404 Not Found

## Implementation Steps
1. Clone the repository:
    ```shell
    git clone https://github.com/wright4i/api-playground.git
    ```
2. Create a virtual environment:
    ```shell
    python3 -m venv --system-site-packages api-playground
    ```
3. Activate the virtual environment:
    - On PASE (IBM i):
        ```shell
        . api-playground/bin/activate
        ```
    - On macOS/Linux:
        ```shell
        source api-playground/bin/activate
        ```
    - On Windows:
        ```shell
        api-playground\Scripts\activate
        ```
4. Change directory:
    ```shell
    cd api-playground
    ```
5. Install the required packages:
    ```shell
    pip install -r requirements.txt
    ```
6. Copy the example environment file and set up the environment variables:
    ```shell
    cp .env.example .env
    ```
    Edit the `.env` file to configure the necessary variables.

7. Run the application:
    ```shell
    uvicorn app.main:app --reload --host 0.0.0.0 --port 10500
    ```

## Project Structure
```
api-playground/
├── app/
│   ├── main.py 
│   ├── templates.py
│   ├── utils.py
│   ├── connections/
│   │   ├── base.py
│   │   ├── sqlite.py
│   ├── models/
│   │   ├── department.py
│   │   ├── employee.py
│   │   ├── token.py
│   ├── routers/
│   │   ├── department.py
│   │   ├── echo.py
│   │   ├── employee.py
│   │   ├── reverse.py
│   │   ├── token.py
│   │   ├── websocket.py
├── templates/
│   ├── index.html
│   ├── auth_token_modal.html
│   ├── admin_panel_modal.html
│   ├── send_tab.html
│   ├── receive_tab.html
│   ├── employee_tab.html
│   ├── department_tab.html
├── static/
│   └── css/
│   ├── dracula.css
│   ├── styles.css
│   └── css/
│   ├── admin_panel_modal.js
│   ├── auth_token_modal.js
│   ├── department_tab.js
│   ├── employee_tab.js
│   ├── index.js
│   ├── receive_tab.js
│   ├── send_tab.js
├── requirements.txt
├── playground.yml
└── README.md
```
