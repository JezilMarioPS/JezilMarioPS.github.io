import os
import re
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
from datetime import datetime, timedelta
from pytz import timezone
from tzlocal import get_localzone


# Configure application
app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budget.db")


# Fetch user's timezone from the system dynamically
user_timezone = str(get_localzone())


def convert_utc_to_local(utc_timestamp, user_timezone):
    # Convert UTC timestamp to local time
    local_tz = timezone(user_timezone)
    utc_timestamp = datetime.strptime(utc_timestamp, "%Y-%m-%d %H:%M:%S")
    local_timestamp = utc_timestamp.replace(tzinfo=timezone("UTC")).astimezone(local_tz)
    return local_timestamp.strftime("%Y-%m-%d %H:%M:%S")


@app.route("/")
@login_required
def index():
    """Home page - Redirect to dashboard"""
    return redirect("/dashboard")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        # Extract form data for date range
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")

        # Check if date strings are not empty
        if start_date_str and end_date_str:
            # Convert date strings to datetime objects
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)
        elif start_date_str:
            # If only start date is provided, set end date to the next day
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)
        else:
            flash("Please provide at least the start date for the date range.")
            return redirect("/dashboard")

        # Fetch user's transactions for the dashboard with category names within the specified date range
        user_transactions = db.execute(
            """
            SELECT transactions.*, categories.name as category_name
            FROM transactions
            LEFT JOIN categories ON transactions.category_id = categories.id
            WHERE transactions.user_id = :user_id
                AND transactions.timestamp >= :start_date
                AND transactions.timestamp < :end_date
            ORDER BY transactions.timestamp DESC
            """,
            user_id=session["user_id"],
            start_date=start_date,
            end_date=end_date,
        )
    else:
        # Fetch user's transactions for the dashboard with category names for the last 30 days by default
        thirty_days_ago = datetime.now() - timedelta(days=30)
        user_transactions = db.execute(
            """
            SELECT transactions.*, categories.name as category_name
            FROM transactions
            LEFT JOIN categories ON transactions.category_id = categories.id
            WHERE transactions.user_id = :user_id
                AND transactions.timestamp >= :thirty_days_ago
            ORDER BY transactions.timestamp DESC
            """,
            user_id=session["user_id"],
            thirty_days_ago=thirty_days_ago,
        )

    # Convert UTC timestamps to local time
    for transaction in user_transactions:
        transaction["timestamp"] = convert_utc_to_local(
            transaction["timestamp"], user_timezone
        )

    # Calculate total income and expenses
    total_income = sum(
        transaction["amount"]
        for transaction in user_transactions
        if transaction["type"] == "income"
    )
    total_expenses = sum(
        transaction["amount"]
        for transaction in user_transactions
        if transaction["type"] == "expense"
    )

    # Calculate net income (income - expenses)
    net_income = total_income - total_expenses

    # Fetch user's categories for additional information
    user_categories = db.execute(
        "SELECT * FROM categories WHERE user_id = :user_id",
        user_id=session["user_id"],
    )

    # Calculate transaction summaries for income and expenses
    income_summary, expense_summary = calculate_transaction_summaries(user_transactions)

    return render_template(
        "dashboard.html",
        transactions=user_transactions,
        categories=user_categories,
        total_income=total_income,
        total_expenses=total_expenses,
        net_income=net_income,
        income_summary=income_summary,
        expense_summary=expense_summary,
    )


def calculate_transaction_summaries(transactions):
    income_summary = {}
    expense_summary = {}

    for transaction in transactions:
        category = transaction["category_name"]
        amount = transaction["amount"]

        # Initialize the category in the summary if not exists
        if category not in income_summary:
            income_summary[category] = {"count": 0, "total_value": 0}

        if category not in expense_summary:
            expense_summary[category] = {"count": 0, "total_value": 0}

        # Update count and total value based on transaction type
        if transaction["type"] == "income":
            income_summary[category]["count"] += 1
            income_summary[category]["total_value"] += amount
        elif transaction["type"] == "expense":
            expense_summary[category]["count"] += 1
            expense_summary[category]["total_value"] += amount

    # Filter out categories with zero transactions
    income_summary = {k: v for k, v in income_summary.items() if v["count"] > 0}
    expense_summary = {k: v for k, v in expense_summary.items() if v["count"] > 0}

    return income_summary, expense_summary


