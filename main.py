import pymongo
from flask import Flask, request, render_template, session, redirect
import datetime

import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

from bson import ObjectId

app = Flask(__name__)
app.secret_key = "Shrinika"
my_client = pymongo.MongoClient('mongodb://localhost:27017')
my_db = my_client["Hotel_Management"]
admin_col = my_db['admin']
user_col = my_db['user']
room_type_col = my_db['room_type']
room_col = my_db['room']
bookings_col = my_db['bookings']
payment_col = my_db['payment']

count = admin_col.count_documents({})
if count == 0:
    admin = {"Admin_Email": "admin@gmail.com", "Admin_Password": "admin"}
    admin_col.insert_one(admin)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/adminlog")
def adminlog():
    return render_template("adminlog.html")


@app.route("/adminlog1", methods=['post'])
def adminlog1():
    Admin_Email = request.form.get("Admin_Email")
    Admin_Password = request.form.get("Admin_Password")
    query = {"Admin_Email": Admin_Email, "Admin_Password": Admin_Password}
    admin = admin_col.find_one(query)
    if admin != None:
        session['admin_id'] = str(admin['_id'])
        session['role'] = 'Admin'
        return redirect("admin_home")
    else:
        return render_template("message.html", message="Fail to Log")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/userlog")
def userlog():
    return render_template("userlog.html")


@app.route("/userlog1", methods=['post'])
def userlog1():
    User_Email = request.form.get("User_Email")
    User_Password = request.form.get("User_Password")
    query = {"User_Email": User_Email, "User_Password": User_Password}
    count = user_col.count_documents(query)
    if count > 0:
        user = user_col.find_one(query)
        session['user_id'] = str(user['_id'])
        session['role'] = 'user'
        return render_template("user_home.html")
    else:
        return render_template("message.html", message="Fail to Login")


@app.route("/userreg")
def userreg():
    return render_template("userreg.html")


@app.route("/userreg1", methods=['post'])
def userreg1():
    User_Name = request.form.get("User_Name")
    User_Email = request.form.get("User_Email")
    User_Phone = request.form.get("User_Phone")
    User_Password = request.form.get("User_Password")
    User_Id_Proof = request.files['User_Id_Proof']
    path = APP_ROOT + "/static/myfiles/" + User_Id_Proof.filename
    User_Id_Proof.save(path)
    User_Picture = request.files['User_Picture']
    path = APP_ROOT + "/static/myfiles/" + User_Picture.filename
    User_Picture.save(path)
    query = {"$or": [{"User_Email": User_Email}, {"User_Phone": User_Phone}]}
    count = user_col.count_documents(query)
    if count == 0:
        user = {"User_Name": User_Name, "User_Email": User_Email, "User_Phone": User_Phone,
                "User_Password": User_Password, "User_Picture": User_Picture.filename,
                "User_Id_Proof": User_Id_Proof.filename}
        user_col.insert_one(user)
        return render_template("message.html", message="User Registration Successfull")
    else:
        return render_template("message.html", message="Already Exists")


@app.route("/room_type")
def room_type():
    return render_template("room_type.html")


@app.route("/room_type1", methods=['post'])
def room_type1():
    room_type_name = request.form.get("room_type_name")
    query = {"room_type_name": room_type_name}
    count = room_type_col.count_documents(query)  # so that we dont get same type twice we count
    if count == 0:
        room_type_col.insert_one(query)
        return redirect("/view_room_type")
    else:
        return render_template("amessage.html", mg="Duplicate Room Type")


@app.route("/view_room_type")
def view_room_type():
    room_types = room_type_col.find() # send to view room type page from room type
    return render_template("view_room_type.html", room_types=room_types)


@app.route("/add_room")
def add_room():
    room_types = room_type_col.find()
    return render_template("add_room.html", room_types=room_types)


@app.route("/add_room1", methods=['post'])
def add_room1():
    room_numbers = []
    no_of_rooms = request.form.get("no_of_rooms")
    for i in range(1, int(no_of_rooms) + 1):
        room_numbers.append(request.form.get(str(i)))
    room_type_id = request.form.get("room_type_id")
    room_name = request.form.get("room_name")
    price_per_day = request.form.get("price_per_day")
    allowed_persons = request.form.get("allowed_persons")
    description = request.form.get("description")
    room_image = request.files.get('room_image')
    path = APP_ROOT + "/static/myfiles/" + room_image.filename
    room_image.save(path)
    query = {"room_name": room_name, "room_type_id": room_type_id}
    count = room_col.count_documents(query)
    if count == 0:
        query1 = {"room_type_id": ObjectId(room_type_id), "room_name": room_name, "room_numbers": room_numbers,
                  "room_image": room_image.filename, "no_of_rooms": no_of_rooms, "price_per_day": price_per_day,
                  "allowed_persons": allowed_persons, "description": description}
        room_col.insert_one(query1)
        return render_template("amessage.html", mg="Added Successfully")
    else:
        return render_template("amessage.html", mg="Duplicate Room")


