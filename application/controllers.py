from flask import request, session, render_template, redirect, flash
from application.models import db, Admin, User, Lot, Spot, Reservation
from app import app
from sqlalchemy import desc, func
from datetime import datetime


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# LOGIN
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter(
            User.username == username, User.password == password
        ).first()
        admin = Admin.query.filter(
            Admin.username == username, Admin.password == password
        ).first()

        if user:
            session["username"] = user.username
            session["role"] = "user"
            return redirect(f"/user_dashboard/{user.id}")
        elif admin:
            session["username"] = admin.username
            session["role"] = "admin"
            return redirect("/admin_dashboard")
        else:
            flash("Invalid credentials")
            return redirect("/")

    return render_template("login.html")


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# ADMIN DASHBOARD
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/admin_dashboard")
def admin_dashboard():
    if "role" in session and session["role"] == "admin":
        lots = Lot.query.all()
        lot_data = []

        for lot in lots:
            lot_id = lot.id
            total_spots = (
                db.session.query(func.count(Spot.id))
                .filter(Spot.l_id == lot_id)
                .scalar()
            )
            available_spots = (
                db.session.query(func.count(Spot.id))
                .filter(Spot.l_id == lot_id, Spot.status == "A")
                .scalar()
            )
            spots = (
                db.session.query(Spot.id, Spot.status).filter(Spot.l_id == lot_id).all()
            )
            occupied_spots = total_spots - available_spots

            lot_data.append(
                {
                    "lot": lot,
                    "total": total_spots,
                    "available": available_spots,
                    "occupied": occupied_spots,
                    "spots": spots,
                }
            )

        return render_template("admin_dashboard.html", lot_data=lot_data)


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# LOGOUT
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect("/")


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# REGISTRATION
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        ph_num = request.form["ph_num"]
        username = request.form["username"]
        password = request.form["password"]

        u = db.session.query(User).filter(User.username == username).first()
        if u:
            flash("Username already exists. Please choose a different username.")
            return redirect("/register")

        new_user = User(name=name, username=username, ph_num=ph_num, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.")
        return redirect("/")
    return render_template("register.html")


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# USER DASHBOARD
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/user_dashboard/<int:id>", methods=["GET", "POST"])
def user_dashboard(id):
    if session.get("role") != "user":
        return redirect("/")

    user = User.query.filter(User.id == id).first()
    lot = None
    spot = None

    if request.method == "GET" and request.args.get("lot_id"):
        lot_id = request.args.get("lot_id")
        lot = Lot.query.get(lot_id)
        spot = Spot.query.filter(Spot.l_id == lot_id, Spot.status == "A").first()

    if request.method == "POST":
        lot_id = request.form["lot_id"]
        reg_num = request.form["reg"]

        lot = Lot.query.get(lot_id)
        spot = Spot.query.filter(Spot.l_id == lot_id, Spot.status == "A").first()

        if spot:
            new_reservation = Reservation(
                u_id=user.id,
                l_id=lot.id,
                s_id=spot.id,
                reg_num=reg_num,
                start_time=datetime.now(),
            )
            spot.status = "O"
            spot.reg_num = reg_num

            db.session.add(new_reservation)
            db.session.commit()
            flash("Spot reserved successfully!")
        else:
            flash("No available spots in this lot.")
        return redirect(f"/user_dashboard/{id}?lot_id={lot_id}")

    lots = Lot.query.all()
    reservations = Reservation.query.filter(Reservation.u_id == user.id).join(Lot).all()

    return render_template(
        "user_dashboard.html",
        user=user,
        lot=lot,
        lots=lots,
        spot=spot,
        reservations=reservations,
    )


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# ADD LOTS
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/add_lots", methods=["GET", "POST"])
def add_lots():
    if session.get("role") != "admin":
        return redirect("/")

    if request.method == "POST":
        location = request.form["location"]
        address = request.form["address"]
        pincode = request.form["pincode"]
        price = request.form["price"]
        max_spots = int(request.form["max_spots"])

        new_lot = Lot(
            loc=location,
            address=address,
            pincode=pincode,
            price_per_hour=price,
            max_spots=max_spots,
        )
        db.session.add(new_lot)
        db.session.commit()
        lot_id = new_lot.id

        for i in range(1, max_spots+1):
            add_spot = Spot(l_id=lot_id, status="A", spot_number=i)
            db.session.add(add_spot)
        db.session.commit()

        flash(f"Parking lot '{location}' added with {max_spots} spots.")
        return redirect("/admin_dashboard")

    return render_template("add_lots.html")


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# OCCUPIED SPOT DETAILS
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/spot_details/<int:id>")
def spot_details(id):
    if session.get("role") != "admin":
        return redirect("/")

    spot = (
        db.session.query(Reservation)
        .join(Lot)
        .join(User)
        .filter(Reservation.s_id == id)
        .first()
    )
    print(spot)
    return render_template("spot_details.html", spot=spot)


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# DELETE LOT
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/delete_lot/<int:id>", methods=["GET", "POST"])
def delete_lot(id):
    if session.get("role") != "admin":
        return redirect("/")

    lot = Lot.query.filter(Lot.id == id).first()

    if request.method == "POST":
        occupied_count = (
            db.session.query(func.count(Spot.id))
            .filter(Spot.l_id == id, Spot.status == "O")
            .scalar()
        )
        if occupied_count > 0:
            flash("Cannot delete lot as it contains occupied spots.")
            return redirect(f"/delete_lot/{id}")

        spot = Spot.query.filter(Spot.l_id == id).all()
        for s in spot:
            db.session.delete(s)
        db.session.commit()

        lot1 = Lot.query.get(id)
        if lot1:
            db.session.delete(lot1)
        db.session.commit()

        flash("Lot Deleted!.")
        return redirect("/admin_dashboard")

    return render_template("delete_lot.html", lot=lot)


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# SHOW REGISTERED USERS
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/get_users", methods=["GET"])
def get_user():
    if session.get("role") != "admin":
        return redirect("/")

    users = User.query.all()
    return render_template("get_users.html", users=users)


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# RELEASE SPOT
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/release_spot/<int:user_id>/<int:reservation_id>", methods=["GET", "POST"])
def release(user_id, reservation_id):
    if session.get("role") != "user":
        return redirect("/")

    reservation = Reservation.query.filter(
        Reservation.id == reservation_id, Reservation.end_time == None
    ).first()

    if not reservation:
        flash("Spot released!")
        return redirect(f"/user_dashboard/{user_id}")

    end_time = datetime.now()
    duration_hours = max((end_time - reservation.start_time).total_seconds() / 3600, 1)
    cost = round(duration_hours * reservation.lot.price_per_hour, 2)

    reservation.end_time = end_time
    reservation.cost = cost
    reservation.spot.status = "A"

    db.session.commit()

    return render_template(
        "release_spot.html", reservation=reservation, user_id=user_id
    )


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# EDIT LOT INFO
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/edit/<int:lot_id>", methods=["GET", "POST"])
def edit_lot(lot_id):
    if session.get("role") != "admin":
        return redirect("/")

    lot = Lot.query.filter(Lot.id == lot_id).first()
    if not lot:
        flash("Parking lot not found.")
        return redirect("/admin_dashboard")

    if request.method == "POST":
        new_name = request.form["name"]
        new_address = request.form["address"]
        new_pincode = request.form["pincode"]
        new_price = float(request.form["price_per_hour"])
        new_max_spots = int(request.form["max_spots"])

        current_spots = lot.max_spots
        diff = new_max_spots - current_spots

        lot.loc = new_name
        lot.address = new_address
        lot.pincode = new_pincode
        lot.price_per_hour = new_price
        lot.max_spots = new_max_spots

        if diff > 0:
            for i in range(current_spots+1, new_max_spots+1):
                new_spot = Spot(l_id=lot_id, status="A", spot_number=i)
                db.session.add(new_spot)
        elif diff < 0:
            removable = (
                db.session.query(Spot.id)
                .filter(Spot.l_id == lot_id, Spot.status == "A")
                .order_by(desc(Spot.id))
                .limit(abs(diff))
                .all()
            )
            if len(removable) < abs(diff):
                flash("Cannot reduce spots. Not enough available spots to remove.")
                return redirect(f"/edit/{lot_id}")
            for (spot_id,) in removable:
                spot = Spot.query.get(spot_id)
                if spot:
                    db.session.delete(spot)

        db.session.commit()
        flash("Parking lot updated successfully.")
        return redirect(f"/admin_dashboard")

    return render_template("edit.html", lot=lot)


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# EDIT PROFILE
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/edit_profile/<int:id>", methods=["GET", "POST"])
def edit_profile(id):
    if session.get("role") != "user":
        return redirect("/")

    user = User.query.filter(User.id == id).first()
    if not user:
        flash("User not found.")
        return redirect("/user_dashboard")

    if request.method == "POST":
        new_name = request.form["name"]
        new_username = request.form["username"]
        new_ph_num = request.form["ph_num"]
        new_password = request.form["pass"]

        user.name = new_name
        user.username = new_username
        user.ph_num = new_ph_num
        user.password = new_password

        db.session.commit()
        flash("Profile updated successfully.")
        return redirect(f"/user_dashboard/{id}")

    return render_template("edit_profile.html", user=user)


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route("/summary")
def summary():
    
    lots = Lot.query.order_by(Lot.id).all()

    
    locations = [lot.loc for lot in lots]

    occupied_counts = []
    available_counts = []

    for lot in lots:
        occ = Spot.query.filter(Spot.l_id==lot.id, Spot.status=="O").count()
        avail = Spot.query.filter(Spot.l_id==lot.id, Spot.status=="A").count()
        occupied_counts.append(occ)
        available_counts.append(avail)

    return render_template("summary.html", locations=locations, occupied_counts=occupied_counts, available_counts=available_counts)