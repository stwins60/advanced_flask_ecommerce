
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Float)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)

def cart():
    return session.setdefault("cart", {})

@app.route("/")
def home():
    products = Product.query.all()
    return render_template("index.html", products=products)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = user.username
            session["admin"] = user.is_admin
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    c = cart()
    c[str(id)] = c.get(str(id),0) + 1
    session["cart"] = c
    return redirect("/cart")

@app.route("/cart")
def view_cart():
    items = []
    total = 0
    for pid,qty in cart().items():
        p = Product.query.get(int(pid))
        subtotal = p.price * qty
        total += subtotal
        items.append({"product":p,"qty":qty,"subtotal":subtotal})
    return render_template("cart.html",items=items,total=total)

@app.route("/checkout")
def checkout():
    session["cart"] = {}
    return render_template("checkout.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/")
    products = Product.query.all()
    return render_template("admin/dashboard.html",products=products)

@app.route("/admin/add",methods=["POST"])
def admin_add():
    if not session.get("admin"):
        return redirect("/")
    p = Product(
        name=request.form["name"],
        price=request.form["price"],
        image=request.form["image"],
        description=request.form["description"]
    )
    db.session.add(p)
    db.session.commit()
    return redirect("/admin")

@app.route("/api/products")
def api_products():
    products = Product.query.all()
    return jsonify([
        {"id":p.id,"name":p.name,"price":p.price,"image":p.image}
        for p in products
    ])

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin",
                         password=generate_password_hash("admin"),
                         is_admin=True)
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