@app.route("/view_room")
def view_room():
    rooms = room_col.find()
    return render_template("view_room.html", rooms=rooms, get_room_type_id=get_room_type_id)


def get_room_type_id(room_type_id):
    query = {"_id": ObjectId(room_type_id)}
    room_type = room_type_col.find_one(query)
    return room_type


@app.route("/search_room")
def search_room():
    room_types = room_type_col.find()
    return render_template("search_room.html", room_types=room_types)


@app.route("/search_room1", methods=['post'])
def search_room1():
    check_in = request.form.get("check_in")
    check_out = request.form.get("check_out")
    room_type_id = request.form.get("room_type_id")
    no_of_rooms_required = request.form.get("no_of_rooms_required")
    check_in = check_in.replace("T", ' ')
    check_out = check_out.replace("T", ' ')
    new_check_in = datetime.datetime.strptime(check_in, "%Y-%m-%d %H:%M")
    new_check_out = datetime.datetime.strptime(check_out, "%Y-%m-%d %H:%M")
    start_date = str(new_check_in.date())
    end_date = str(new_check_out.date())
    diff = (new_check_out - new_check_in)
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    days = int(hours / 24)
    if hours % 24 > 0:
        days = days + 1
    rooms = room_col.find({"room_type_id": ObjectId(room_type_id)})
    rooms2 = []
    for room in rooms:
        print("****")

        booked_rooms = 0
        query = {"$or": [{"room_id": room['_id'], "status": 'Room Booked'},
                         {"room_id": room['_id'], "status": 'Checked In'}]}
        bookings = bookings_col.find(query)
        for booking in bookings:
            old_check_in = booking['check_in']
            old_check_out = booking['check_out']
            old_check_in = datetime.datetime.strptime(old_check_in, "%Y-%m-%d %H:%M")
            old_check_out = datetime.datetime.strptime(old_check_out, "%Y-%m-%d %H:%M")
            if ((new_check_in >= old_check_in and new_check_in <= old_check_out) and (
                    new_check_out >= old_check_in and new_check_out >= old_check_out)):
                booked_rooms = booked_rooms + int(booking['no_of_rooms_required'])
            elif ((new_check_in <= old_check_in and new_check_in <= old_check_out) and (
                    new_check_out >= old_check_in and new_check_out <= old_check_out)):
                booked_rooms = booked_rooms + int(booking['no_of_rooms_required'])
            elif ((new_check_in >= old_check_in and new_check_in >= old_check_out) and (
                    new_check_out <= old_check_in and new_check_out <= old_check_out)):
                booked_rooms = booked_rooms + int(booking['no_of_rooms_required'])
            elif ((new_check_in >= old_check_in and new_check_in <= old_check_out) and (
                    new_check_out >= old_check_in and new_check_out <= old_check_out)):
                booked_rooms = booked_rooms + int(booking['no_of_rooms_required'])
        print(booked_rooms)
        available_rooms = int(room['no_of_rooms']) - booked_rooms
        if available_rooms >= int(no_of_rooms_required):
            rooms2.append(room)
    print(rooms2)
    if len(rooms2) == 0:
        return render_template("umessage.html", msg="Rooms are not available")
    return render_template("search_room1.html", days=days, no_of_rooms_required=no_of_rooms_required, rooms=rooms2,
                           start_date=start_date, end_date=end_date, check_in=check_in, check_out=check_out,
                           get_room_type_id1=get_room_type_id1, room_type_id=room_type_id,
                           formate_date_time=formate_date_time)


def get_room_type_id1(room_type_id):
    query = {"_id": ObjectId(room_type_id)}
    room_type = room_type_col.find_one(query)
    return room_type


def formate_date_time(date):
    date = datetime.datetime.strptime(str(date), "%Y-%m-%d %H:%M")
    date = str(date.date()) + " " + str(date.strftime("%I")) + ":" + str(date.strftime("%M")) + " " + str(
        date.strftime("%p"))
    return date


