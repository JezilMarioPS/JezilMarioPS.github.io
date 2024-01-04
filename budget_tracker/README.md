# Budget Tracker
#### Video Demo:  < https://youtu.be/dl-JaSj5Sqc?si=Zey_bDTOhlQie2Or >
#### Description:

## Project Summary

The Budget Tracker is a web app that is made to help the user to manage and track their finances by tracking their income and expenses, also categorizing transactions, visualizing financial data through pie charts, and also providing insightful transaction summaries.

## Project Overview

The Budget Tracker is a web app to help users to manage their finances effectively, therby reducing the dependancy to remember every transactions by humans. Here the users can track their income and expenses by adding those to the web app, also the user can categorize those transactions based on the caterogies perferred by the user. The user can also lookup the transaction history of the income and expenses. The budget tracker web app has a wide range of features, including adding a new transaction, managing categories, viewing recent transactions and deleting any unwanted transaction history that is being added by any mistake. The user can also check for total income, total expense and money left over over a specified date range in the dashboard using the different features implemented in the web app. The users can also view transaction summaries for both income and expenses, as well as visualize them using pie charts provided in the web app. Additionally, the web app allows users to change their current password to a new password for added security.

## Files Overview

- **app.py**: The app.py is the main python file for the implementation of the web app. It includes routes for the home page, dashboard, add transactions, login, logout, register, manage categories, recent transactions, and change the current password. It also utilizes functions for converting the time to the user's local time for added convenience and also calculating the transaction summaries.

- **helpers.py**: This python file contains helper functions for the main python file. The helper functions are apology, which generates error messages for the user when any of the input validation fails, and the other helper file is  login_required, which make sure that the user is logged in before using the web app.

- **templates/**: The templates contains HTML templates used for different pages. Templates include:
  - **dashboard.html**: This is the main dashboard for displaying recent transactions, income, expenses, transaction summaries, and pie chart. All the details for the transactions can be accessed in the dashboard, making it easier for the user to identify and lookup the finances.
  - **add_transaction.html**: It is used to add new transaction to the database. The transactions can be either income or expense based on the user perference and also the transaction categories can also be selected by the user in a dropdown list provided int the page.
  - **login.html**: Displays the login page for the user to login. When the user types the password, it is hidden for added security.
  - **register.html**: Displays the registration page for a new user to register an account. It consists of user name and password section to register a new user. Here i added for passwords to have symbols, numbers and letters for added security.
  - **manage_categories.html**: The manage category allows the users to view the categories which are available for the dropdown in the add_transaction route.
  - **add_category.html**: It is used to add new categories for the dropdown in the add transaction page. The add category page can also be used to show and hide the categories, and also delete any existing categories which may be unnecessary for the user. There will be five default categories which is most common in users daily life.  The default categories can also be deleted or hidden according to the users need.
  - **apology.html**: Apology file is used to display the error messages to users when the input validation fails.
  - **change_password.html**: The change password is used to change the users current password with the new password.
  - **recent_transactions.html**: Recent transaction displays the transaction history of the user, it also includes a delete button to delete any unwanted user transaction from the history which is either added by mistake or the user dont need that in the transaction history.
  - **layout.html**: This used as a common main layout template shared among other templates.

- **static/**: The static directory contains static files for the styles.css file and images used for the web app.
  - **styles.css**: This file is used for the overall styles of the web app, including dashboard etc.

- **budget.db**: SQLite3 database file for storing user information, transactions, and categories etc.


## Design Choices

- **User Authentication**: The user passwords are hashed for extra security.

- **Timezone Handling**: The web app shows the user's timezone from the users system to display the user's local time.

**Category Management**: Users can add, hide, and delete categories. Five default categories are added for new users during the first user registration. The default categories are added for user convenience and can be deleted or hidden by the user if not needed.

### Pie Charts

- The dashboard includes pie charts for the users to view their financial data more easily. The charts include:

- **Expense Distribution by Category**: A pie chart displaying the expense distribution for the different categories.

- **Income Distribution by Category**: A pie chart displaying the income distribution for the different categories.

### Dashboard Template

The dashboard.html template provides the user with a simple overview of the user's financial activities. It includes:

- A date range selection form allowing users to filter transactions based on a specified date.
- Total Income, Total Expenses, and Money Left Over columns provide the summary of the user's total transactions during a specified date range.
- Pie charts showing the Expense and Income Distribution by Category. The pie chart can also show the overall percentage per category for the user transaction for income as well as expense.
- Transaction summary table showing the number of transactions and total values for expenses and income.
- A recent transaction table displaying recent transactions for the last 30 days or transactions for the selected date range.


## Project Outcomes

- **Good Outcome**: Implementing core features like adding transactions, viewing a dashboard, and basic category management.

- **Better Outcome**: Enhancing user experience with additional features such as interactive graphs, transaction search, and improved category management.

- **Best Outcome**: Implementing advanced features like budget forecasting, recurring transactions, and integration with financial APIs for real-time data.

## Next Steps

1. **Testing**: Implementing comprehensive testing for the web app and security testing to ensure the error free and more added security for the web app.

2. **UI/UX Enhancement**: Improving the user interface for better usability.

3. **Security Audit**: Conducting a thorough security check to identify and address potential vulnerabilities and issues.

4. **Documentation**: Creating a detailed documentation of the web app for users, explaining how to use the application.

6. **User Feedback**: Collecting user feedback for future improvements and bug fixes.


## How to Run the Application

1. Install the required dependencies using pip install -r requirements.txt.
2. Run the application with python app.py.
3. Access the application in a web browser at localhost:5000.
# Project
# Project
