# Personal Portfolio Website

A responsive personal portfolio website for showcasing professional
information, technical skills, projects, certifications, and contact
details. The project also includes a small FastAPI service that sends
and verifies email OTPs for the viewer password-reset flow.

## Features

-   Responsive portfolio layout with a dark visual theme.
-   Separate **Admin** and **Viewer** access flows.
-   Viewer registration and login using browser `localStorage`.
-   Admin editing controls for selected portfolio text.
-   Profile photo upload, crop, and removal; the selected photo is
    stored in browser `localStorage`.
-   Certification/document upload controls.
-   Forgot-password flow using email OTP:
    -   Request a 4-digit OTP.
    -   Verify the OTP.
    -   Authorize a password reset after successful verification.
-   FastAPI backend with endpoints for sending, verifying, and
    completing the OTP reset flow.

## Project structure

``` text
venky_portfolio/
├── portfolio.html       # Frontend portfolio website
├── otp_backend.py       # FastAPI OTP service
├── requirements.txt     # Python dependencies
├── .env                 # Local SMTP configuration (do not commit)
└── .gitignore
```

Do not include a Python virtual environment (`venv/`) in source control
or deployment packages. Create it locally when setting up the project.

## Technologies used

-   HTML5
-   CSS3
-   JavaScript
-   Python
-   FastAPI
-   Pydantic
-   Uvicorn
-   SMTP email (for OTP delivery)
-   Browser `localStorage` and `sessionStorage`

## Requirements

-   Python 3.9 or newer
-   pip
-   A Gmail account or another SMTP provider configured to send email
-   A modern web browser

Install the Python dependencies:

``` bash
pip install -r requirements.txt
```

## Configuration

The OTP backend reads its SMTP settings from environment variables:

  Variable          Description
  ----------------- ------------------------------------------------------
  `SMTP_HOST`       SMTP server hostname, for example `smtp.gmail.com`
  `SMTP_PORT`       SMTP port, commonly `587` for STARTTLS
  `SMTP_USERNAME`   SMTP account username/email
  `SMTP_PASSWORD`   SMTP password or provider-generated app password
  `SMTP_FROM`       Optional sender address; defaults to `SMTP_USERNAME`

Create a local `.env` file or configure these variables in your
operating system or hosting platform. The Python file does not
automatically load `.env`, so if you use a `.env` file, install and
configure a dotenv loader or export the variables before starting the
server.

Example `.env` format (replace the placeholders with your own values):

``` env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@example.com
```

**Never commit `.env`, SMTP credentials, passwords, or API secrets to
GitHub.**

## Run the application

### 1. Start the OTP backend

From the project directory, run:

``` bash
uvicorn otp_backend:app --host 127.0.0.1 --port 8000 --reload
```

The API root should respond at:

``` text
http://127.0.0.1:8000/
```

Interactive API documentation is available at:

``` text
http://127.0.0.1:8000/docs
```

### 2. Open the portfolio frontend

Open `portfolio.html` in a browser.

The forgot-password frontend currently calls the backend at:

``` text
http://127.0.0.1:8000
```

If the backend is hosted elsewhere, update the `API_BASE` value in the
frontend JavaScript to the deployed API URL. For production, serve the
frontend and backend over HTTPS and configure CORS to allow only the
actual portfolio origin.

## OTP API endpoints

  ------------------------------------------------------------------------
  Method                  Endpoint                 Purpose
  ----------------------- ------------------------ -----------------------
  `GET`                   `/`                      Check that the OTP
                                                   service is running

  `POST`                  `/auth/send-otp`         Generate and email a
                                                   4-digit OTP

  `POST`                  `/auth/verify-otp`       Verify the OTP

  `POST`                  `/auth/reset-password`   Confirm that OTP
                                                   verification succeeded
                                                   and authorize reset
  ------------------------------------------------------------------------

### Example request bodies

Send OTP:

``` json
{
  "email": "user@example.com"
}
```

Verify OTP:

``` json
{
  "email": "user@example.com",
  "otp": "1234"
}
```

Authorize password reset:

``` json
{
  "email": "user@example.com",
  "new_password": "new-password"
}
```

The OTP expires after five minutes. The backend stores OTP data
temporarily in memory, so pending OTPs are lost when the server
restarts.

## Important security notes

This project is suitable as a learning/demo portfolio, but the
authentication implementation needs hardening before public production
use:

-   The frontend contains an admin login credential in client-side
    JavaScript. Anything in frontend code can be viewed by visitors.
    Remove this approach and implement admin authentication on the
    server; rotate any credential that has been exposed.
-   Viewer account details and passwords are stored in browser
    `localStorage`. Do not store plaintext passwords there. Use
    server-side account storage and securely hashed passwords.
-   The OTP backend currently keeps OTPs in an in-memory dictionary. Use
    a shared, expiring store such as Redis or a database for production.
-   Add rate limiting, OTP attempt limits, and protections against
    repeated password-reset requests.
-   The reset endpoint currently authorizes the reset; it does not
    update a server-side user database. The frontend updates its locally
    stored viewer record after the API confirms the reset.
-   Restrict CORS to trusted origins. Do not use wildcard origins for a
    production deployment.
-   Use HTTPS, secure session handling, input validation, and
    appropriate logging without exposing secrets.
-   Avoid committing `.env`, `venv/`, cache files, or other
    local/private data.

## Troubleshooting

**OTP email is not sent** - Confirm that all SMTP environment variables
are set. - Check the SMTP host and port. - For Gmail, use an app
password where required by Google account security settings. - Check
that the backend is running and reachable at the configured `API_BASE`.

**The frontend cannot reach the API** - Confirm the backend is running
on port `8000`. - Check the `API_BASE` value in `portfolio.html`. - If
the frontend is deployed, replace the localhost URL with the deployed
backend URL and configure CORS accordingly.

**OTP expired** - Request a new OTP. OTPs are valid for five minutes.
