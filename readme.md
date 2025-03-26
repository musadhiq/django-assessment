# Documentation

## Task 1 : API Development

### Endpoints

* `/`: A simple endpoint returning `{"hello": "world"}`. Primarily for testing purposes.
* `/api/users/`: Retrieves a list of all users. Returns a JSON array of user objects serialized using `UserSerializer`.
* `/api/users/import/`: Imports users from a CSV file. Accepts a POST request with a CSV file uploaded as `file`.

### `/api/users/import/` Endpoint Details

This endpoint processes a CSV file containing user data. The CSV file should have columns named "name", "email", and "age".

#### Input

* A CSV file uploaded via a POST request.

#### Validation

* Checks if the file is a CSV file.
* Validates that "name", "email", and "age" fields are present in each row.
* Validates email format using Django's `validate_email`.
* Validates that age is an integer between 0 and 120.
* Checks for duplicate emails.

#### Output

A JSON response containing:

* `success`: A list of successfully created users.
* `rejected`: A list of rows that failed validation, including the error message.
* `successCount`: The number of successfully created users.
* `rejectedCount`: The number of rows that failed validation.

#### Error Handling

Returns appropriate HTTP status codes (400 for bad requests, 500 for server errors) with detailed error messages.

#### Bulk Creation

Uses `bulk_create` for efficient database insertion of valid users.

### Example Usage

* `GET /api/users/`: Retrieves all users.
* `POST /api/users/import/`: Imports users from a CSV file. The request body should contain a file named "file" with the CSV data.

## Task 2 : Middleware Development

### Purpose

This file contains the `BlockIPMiddleware` class, which implements a rate limiting mechanism to prevent abuse and denial-of-service attacks. It works by tracking the number of requests from each IP address within a specified time window.

### Functionality

* Rate Limiting: Limits the number of requests from a single IP address to `RATE_LIMIT` (currently 100) within a `TIME_WINDOW` (currently 5 minutes).
* Blocking: If the rate limit is exceeded, the IP address is blocked for `BLOCK_TIME` (currently 10 minutes).
* Caching: Uses Django's cache to store request counts and block status.
* Response Headers: Adds an `x-remaining-allowed-requests` header to the response, indicating the number of remaining allowed requests before the rate limit is reached.
* IP Address Detection: Attempts to determine the client's IP address from either `HTTP_X_FORWARDED_FOR` or `REMOTE_ADDR` headers. Handles cases where the IP address is missing.
* Logging: Logs warnings when an IP address is blocked or when an IP address cannot be determined.

### Configuration

The following constants control the rate limiting behavior:

* `RATE_LIMIT`: The maximum number of requests allowed within the time window.
* `TIME_WINDOW`: The time window (in seconds) for rate limiting.
* `BLOCK_TIME`: The duration (in seconds) for which an IP address is blocked after exceeding the rate limit.

### Example Usage

The middleware is automatically applied to all requests if properly configured in Django's `MIDDLEWARE` setting.
