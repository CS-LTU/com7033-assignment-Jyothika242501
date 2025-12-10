## HS StrokeApp

HS StrokeApp is a Flask-based web application for managing anonymised patient data
related to stroke and cardiovascular risk.

### Features
- Patient analytics dashboard
- Patient list and filtering
- MFA-enabled authentication
- CSV data import
## Project Architecture

HS StrokeApp is built using a modular Flask architecture to ensure scalability,
maintainability, and separation of concerns.

### Architecture Overview

- **Frontend**
  - HTML templates rendered using Jinja2
  - CSS for responsive UI styling
  - Chart.js used for data visualisation

- **Backend**
  - Flask web framework
  - Blueprint-based routing for modular design
  - Flask-Login for authentication and session management
  - MFA implementation using authenticator-based verification

- **Database**
  - SQLite database (`users.db`)
  - Stores anonymised patient records and user credentials

- **Data Layer**
  - CSV dataset imported using `import_patients.py`
  - Patient records stored and queried from the database

### Application Flow

1. User registers and sets up MFA using an authenticator app
2. User logs in with password + MFA verification
3. Dashboard displays analytics and visualisations
4. Users can view and manage patient records securely