@app.route("/addBookings", methods=['post'])
def addBookings():
    print("inside")
    rooms = request.get_json()
    rooms["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    rooms["status"] = "Room Selected"
    rooms["user_id"] = ObjectId(session["user_id"])
    result = bookings_col.insert_one(rooms)
    print(result.inserted_id)
    return {"booking_id": str(result.inserted_id)}


@app.route("/book_rooms2", methods=['post'])
def book_rooms2():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    number_of_days = request.form.get('number_of_days')
    no_of_rooms_required = request.form.get('no_of_rooms_required')
    room_id = request.form.get('room_id')
    query = {"start_date": start_date, "end_date": end_date, "check_in": check_in, "check_out": check_out,
             "number_of_days": number_of_days, "no_of_rooms_required": no_of_rooms_required,
             "room_id": ObjectId(room_id), "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
             "status": "Room Selected", "user_id": ObjectId(session["user_id"])}
    result = bookings_col.insert_one(query)
    print(result.inserted_id)
    return redirect("book_rooms?booking_id=" + str(result.inserted_id))


@app.route("/book_rooms")
def book_rooms():
    booking_id = request.args.get("booking_id")
    query = {"_id": ObjectId(booking_id)}
    booking = bookings_col.find_one(query)
    query = {"_id": booking['room_id']}
    room = room_col.find_one(query)
    user_id = booking['user_id']
    query = {"_id": ObjectId(user_id)}
    user = user_col.find_one(query)
    User_Name = user['User_Name']
    totalPrice = int(room['price_per_day']) * int(booking['no_of_rooms_required']) * int(booking['number_of_days'])
    query = {"$set": {"totalPrice": totalPrice}}
    bookings_col.update_one({"_id": ObjectId(booking_id)}, query)
    query = {"_id": ObjectId(booking_id)}
    booking = bookings_col.find_one(query)
    return render_template("book_rooms.html", booking=booking, User_Name=User_Name, get_room_id=get_room_id, int=int)


def get_room_id(room_id):
    query = {"_id": ObjectId(room_id)}
    room = room_col.find_one(query)
    return room


@app.route("/pay_order", methods=['post'])
def pay_order():
    totalPrice = request.form.get("totalPrice")
    booking_id = request.form.get("booking_id")
    advance_amount = request.form.get("advance_amount")
    user_id = session['user_id']
    date = str(datetime.datetime.now().date())
    status = "Payment Successfully"
    payment = {"booking_id": ObjectId(booking_id), "user_id": ObjectId(user_id), "date": date, "status": status,
               "amount": advance_amount}
    payment_col.insert_one(payment)
    query = {'_id': ObjectId(booking_id)}
    query1 = {"$set": {"status": "Room Booked", "totalPrice": totalPrice, "advance_amount": advance_amount}}
    bookings_col.update_one(query, query1)
    return render_template("pay_order.html")


@app.route("/bookings")
def bookings():
    booking_type = request.args.get("booking_type")
    booking_date = request.args.get("booking_date")
    today = str(datetime.datetime.now().date())
    if booking_date == None:
        booking_date = str(datetime.datetime.now().date())
    if session['role'] == 'user':
        if booking_type == None:
            query = {"$or": [{"status": "Room Booked", "user_id": ObjectId(session['user_id'])},
                             {"status": "Checked In", "user_id": ObjectId(session['user_id'])},
                             {"status": "Checked Out", "user_id": ObjectId(session['user_id'])}]}
        else:
            query = {"$or": [{"status": "Vacated", "user_id": ObjectId(session['user_id'])},
                             {"status": "Room Cancelled", "user_id": ObjectId(session['user_id'])}]}
    elif session['role'] == 'Admin':
        if booking_type == 'check_in':
            query = {"start_date": booking_date, "status": "Room Booked"}
        elif booking_type == 'check_out':
            query = {"$or": [{"end_date": booking_date, "status": "Checked In"}, {"status": "Checked Out"}]}
        elif booking_type == 'history':
            query = {"$or": [{"end_date": booking_date, "status": "Checked Out"},
                             {"end_date": booking_date, "status": "Vacated"},
                             {"status": "Room Cancelled", "cancelled_date": booking_date}]}
    bookings = bookings_col.find(query)
    return render_template("bookings.html", bookings=bookings, get_room_id2=get_room_id2, today=today,
                           booking_date=booking_date, booking_type=booking_type,
                           get_available_rooms=get_available_rooms)


def get_available_rooms(booking_id):
    query = {"_id": ObjectId(booking_id)}
    booking2 = bookings_col.find_one(query)
    check_in = booking2['check_in']
    check_out = booking2['check_out']
    new_check_in = datetime.datetime.strptime(check_in, "%Y-%m-%d %H:%M")
    new_check_out = datetime.datetime.strptime(check_out, "%Y-%m-%d %H:%M")
    room = room_col.find_one({"_id": booking2['room_id']})
    available_rooms = []
    booked_rooms = []
    bookings = bookings_col.find({"room_id": room['_id'], "_id": {"$ne": booking2['_id']}})
    for booking in bookings:
        old_check_in = booking['check_in']
        old_check_out = booking['check_out']
        old_check_in = datetime.datetime.strptime(old_check_in, "%Y-%m-%d %H:%M")
        old_check_out = datetime.datetime.strptime(old_check_out, "%Y-%m-%d %H:%M")
        if ((new_check_in >= old_check_in and new_check_in <= old_check_out) and (
                new_check_out >= old_check_in and new_check_out >= old_check_out)):
            if 'selectedRooms' in booking:
                for selectedRoom in booking['selectedRooms']:
                    booked_rooms.append(selectedRoom)
        elif ((new_check_in <= old_check_in and new_check_in <= old_check_out) and (
                new_check_out >= old_check_in and new_check_out <= old_check_out)):
            if 'selectedRooms' in booking:
                for selectedRoom in booking['selectedRooms']:
                    booked_rooms.append(selectedRoom)
        elif ((new_check_in >= old_check_in and new_check_in >= old_check_out) and (
                new_check_out <= old_check_in and new_check_out <= old_check_out)):
            if 'selectedRooms' in booking:
                for selectedRoom in booking['selectedRooms']:
                    booked_rooms.append(selectedRoom)
        elif ((new_check_in >= old_check_in and new_check_in <= old_check_out) and (
                new_check_out >= old_check_in and new_check_out <= old_check_out)):
            if 'selectedRooms' in booking:
                for selectedRoom in booking['selectedRooms']:
                    booked_rooms.append(selectedRoom)
    print("****")
    print(booked_rooms)

    for room_number in room['room_numbers']:
        if room_number not in booked_rooms:
            available_rooms.append(room_number)
        if len(available_rooms) > 0:
            room['room_numbers'] = available_rooms
    print(room)
    return room


def get_room_id2(room_id):
    query = {"_id": ObjectId(room_id)}
    room = room_col.find_one(query)
    return room


@app.route("/booking_cancle")
def booking_cancle():
    booking_id = request.args.get("booking_id")
    query = {'_id': ObjectId(booking_id)}
    query1 = {"$set": {"status": "Room Cancelled", "cancelled_date": str(datetime.datetime.now().date())}}
    bookings_col.update_one(query, query1)
    return render_template("umessage.html", msg="Room Cancelled")


@app.route("/user_home")
def user_home():
    return render_template("user_home.html")


@app.route("/check_in", methods=['post'])
def check_in():
    data = request.get_json()
    print(data)
    booking_id = data["booking_id"]
    query = {'_id': ObjectId(booking_id)}
    query1 = {"$set": {"status": "Checked In", "selectedRooms": data['selectedRooms']}}
    bookings_col.update_one(query, query1)
    return render_template("amessage.html", mg="Checked In")


@app.route("/check_out")
def check_out():
    booking_id = request.args.get("booking_id")
    query = {'_id': ObjectId(booking_id)}
    query1 = {"$set": {"status": "Checked Out"}}
    bookings_col.update_one(query, query1)
    return render_template("amessage.html", mg="Checked Out")


@app.route("/check_out2")
def check_out2():
    booking_id = request.args.get("booking_id")
    query = {'_id': ObjectId(booking_id)}
    booking = bookings_col.find_one(query)
    return render_template("check_out.html", booking=booking, float=float)


@app.route("/check_out3", methods=['post'])
def check_out3():
    booking_id = request.form.get("booking_id")
    amount = request.form.get('amount')
    query = {'_id': ObjectId(booking_id)}
    query1 = {"$set": {"status": "Vacated"}}
    bookings_col.update_one(query, query1)
    status = "Payment Successfully"
    payment = {"booking_id": ObjectId(booking_id), "user_id": ObjectId(session['user_id']),
               "date": str(datetime.datetime.now()), "status": status, "amount": amount}
    payment_col.insert_one(payment)
    return render_template("umessage.html", mg="Checked Out")


@app.route("/payment_details")
def payment_details():
    booking_id = request.args.get("booking_id")
    query = {'booking_id': ObjectId(booking_id)}
    payments = payment_col.find(query)
    return render_template("payment_details.html", payments=payments, get_user_id=get_user_id)


def get_user_id(user_id):
    query = {"_id": ObjectId(user_id)}
    user = user_col.find_one(query)
    return user


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")


app.run(debug=True)
