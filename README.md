# Stock Portfolio Tracker - Flask Web Application
A simple and efficient stock portfolio tracker built with Flask. Track your investments, monitor real-time stock prices, and manage your portfolio seamlessly. Features a user-friendly interface and customizable portfolios for a personalized investment experience. This application allows users to manage and track their US market stock portfolios. Users can register, log in, buy and sell stocks, view transaction history, and analyze their portfolio's performance.

## Table of Contents
- [Getting Started](#getting-started)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Routes](#routes)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

To run this application locally, follow the instructions below.

### Features

- **User Authentication:** Register an account and log in securely.
- **Portfolio Overview:** View your current stock portfolio and cash balance.
- **Buy and Sell Stocks:** Purchase and sell US market stocks easily.
- **Stock Quote:** Get the latest price information for a specific stock.
- **Transaction History:** Track your buying and selling transactions.
- **Change Password:** Change your account password for security.
- **Logout:** Log out of your account securely.

### Prerequisites

Make sure you have the following installed:

- Python
- Flask
- SQLite
- cs50 
- Other dependencies as specified in the `requirements.txt` file

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Shauryainks/Stock-Portfolio-Tracker.git
   cd Stock-Portfolio-Tracker
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python application.py
   ```

The application should be running on [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Usage

- Open your web browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).
- Register a new account or log in with existing credentials.
- Use the navigation menu to access different features:
  - **Portfolio:** View your current US stock portfolio and cash balance.
  - **Buy:** Purchase US stocks by providing the stock symbol and quantity.
  - **Sell:** Sell US stocks from your portfolio.
  - **Quote:** Get the latest price information for a US stock.
  - **History:** View your transaction history.
  - **Change Password:** Change your account password.
  - **Logout:** Log out of your account.

## Routes

- `/`: Home page, requires user authentication.
- `/buy`: Buy US stocks, requires user authentication.
- `/history`: View transaction history, requires user authentication.
- `/login`: Log in to your account.
- `/logout`: Log out of your account.
- `/quote`: Get US stock quotes, requires user authentication.
- `/register`: Register a new account.
- `/sell`: Sell US stocks, requires user authentication.
- `/changepassword`: Change account password, requires user authentication.

## Contributing

If you'd like to contribute to this project, feel free to fork the repository and submit a pull request. Contributions and feedback are always welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
