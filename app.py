import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.filters["usd"] = usd
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///finance.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    total_portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = ?;", session['user_id'])
    total_cash = db.execute("SELECT cash FROM users WHERE id = ?;", session['user_id'])
    total_cash = total_cash[0]['cash']
    total_value = total_cash
    for i in total_portfolio:
        temp_price = lookup(i['share_symbol'])
        i['share_price'] = temp_price['price']
        i['total'] = i['share_qty'] * i['share_price']
        total_value += i['total']
    return render_template("index.html", allportfolio=total_portfolio, cash=total_cash, allvalue=round(total_value, 2))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol", 404)
        elif not request.form.get("shares"):
            return apology("must provide share quantity", 404)
        else:
            buysymbol = request.form.get("symbol")
            buyqty = request.form.get("shares")
            if (buyqty.isnumeric() != True or int(buyqty) < 0):
                return apology("Please provide valid quantity", 400)
            buyqty = request.form.get("shares", type=int)
            try:
                buydata = lookup(buysymbol)
                logged_in_user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
                logged_in_user_cash = logged_in_user_cash[0]['cash']
                if (float(logged_in_user_cash) < float((float(buydata["price"]) * float(buyqty)))):
                    return apology("CAN'T AFFORD", 400)
                else:
                    db.execute("UPDATE users  SET cash = ? WHERE id = ?", (logged_in_user_cash - (buydata['price'] * buyqty)), session["user_id"])
                    db.execute("INSERT INTO transactions (transaction_cost, transaction_type, share_name, share_symbol, share_qty, share_price, user_id) VALUES (?, ?, ?, ?, ?, ?, ?);",
                               buydata['price'] * (buyqty), 'buy', buydata['name'], buydata['symbol'], buyqty, buydata['price'], session['user_id'])
                    check = db.execute("SELECT * FROM portfolio WHERE user_id = ? AND share_symbol = ?;", session['user_id'], buydata['symbol'])
                    if (len(check) == 0):
                        db.execute("INSERT INTO portfolio (user_id, share_name, share_symbol, share_qty) VALUES (?, ?, ?, ?);",
                                   session['user_id'], buydata['name'], buydata['symbol'], buyqty)
                    else:
                        check2 = db.execute("SELECT * FROM portfolio WHERE user_id = ? AND share_symbol = ?", session['user_id'], buydata['symbol'])
                        final_qty = check2[0]['share_qty'] + buyqty
                        db.execute("UPDATE portfolio SET share_qty = ? WHERE user_id = ? AND share_symbol = ?",
                                   final_qty, session['user_id'], buydata['symbol'])
            except (KeyError, TypeError, ValueError):
                return apology("INVALID SYMBOL ?", 400)
        return redirect("/")
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    history = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", session['user_id'])
    return render_template("history.html", history=history)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        else:
            quotesymbol = request.form.get("symbol")
            try:
                quoted = lookup(quotesymbol)
                quoted['price'] = usd(quoted['price'])
                return render_template("quoted.html", symbol=quoted['symbol'], name=quoted['name'], price=quoted['price'])
            except (KeyError, TypeError, ValueError):
                return apology("INVALID SYMBOL ?", 400)
    elif request.method == "GET":
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must provide password", 400)
        username = request.form.get('username').strip()
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        if (len(username) > 1):
            usernamecheck = db.execute("SELECT * FROM users WHERE username = ?", username)
            if (password != confirmation):
                return apology("Enter details correctly", 400)
            if (len(usernamecheck) < 1 and password == confirmation):
                hash = generate_password_hash(password)
                db.execute('INSERT INTO users (username, hash)VALUES (?, ?);', username, hash)
                return redirect("/login")
        return apology("USERNAME ALREADY EXISTS", 400)
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        elif not request.form.get("shares"):
            return apology("must provide sell quantity ", 403)
        sellsymbol = request.form.get("symbol")
        sellqty = request.form.get("shares", type=float)
        check = db.execute("SELECT * FROM portfolio WHERE user_id = ? AND share_symbol = ?", session["user_id"], sellsymbol)
        if (len(check) > 0 and check[0]['share_qty'] >= sellqty):
            try:
                data_from_api = lookup(sellsymbol)
                totalsellvalue = data_from_api['price'] * sellqty
            except (KeyError, TypeError, ValueError):
                return apology("INVALID SYMBOL ?", 400)
            cashwas = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
            cashnow = totalsellvalue + cashwas[0]['cash']
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cashnow, session["user_id"])
            db.execute("INSERT INTO transactions (transaction_cost,transaction_type,share_name,share_symbol,share_qty,share_price,user_id)VALUES (?,?,?,?,?,?,?)",
                       totalsellvalue, "sell", data_from_api['name'], data_from_api['symbol'], sellqty, data_from_api['price'], session['user_id'])
            if (sellqty == check[0]['share_qty']):
                db.execute("DELETE FROM portfolio WHERE user_id = ? AND share_symbol = ?", session['user_id'], sellsymbol)
            elif (sellqty < check[0]['share_qty']):
                qty = (check[0]['share_qty'] - sellqty)
                db.execute("UPDATE portfolio SET share_qty = ? WHERE user_id = ? AND share_symbol = ?",
                           qty, session['user_id'], sellsymbol)
        elif (len(check) < 0 or check[0]['share_qty'] < sellqty):
            return apology("TOO MANY SHARES", 400)
        return index()
    else:
        stockname = db.execute('SELECT share_symbol FROM portfolio WHERE user_id = ?', session['user_id'])
        stockname = [x['share_symbol'] for x in stockname]
        return render_template('sell.html', allstocks=stockname)

@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    if request.method == "POST":
        if not request.form.get("CurrentPassword") or not request.form.get("NewPassword") or not request.form.get("NewPasswordagain"):
            return apology("Please provide all details", 400)
        CurrentPass = request.form.get("CurrentPassword")
        NewPass = request.form.get("NewPassword").strip()
        NewPassagain = request.form.get("NewPasswordagain").strip()
        if (NewPass != NewPassagain):
            return apology("Please enter details correctly", 400)
        database = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if (check_password_hash(database[0]['hash'], CurrentPass) == False):
            return apology("Current Password is wrong", 400)
        else:
            NewPass = generate_password_hash(NewPass)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", NewPass, session["user_id"])
        return redirect("/logout")
    else:
        return render_template('changepassword.html')
