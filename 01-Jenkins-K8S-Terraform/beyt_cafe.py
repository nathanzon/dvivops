import html, json

from flask import Flask, request

import pymongo
from datetime import datetime

coffee_app = Flask(__name__)


def connect_mongodb():
    # user password
    uri = "mongodb+srv://USERNAME:PASSWORD@espressocluster1.al0msxw.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri)
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("MongoDB connection successfull")
        return client.test
    except Exception as e:
        print(e)
        return 1


@coffee_app.route("/")
def landing_page():
    '''Main landing page with the user input form'''
    body_html = "<h1>Yuriy's Coffee House</h1>"
    body_html += "<p><i>"+datetime.now().strftime("%d.%m.%Y %H:%M")+"</i><p>"
    # Connecting to the database
    db = connect_mongodb()  # client.test
    body_html += "<form action='/api'><table border='0' cellpadding='10' cellspacing='10'>"
    bill = 0
    for coffee in db.Coffee.find():
        body_html += "<tr><td>" + coffee["Name"] + "</td>" + \
                     "<td>" + str(coffee["Price"]) + " NIS</td>" + \
                     "<td><input type='number' id='sold' name='" + coffee["Name"] + "' step='1' max='99' min='" + str(
            coffee["Sold"]) + \
                     "' value='" + str(coffee[
                                           "Sold"]) + "'></td><td><input type='submit' name='order' value='update'></td><td><input type='submit' name='" + \
                     coffee["Name"] + "_delete' value='remove'></td></tr>"
        bill += coffee["Price"] * coffee["Sold"]
    body_html += "<tr><td><input type='text' name='coffee' value='Something new' width=16></td><td><input type='number' name='price' width=2 min='5' max='30'>" \
                 "</td><td>&nbsp;NIS</td><td>&nbsp;</td><td><input type='submit' name='add_coffee' value='Add to the menu'></td></tr>"
    body_html += "</table>"
    # body_html += "<input type='submit' name='order' value='Order coffee'>"
    if bill > 0:
        body_html += "<p>Your order total is <b>" + str(
            bill) + " NIS</b>. To pay the bill please add your credit card number below:"
    body_html += "<p><input type='number' name='cc' max='9999999999999999'><input type='hidden' name='bill' value='" + str(
        bill) + \
                 "'><input type='submit' name='pay' value='Pay the bill'></form>"
    body_html += "<hr><b>Billing history (mongo):</b>"
    for logs in db.Billing.find().sort('id', -1):
        body_html += "<p><pre>" + str(logs["id"]) + "   " + str(logs["message"]) + "</pre>"
    return body_html


@coffee_app.route("/api/", methods=['GET'])
@coffee_app.route("/api", methods=['GET'])
def api_server(order="no"):
    '''Reads the API via location and parses the returned JSON into an HTML page'''
    db = connect_mongodb()
    '''your code for API request and second HTML'''
    args = request.args
    if "order" in args.keys():
        body_html = "<html><title>Updating database...</title><head><meta http-equiv='refresh' content='3; url=/'></head><body>"
        for coffee in db.Coffee.find():
            if (coffee["Name"] in args.keys()) and (int(args[coffee["Name"]]) > coffee["Sold"]):
                buy = int(args[coffee["Name"]])
                buy_message = "Updating " + str(coffee["Name"]) + " to " + str(buy) + " sold items"
                db.Coffee.update_one({'Name': coffee["Name"]}, {"$set": {'Sold': buy}})
                # Update transaction logs
                db.Billing.insert_one({'id': datetime.now(), 'message': buy_message})
    elif "pay" in args.keys():
        body_html = "<html><title>Connecting to the bank...</title><head><meta http-equiv='refresh' content='3; url=/'></head><body>"
        if len(args["cc"]) == 16:
            db.Coffee.update_many({}, {"$set": {'Sold': 0}})
            body_html += "Processing your payment..."
            # Update transaction logs
            pay_message = "Bill of " + args["bill"] + " NIS was paid"
            db.Billing.insert_one({'id': datetime.now(), 'message': pay_message})
        else:
            body_html += "<b>ERROR:</b> Credit card number not valid<p>"
    elif "add_coffee" in args.keys():
        body_html = "<html><title>Adding menu item...</title><head><meta http-equiv='refresh' content='3; url=/'></head><body>"
        add_message = "Adding " + args["coffee"] + " to the menu, price: " + args["price"]
        db.Coffee.insert_one({'Name': args["coffee"], 'Price': int(args["price"]), 'Sold': 0})
        db.Billing.insert_one({'id': datetime.now(), 'message': add_message})
    else:
        body_html = ""
    for coffee in db.Coffee.find():
        # check if there is a delete request
        delete_coffee_string = coffee["Name"] + "_delete"
        if delete_coffee_string in args.keys():
            body_html = "<html><title>Removing menu item...</title><head><meta http-equiv='refresh' content='3; url=/'></head><body>"
            db.Coffee.delete_one({'Name': coffee["Name"]})
            db.Billing.insert_one({'id': datetime.now(), 'message': coffee["Name"] + " removed from the menu"})
        if coffee["Sold"] > 0:
            body_html += str(coffee)
    return body_html


@coffee_app.errorhandler(404)
def page_not_found(error):
    '''Landing page for 404 errors. Redirects to home page in 5 seconds.
    If you want to change this, replace content='5' with your number,
    or remove the <meta> tag to remove the redirect
    '''
    body_html = "<html><title>Not found</title><head><meta http-equiv='refresh' content='5; url=/'></head><body> \
                <h1>Yuriy's Coffee Shop</h1><p><p>\
                    Page not found, refreshing in 5 seconds...</body></html>"
    return body_html, 404


@coffee_app.errorhandler(500)  # handle all errors except 404
def internal_server_error(error):
    '''"500 Internal Server Error" error handler function
    This function prints an error and redirects to home page in 5 seconds
    If you want to change this, replace content='5' with your number,
    or remove the <meta> tag to remove the redirect
    The 500 error is generated when there is no API connection or wrong user input'''
    body_html = "<html><title>Error 500</title><head><meta http-equiv='refresh' content='5; url=/'></head><body> \
                <h1>Yuriy's Coffee Shop</h1><p><p>\
                    Server error, refreshing in 5 seconds...</body></html>"
    return body_html, 500


if __name__ == '__main__':
    coffee_app.run()
