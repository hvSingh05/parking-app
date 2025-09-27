# vehicle-parking-app-v1
this is a course project about a 4-wheeler vehicle parking app.

the app.py is the main file where the app is defined.

the /templates directory contains the templates which are rendered to display the webpages.

in the application directory we have two python files:
    application/controllers.py
    application/models.py

the controllers.py file contains the app routes/controlles where the logic of the app is defined.

the models.py contains database models that are defined using sqlalchemy.

the models.py contains the following models:
    Admin(id(pk), name, username, phone nummber, password),
    User(id(pk), name, username, phone nummber, password),
    Lot(id(pk), location, address, pincode, max spots, price/hr),
    Spot(id(pk), spot number, lot id(fk), status, vehicle registration number),
    Reservation(id(pk), user id(fk), lot id(fk), spot id(fk), vehicle registration number, parking time, releasing time, total cost)

to execute the program, run app.py.

the app.py contains a function initialize_database() which creates the database tables and default admin, pushing app context to app.