@app.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    """Add a new transaction"""
    if request.method == "POST":
        # Extract form data
        category_id = request.form.get("category")

        if category_id == "add_new_category":
            # Redirect to the add_category page if "Add New Category" is selected from dropdown
            return redirect("/add_category")

        amount = request.form.get("amount")
        description = request.form.get("description")
        transaction_type = request.form.get("type")

        # Server-side validation for amount
        try:
            amount = float(amount)
        except ValueError:
            return apology("Please enter a valid number", 400)

        # Validate the form data
        if not category_id or not amount or not transaction_type:
            return apology("Please fill out all required fields", 400)

        # Convert amount to float
        amount = float(amount)

        # Update the transactions table in the database
        db.execute(
            "INSERT INTO transactions (user_id, category_id, amount, description, type) VALUES (:user_id, :category_id, :amount, :description, :type)",
            user_id=session["user_id"],
            category_id=category_id,
            amount=amount,
            description=description,
            type=transaction_type,
        )

        # Display success
        flash("Transaction added successfully")
        return redirect("/dashboard")

    else:
        # If the request method is GET, provide the form for adding a transaction
        # Fetch user's visible categories for the dropdown
        user_categories = db.execute(
            "SELECT * FROM categories WHERE user_id = :user_id AND visible = 1",
            user_id=session["user_id"],
        )
        return render_template("add_transaction.html", categories=user_categories)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must Provide Username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must Provide Password", 403)

        # Query database for username
        user = db.execute(
            "SELECT * FROM users WHERE username = :username",
            username=request.form.get("username"),
        )

        # Ensure username exists and password is correct
        if not user or not check_password_hash(
            user[0]["password"], request.form.get("password")
        ):
            return apology("Invalid Username Or Password", 403)

        # Remember which user has logged in
        session["user_id"] = user[0]["id"]

        # Redirect user to home page
        return redirect("/dashboard")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Extract form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("Must Provide Username", 400)

        elif not password:
            return apology("Must Provide Password", 400)

        elif not confirmation:
            return apology("Must Confirm Password", 400)

        # Ensure password confirmation and match
        elif password != confirmation:
            return apology("Passwords Do Not Match", 400)

        # Require users’ passwords to have some number of letters, numbers, and/or symbols
        if not (
            re.search(r"[a-zA-Z]", password)
            and re.search(r"\d", password)
            and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
        ):
            return apology(
                "Password must include at least One letter, One number, and One symbol",
                400,
            )

        # Check if the username is already taken
        existing_user = db.execute(
            "SELECT * FROM users WHERE username = :username", username=username
        )
        if existing_user:
            return apology("Username Already Taken", 400)

        # Insert the new user into the database
        user_id = db.execute(
            "INSERT INTO users (username, password) VALUES (:username, :password)",
            username=username,
            password=generate_password_hash(password),
        )

        # Insert default categories for the new user
        default_categories = [
            ("GROCERIES", "default_type"),
            ("TRAVEL", "default_type"),
            ("FOOD", "default_type"),
            ("HOUSING AND UTILITIES", "default_type"),
            ("ENTERTAINMENT", "default_type"),
        ]

        # Get the user_id of the newly registered user
        user_id = db.execute(
            "SELECT id FROM users WHERE username = :username", username=username
        )[0]["id"]

        # Insert default categories using the correct syntax
        for name, category_type in default_categories:
            db.execute(
                "INSERT INTO categories (user_id, name, type) VALUES (:user_id, :name, :type)",
                user_id=user_id,
                name=name,
                type=category_type,
            )

        # Redirect user to login page
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/manage_categories", methods=["GET", "POST"])
@login_required
def manage_categories():
    if request.method == "POST":
        pass

    # Fetch and display user's categories (both user-added and default)
    user_categories = db.execute(
        """
        SELECT id, name FROM categories WHERE user_id = :user_id AND visible = 1
        UNION
        SELECT id, name FROM categories WHERE user_id IS NULL AND visible = 1
        """,
        user_id=session["user_id"],
    )

    return render_template("manage_categories.html", categories=user_categories)


@app.route("/add_category", methods=["GET", "POST"])
@login_required
def add_category():
    """Add a new category"""
    if request.method == "POST":
        # Extract form data
        name = request.form.get("name")
        category_type = request.form.get("type", "default_type")

        # Validate the form data
        if not name:
            return apology("Please fill out all required fields", 400)

        # Convert the category name to uppercase
        name = name.upper()

        # Update the categories table in the database
        db.execute(
            "INSERT INTO categories (user_id, name, type) VALUES (:user_id, :name, :type)",
            user_id=session["user_id"],
            name=name,
            type=category_type,
        )

        return redirect("/add_category")

    else:
        # If the request method is GET, provide the form for adding a category
        # Fetch user's categories for the dropdown
        user_categories = db.execute(
            "SELECT * FROM categories WHERE user_id = :user_id",
            user_id=session["user_id"],
        )
        return render_template("add_category.html", categories=user_categories)


