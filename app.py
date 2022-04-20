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

@app.route("/order", methods=["POST", "GET"])
def order_cheap():
    try:
        apartment_order = request.form["order"]
        if apartment_order == "cheap":
            result = db.session.execute("SELECT * FROM apartments ORDER BY rent")
            results = result.fetchall()
        elif apartment_order == "expensive":
            result = db.session.execute("SELECT * FROM apartments ORDER BY rent DESC")
            results = result.fetchall()
        elif apartment_order == "small":
            result = db.session.execute("SELECT * FROM apartments ORDER BY area")
            results = result.fetchall()
        elif apartment_order == "big":
            result = db.session.execute("SELECT * FROM apartments ORDER BY area DESC")
            results = result.fetchall()

        return render_template("order.html", results=results)
    except:
        return redirect("/")

@app.route("/login",methods=["POST", "GET"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if "admin" in username:
        sql = "SELECT id, password FROM admins WHERE username=:username"
    else:
        sql = "SELECT id, password FROM users WHERE username=:username"

    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    if not user:
        no_user = True
        return render_template("index.html", no_user=no_user)
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username     # Voi kirjautua
            return redirect("/")
        else:
            no_user = True
            return render_template("index.html", no_user=no_user)

@app.route("/register", methods=["POST", "GET"])
def register():
    return render_template("register.html")

@app.route("/create",methods=["POST", "GET"])
def create():
    name_taken = False
    too_long_user = False
    too_short_user = False
    too_long_pass = False
    too_short_pass = False
    pws_not_equal = False
    username = request.form["username"]
    password = request.form["password"]
    password_again = request.form["password_again"]

    if password != password_again:
        pws_not_equal = True

    sqlusers = f"SELECT username FROM users WHERE username='{username}'"
    result = db.session.execute(sqlusers)
    user = result.fetchone()

    if user:
        name_taken = True

    if 15<len(username) and not name_taken and not pws_not_equal:
        too_long_user = True
    elif 6>len(username) and not name_taken and not pws_not_equal:
        too_short_user = True

    if 15<len(password) and not name_taken and not pws_not_equal:
        too_long_pass = True
    elif 6>len(password) and not name_taken and not pws_not_equal:
        too_short_pass = True

    if 15>=len(username)>=6 and 15>=len(password)>=6 and not name_taken and not pws_not_equal:
        hash_value = generate_password_hash(password)
        if "admin" not in username:
            sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
        else:
            sql = "INSERT INTO admins (username, password) VALUES (:username, :password)"
        db.session.execute(sql, {"username": username, "password": hash_value})
        db.session.commit()
        session["username"] = username
        return redirect("/")

    return render_template("register.html", name_taken=name_taken, too_long_user=too_long_user,
                           too_short_user=too_short_user, too_long_pass=too_long_pass,
                           too_short_pass=too_short_pass, pws_not_equal=pws_not_equal)

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
    if query == "" and min_area == "" and max_area == "" and \
            len(roomcount)==0 and len(buildingtype)==0 and len(condition)==0:
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
    return render_template("result.html", resultslen=len(results), results=results)

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
    sql = f"INSERT INTO apartments (area, rooms, building, location, rent, condition, descr)" \
          f" VALUES ({area}, {roomcount}, '{buildingtype}', '{location}', {rent}, '{condition}', '{descr}');"
    db.session.execute(sql)
    db.session.commit()
    return redirect("/")

@app.route("/add_applied_or_fave", methods=["GET", "POST"])
def add_applied_or_fave():

    username = session["username"]
    user_id_search = f"SELECT id FROM users WHERE username='{username}'"
    user_result = db.session.execute(user_id_search)
    user_id = user_result.fetchone()[0]

    apply = request.form.getlist("apply")
    fave = request.form.getlist("fave")

    for i in range(0, len(apply)):
        sql = f"INSERT INTO applied (user_id, apartment_id) VALUES ({user_id}, {apply[i]})"
        db.session.execute(sql)
        db.session.commit()

    for i in range(0, len(fave)):
        sql = f"INSERT INTO faved (user_id, apartment_id) VALUES ({user_id}, {fave[i]})"
        db.session.execute(sql)
        db.session.commit()


    return redirect("/")


@app.route("/appandfav", methods=["GET", "POST"])
def appandfav():
    username = session["username"]
    user_id_search = f"SELECT id FROM users WHERE username='{username}'"
    user_result = db.session.execute(user_id_search)
    user_id = user_result.fetchone()[0]

    applied_sql = f"SELECT apartment_id FROM applied WHERE user_id={user_id}"
    applied_result = db.session.execute(applied_sql)
    applied_results = applied_result.fetchall()

    faved_sql = f"SELECT apartment_id FROM faved WHERE user_id={user_id}"
    faved_result = db.session.execute(faved_sql)
    faved_results = faved_result.fetchall()

    a_sql_const = True
    f_sql_const = True
    a_sql = ""
    f_sql = ""
    a_results = []
    f_results = []

    if len(applied_results)>=1:
        for i in applied_results:
            b = str(i).strip("(),")
            if a_sql_const:
                a_sql = f"SELECT * FROM apartments WHERE id={int(b)}"
                a_sql_const = False
            else:
                a_sql += f" OR id={int(b)}"
            a_result = db.session.execute(a_sql)
            a_results = a_result.fetchall()


    if len(faved_results)>=1:
        for i in faved_results:
            b = str(i).strip("(),")
            if f_sql_const:
                f_sql = f"SELECT * FROM apartments WHERE id={int(b)}"
                f_sql_const = False
            else:
                f_sql += f" OR id={int(b)}"

            f_result = db.session.execute(f_sql)
            f_results = f_result.fetchall()

    return render_template("appandfav.html", a_resultslen=len(a_results),
                           f_resultslen=len(f_results), a_results=a_results, f_results=f_results)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    result = db.session.execute("SELECT * FROM apartments ORDER BY id DESC")
    apartments = result.fetchall()
    return render_template("delete.html", apartments=apartments)

@app.route("/delete_apartment", methods=["GET", "POST"])
def delete_apartment():
    delete = request.form.getlist("apartment")
    first = True
    sql_applied = ""
    sql_faved = ""
    sql_apartments = ""
    for i in delete:
        if first:
            sql_applied = f"DELETE FROM applied WHERE apartment_id={i}"
            sql_faved = f"DELETE FROM faved WHERE apartment_id={i}"
            sql_apartments = f"DELETE FROM apartments WHERE id={i}"
            first = False
            continue
        sql_applied += f" OR apartment_id={i}"
        sql_faved += f" OR apartment_id={i}"
        sql_apartments += f" OR id={i}"
    db.session.execute(sql_applied)
    db.session.execute(sql_faved)
    db.session.execute(sql_apartments)
    db.session.commit()
    return redirect("/")

@app.route("/manipulate_applied_and_faved", methods=["GET", "POST"])
def manipulate_applied_and_faved():
    username = session["username"]
    user_id_search = f"SELECT id FROM users WHERE username='{username}'"
    user_result = db.session.execute(user_id_search)
    user_id = user_result.fetchone()[0]

    delete_applied = request.form.getlist("delete_applied")
    delete_faved = request.form.getlist("delete_faved")
    fave = request.form.getlist("fave")
    apply = request.form.getlist("apply")
    first = True

    sql = ""
    for i in delete_applied:
        if first:
            sql = f"DELETE FROM applied WHERE user_id='{user_id}' and apartment_id={i}"
            first = False
            continue
        sql += f" OR apartment_id={i}"

    if len(delete_applied)>0:
        db.session.execute(sql)
        db.session.commit()

    sql = ""
    for i in fave:
        sql = f"INSERT INTO faved (user_id, apartment_id) VALUES ({user_id}, {i})"

    if len(fave) > 0:
        db.session.execute(sql)
        db.session.commit()


    first = True
    sql = ""
    for i in delete_faved:
        if first:
            sql = f"DELETE FROM faved WHERE user_id='{user_id}' and apartment_id={i}"
            first = False
            continue
        sql += f" OR apartment_id={i}"

    if len(delete_faved)>0:
        db.session.execute(sql)
        db.session.commit()

    sql = ""
    for i in apply:
        sql = f"INSERT INTO applied (user_id, apartment_id) VALUES ({user_id}, {i})"

    if len(apply) > 0:
        db.session.execute(sql)
        db.session.commit()

    return redirect("/appandfav")


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

