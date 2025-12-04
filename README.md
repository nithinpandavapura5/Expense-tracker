# Expense Tracker

A powerful Expense Tracker application built with Flask that helps users manage their finances effectively.

## Features

### Core Features
- ✅ User Authentication (Login/Register)
- ✅ Log Daily Expenses with Categories
- ✅ Set Monthly Budgets per Category
- ✅ Dashboard with Spending Summary and Budget Alerts
- ✅ Different Budgets for Different Months
- ✅ Dockerized for easy deployment

### Advanced Features
- ✅ **Custom Alert System**
  - 🔴 Red Alert: When spending exceeds budget
  - 🟠 Orange Warning: When 90%+ of budget is used
  - 🟢 Green Status: When spending is under budget
- ✅ **Enhanced Dashboard**
  - Total spending and budget overview
  - Remaining budget display
  - Percentage used per category
  - Color-coded alerts
- ✅ **Delete Functionality**
  - Remove expenses
  - Remove budgets
- ✅ **Reports & Export**
  - Download budget vs spending reports (CSV)
  - Download all expenses (CSV)
  - Excel-compatible format

## Setup & Run

### Prerequisites
- Python 3.9+ or Docker
- Git (optional)

### Option 1: Manual Setup (Recommended)

1.  **Install dependencies:**
    ```bash
    python -m pip install -r requirements.txt
    ```

2.  **Run the application:**
    ```bash
    python run.py
    ```

3.  **Access the application:**
    Open your browser and go to `http://localhost:5000`

### Option 2: Docker Setup

1.  **Build the Docker image:**
    ```bash
    docker build -t expense-tracker .
    ```

2.  **Run the container:**
    ```bash
    docker run -p 5000:5000 expense-tracker
    ```

3.  **Access the application:**
    Open your browser and go to `http://localhost:5000`

## Testing

### Automated Tests
Run the test suite with pytest:
```bash
python -m pytest
```

### Manual Testing Steps

1.  **User Registration & Login**
    - Register a new account
    - Log in with your credentials
    - Verify you're redirected to the dashboard

2.  **Set Budgets**
    - Navigate to the "Budgets" page
    - Set a budget for "Food" category (e.g., $500)
    - Set a budget for "Transport" category (e.g., $200)
    - Verify budgets appear in the table

3.  **Add Expenses**
    - Navigate to the "Expenses" page
    - Add an expense: Amount=$100, Category=Food, Date=Today
    - Add another expense: Amount=$450, Category=Food
    - Verify expenses appear in the list

4.  **Verify Dashboard Alerts**
    - Go to Dashboard
    - "Food" should show:
      - Total spending: $550
      - Budget: $500
      - 🔴 Red "Over Budget!" alert (since $550 > $500)
    - "Transport" should show:
      - 🟢 Green "OK" status (no spending yet)

5.  **Test Warning Alert (90% threshold)**
    - Add expense: Amount=$180, Category=Transport
    - Dashboard should show:
      - 🟠 Orange "90% Used" warning (since $180/$200 = 90%)

6.  **Download Reports**
    - Navigate to "Reports" page
    - Click "Download Budget Report (CSV)"
    - Open the CSV file in Excel/Google Sheets
    - Verify all categories and their data are present
    - Click "Download All Expenses (CSV)"
    - Verify all expenses are listed

7.  **Delete Functionality**
    - Go to Expenses page
    - Click "Delete" on any expense
    - Confirm deletion
    - Verify expense is removed and dashboard updates

## Usage Guide

1.  **Register**: Create a new account
2.  **Login**: Log in with your credentials
3.  **Set Budgets**: 
    - Navigate to "Budgets"
    - Select a category, month, year, and amount
    - Submit to create/update budget
4.  **Add Expenses**: 
    - Navigate to "Expenses"
    - Fill in amount, category, description, and date
    - Submit to log the expense
5.  **View Dashboard**: 
    - See spending summary for current month
    - Monitor budget alerts:
      - 🟢 Green = OK
      - 🟠 Orange = 90%+ used (warning)
      - 🔴 Red = Over budget
6.  **Download Reports**:
    - Navigate to "Reports"
    - Download CSV files for analysis in Excel/Google Sheets

## Technical Details

### Database
- **Type**: SQLite
- **File**: `site.db` (auto-created on first run)
- **ORM**: SQLAlchemy

### Models
- **User**: Authentication and user data
- **Category**: Expense categories (Food, Transport, Entertainment, etc.)
- **Budget**: Monthly budgets per category per user
- **Expense**: Individual expense records

### Default Categories
The following categories are auto-created on first run:
- Food
- Transport
- Entertainment
- Utilities
- Rent
- Other

## Project Structure
```
expense_tracker/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models.py            # Database models
│   ├── routes.py            # Application routes
│   ├── forms.py             # WTForms
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── expenses.html
│   │   ├── budgets.html
│   │   ├── reports.html
│   │   ├── login.html
│   │   └── register.html
│   └── static/
│       └── style.css
├── tests/
│   └── test_app.py         # Unit tests
├── Dockerfile
├── requirements.txt
├── run.py                  # Application entry point
└── README.md
```

## Requirements
See `requirements.txt` for full list. Key dependencies:
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- Flask-Bcrypt 1.0.1

## Contributing
This is a portfolio project. Feel free to fork and customize!

## License
MIT License