@app.route("/delete_category/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    """Delete or hide a category"""
    # Ensure the category belongs to the logged-in user
    result = db.execute(
        "UPDATE categories SET active = 0 WHERE id = :category_id AND user_id = :user_id",
        category_id=category_id,
        user_id=session["user_id"],
    )

    # Check if the update was successful
    if result:
        # If successful, also hide the category from add_transaction dropdown
        db.execute(
            "UPDATE categories SET visible = 0 WHERE id = :category_id AND user_id = :user_id",
            category_id=category_id,
            user_id=session["user_id"],
        )

    # Redirect to the manage categories page
    return redirect("/add_category")


@app.route("/toggle_category/<int:category_id>", methods=["POST"])
@login_required
def toggle_category(category_id):
    """Toggle the visibility of a category"""
    # Ensure the category belongs to the logged-in user
    result = db.execute(
        "UPDATE categories SET visible = NOT visible WHERE id = :category_id AND user_id = :user_id",
        category_id=category_id,
        user_id=session["user_id"],
    )

    # Redirect to the manage categories page
    return redirect("/add_category")


@app.route("/recent_transactions", methods=["GET", "POST"])
@login_required
def recent_transactions():
    """Show recent transactions"""

    if request.method == "POST":
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")

        # Check if date strings are not empty
        if start_date_str and end_date_str:
            # Convert date strings to datetime objects
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)
        elif start_date_str:
            # If only start date is provided, set end date to the next day
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)
        else:
            flash("Please provide at least the start date for the date range.")
            return redirect("/recent_transactions")

        # Fetch user's transactions for the recent transactions page with category names within the specified date range
        user_transactions = db.execute(
            """
            SELECT transactions.*, categories.name as category_name
            FROM transactions
            LEFT JOIN categories ON transactions.category_id = categories.id
            WHERE transactions.user_id = :user_id
                AND transactions.timestamp >= :start_date
                AND transactions.timestamp < :end_date
            ORDER BY transactions.timestamp DESC
            """,
            user_id=session["user_id"],
            start_date=start_date,
            end_date=end_date,
        )
    else:
        # Fetch recent transactions with category names
        user_transactions = db.execute(
            """
            SELECT transactions.*, categories.name as category_name
            FROM transactions
            LEFT JOIN categories ON transactions.category_id = categories.id
            WHERE transactions.user_id = :user_id
            ORDER BY transactions.timestamp DESC
            LIMIT 100
            """,
            user_id=session["user_id"],
        )

    # Convert UTC timestamps to local time
    for transaction in user_transactions:
        transaction["timestamp"] = convert_utc_to_local(
            transaction["timestamp"], user_timezone
        )

    return render_template("recent_transactions.html", transactions=user_transactions)


@app.route("/delete_transaction/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):
    """Delete a transaction"""
    # Ensure the transaction belongs to the logged-in user
    result = db.execute(
        "DELETE FROM transactions WHERE id = :transaction_id AND user_id = :user_id",
        transaction_id=transaction_id,
        user_id=session["user_id"],
    )

    # Redirect to the recent transactions page
    return redirect("/recent_transactions")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user's password"""
    if request.method == "POST":
        # Extract form data
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Validate form data
        if not current_password or not new_password or not confirmation:
            return apology("Please fill out all required fields", 400)

        # Query database for the current user
        user = db.execute(
            "SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"]
        )

        # Ensure the current password is correct
        if not check_password_hash(user[0]["password"], current_password):
            return apology("Current Password Is Incorrect", 400)

        # Ensure the new password and confirmation match
        if new_password != confirmation:
            return apology("New Password Do Not Match", 400)

        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        # Update the user's password in the database
        db.execute(
            "UPDATE users SET password = :password WHERE id = :user_id",
            password=hashed_password,
            user_id=session["user_id"],
        )

        # Display success
        flash("Password changed successfully")
        return redirect("/dashboard")

    else:
        # If the request method is GET, provide the form for changing the password
        return render_template("change_password.html")


if __name__ == "__main__":
    app.run(debug=True)
