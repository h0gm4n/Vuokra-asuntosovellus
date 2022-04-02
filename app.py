from flask import Flask
from flask import redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute("SELECT * FROM apartments ORDER BY id DESC")
    apartments = result.fetchall()
    return render_template("index.html", count=len(apartments), apartments=apartments)

@app.route("/login",methods=["POST", "GET"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    # Tarkistetaan onko käyttäjä olemassa
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    if not user:
        # Jos käyttäjä ei olemassa, sivu päivittyy
        return redirect("/")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username     # Voi kirjautua
            return redirect("/")
        else:
            # Jos salasana väärin, sivu päivittyy
            return redirect("/")

@app.route("/register", methods=["POST", "GET"])
def register():
    return render_template("register.html")

@app.route("/create",methods=["POST", "GET"])
def create():
    username = request.form["username"]
    password = request.form["password"]
    # Jos valitut tunnukset yli 5 merkkiä, luodaan käyttäjä
    if len(username)>5 and len(password)>5:
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
        db.session.execute(sql, {"username": username, "password": hash_value})
        db.session.commit()
        return redirect("/")
    return redirect(url_for("register"))

@app.route("/palaa")
def palaa():
    return redirect("/")

@app.route("/result")
def result():

    query = request.args["query"]
    min_area = request.args["min_area"]
    max_area = request.args["max_area"]
    roomcount = request.args.getlist("roomcount")
    buildingtype = request.args.getlist("buildingtype")
    condition = request.args.getlist("condition")
    if query == "" and min_area == "" and max_area == "" and len(roomcount)==0 and len(buildingtype)==0 and len(condition)==0:
        sql = "SELECT * FROM apartments"
    else:
        sql = "SELECT * FROM apartments WHERE "
        
    on_ehtoja = False
    if query != "":
        sql += f"LOWER(location)=LOWER('{query}') "
        on_ehtoja = True
    if min_area != "":
        if on_ehtoja:
            sql += f"AND area>={min_area} "
        else:
            sql += f"area>={min_area} "
            on_ehtoja = True
    if max_area != "":
        if on_ehtoja:
            sql += f"AND area<={max_area} "
        else:
            sql += f"area<={max_area} "
            on_ehtoja = True

    a = True
    b = 0
    for i in roomcount:
        if len(roomcount)==1:
            if on_ehtoja:
                sql+=f"AND rooms={i}"
            else:
                sql+=f"rooms={i} "
                on_ehtoja = True
        elif a:
            if on_ehtoja:
                sql+=f"AND (rooms={i} "
            else:
                sql+=f"(rooms ={i} "
                on_ehtoja = True
            a = False
            b += 1
        else:
            sql+=f"OR rooms={i}"
            b += 1
        if b==len(roomcount):
            sql+=") "

    a = True
    b = 0
    for i in buildingtype:
        if len(buildingtype)==1:
            if on_ehtoja:
                sql+=f"AND building='{i}'"
            else:
                sql+=f"building='{i}' "
                on_ehtoja = True
        elif a:
            if on_ehtoja:
                sql+=f"AND (building='{i}' "
            else:
                sql+=f"(building='{i}' "
                on_ehtoja = True
            a = False
            b += 1
        else:
            sql+=f"OR building='{i}'"
            b += 1
        if b==len(buildingtype):
            sql+=") "

    for i in condition:
        if len(condition)==1:
            if on_ehtoja:
                sql+=f"AND condition='{i}'"
            else:
                sql+=f"condition='{i}' "
                on_ehtoja = True
        elif a:
            if on_ehtoja:
                sql+=f"AND (condition='{i}' "
            else:
                sql+=f"(condition='{i}' "
                on_ehtoja = True
            a = False
            b += 1
        else:
            sql+=f"OR condition='{i}'"
            b += 1
        if b==len(condition):
            sql+=") "

    result = db.session.execute(sql)
    results = result.fetchall()
    return render_template("result.html", results=results)

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/add", methods=["POST"])
def add():
    area = request.form["area"]
    roomcount = request.form["roomcount"]
    buildingtype = request.form["buildingtype"]
    location = request.form["location"]
    rent = request.form["rent"]
    condition = request.form["condition"]
    descr = request.form["descr"]
    sql = f"INSERT INTO apartments (area, rooms, building, location, rent, condition, descr) VALUES ({area}, {roomcount}, '{buildingtype}', '{location}', {rent}, '{condition}', '{descr}');"
    db.session.execute(sql)
    db.session.commit()
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

