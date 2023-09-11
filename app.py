from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# (flask --app app.py --debug run) 

app = Flask(__name__)
app.secret_key = 'hello'

db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    try:
        listings = reversed(db.execute("SELECT * FROM listings"))
        user_id = session['user_id']
        user = db.execute('SELECT username FROM users WHERE id = ?', user_id)[0]['username'].capitalize()
        return render_template("index.html", listings=listings, heading="All Listings", user_id=user_id, user=user)
    except:
        return apology("Something went wrong!", 500)

@app.route("/lisitng/<listing_id>")
@login_required
def listing(listing_id):
    try:
        user_id = session["user_id"]
        user = db.execute('SELECT username FROM users WHERE id = ?', user_id)[0]['username'].capitalize()
        cart_user = db.execute("SELECT user_id FROM carts WHERE listing_id = ?", listing_id)
        cart_user_id = []
        for i in cart_user:
            cart_user_id.append(i['user_id'])
        listing = db.execute("SELECT * FROM listings WHERE id = ?", listing_id)[0]
        category = db.execute('SELECT name FROM categories WHERE id = ?', listing['category_id'])[0]['name']
        seller = db.execute("SELECT username FROM users WHERE id = ?", listing['user_id'])[0]['username'].capitalize()
        order_listing = db.execute('SELECT listing_id FROM orders WHERE user_id=?', session["user_id"])
        ids = []
        for i in order_listing:
            ids.append(i["listing_id"])
        is_buy = listing["id"] in ids
        return render_template("listing.html", seller=seller, listing=listing, cart_user_id=cart_user_id, 
        is_buy=is_buy, user_id=user_id, user=user, category=category)
    except:
        return apology("Something went wrong!", 500)


@app.route("/categories")
@login_required
def categories():
    try:
        user_id = session["user_id"]
        user = db.execute('SELECT username FROM users WHERE id = ?', user_id)[0]['username'].capitalize()
        categories = db.execute("SELECT * FROM categories")
        return render_template("categories.html", categories=categories, user=user)
    except:
        return apology("Something went wrong!", 500)


@app.route("/category/<category_id>")
@login_required
def category(category_id):
    try:
        user_id = session["user_id"]
        user = db.execute('SELECT username FROM users WHERE id = ?', user_id)[0]['username']
        category = db.execute("SELECT name FROM categories WHERE id=?", category_id)[0]["name"]
        listings = db.execute("SELECT * FROM listings WHERE category_id =?", category_id)
        return render_template("index.html", listings=listings, heading=category, user=user)
    except:
        return apology("Something went wrong!", 500)


@app.route("/cart")
@login_required
def cart():
    try:
        user_id = session["user_id"]
        user = db.execute('SELECT username FROM users WHERE id = ?', user_id)[0]['username'].capitalize()
        ids = []
        for i in db.execute('SELECT listing_id FROM carts WHERE user_id=?', session["user_id"]):
            ids.append(i['listing_id'])
        listings = reversed(db.execute("SELECT * FROM listings WHERE id IN (?)", ids))
        return render_template("index.html", listings=listings, heading="Your Cart",user=user)
    except:
        return apology("Something went wrong!", 500)



@app.route("/buy/<listing_id>")
@login_required
def buy(listing_id):
    try:
        db.execute("DELETE FROM orders WHERE user_id = ? AND listing_id = ?", session["user_id"], listing_id)
        db.execute("INSERT INTO orders (user_id, listing_id) VALUES (?, ?)", session["user_id"], listing_id)
        return redirect("/orders")
    except:
        return apology("Something went wrong!", 500)


@app.route("/add/<listing_id>")
@login_required
def add_cart(listing_id):
    try:
        db.execute("INSERT INTO carts (user_id, listing_id) VALUES (?, ?)", session["user_id"], listing_id)
        return redirect("/cart")
    except:
        return apology("Something went wrong!", 500)


@app.route("/remove/<listing_id>")
@login_required
def remove_cart(listing_id):
    try:
        db.execute("DELETE FROM carts WHERE user_id=? and listing_id=?", session["user_id"], listing_id)
        return redirect("/cart")
    except: 
        return apology("Something went wrong!", 500)


@app.route("/orders")
@login_required
def orders():
    try:
        user_id = session["user_id"]
        user = db.execute('SELECT username FROM users WHERE id = ?', user_id)[0]['username'].capitalize()
        ids = []
        for i in db.execute('SELECT listing_id FROM orders WHERE user_id=?', session["user_id"]):
            ids.append(i['listing_id'])
        listings = reversed(db.execute("SELECT * FROM listings WHERE id IN (?)", ids))
        return render_template("index.html", listings=listings, heading="Your Orders", user=user)
    except: 
        return apology("Something went wrong!", 500)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    try:
        user_id = session["user_id"]
        user = db.execute('SELECT username FROM users WHERE id = ?', user_id)[0]['username'].capitalize()
        if request.method == "POST":
            category_id = db.execute("SELECT * FROM categories WHERE name = ?", request.form.get("category"))[0]["id"]
            user_id = session["user_id"]
            title = request.form.get("title")
            description = request.form.get("description")
            price = request.form.get("price")
            imageUrl = request.form.get("imageUrl")
            db.execute("INSERT INTO listings (category_id, user_id, title, description, price, imageUrl) VALUES (?, ?, ?, ?, ?, ?)", category_id, user_id, title, description, price, imageUrl, )
            return redirect("/")
        else:
            categories = db.execute("SELECT name FROM categories")
            return render_template("create.html", categories=categories, user=user)
    except: 
        return apology("Something went wrong!", 500)   


@app.route("/delete/<listing_id>")
@login_required
def delete(listing_id):
    try:
        db.execute("DELETE FROM listings WHERE id = ?", listing_id)
        return redirect("/")
    except: 
        return apology("Something went wrong!", 403)
       


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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Must Have Username!")
        if not password:
            return apology("Must Have Password!")
        if not confirmation:
            return apology("Must Have Confirmation!")
        if password != confirmation:
            return apology("Must Match!")

        hash = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            return redirect("/")
        except:
            return apology("Username Already Exists!")
    else:
        return render_template("register.html")

