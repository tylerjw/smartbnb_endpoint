import json
import datetime
import time
import os
import re

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

## database objects ################################################

class Reservation(db.Model):
    # reservation table row
    id = db.Column(db.String(10), primary_key=True)
    phone = db.Column(db.String(20))
    name = db.Column(db.String(80))
    code = db.Column(db.String(4))
    status = db.Column(db.String(20))
    listing = db.Column(db.String(10))
    start_date = db.Column(db.DateTime())
    end_date = db.Column(db.DateTime())
    listing = db.Column(db.Integer())

    # construct a Reservation json data
    def __init__(self, data):
        super().__init__()
        self.id = data['code']
        self.phone = data['guest']['phone']
        self.name = data['guest']['first_name'] + ' ' + data['guest']['last_name']
        self.code = re.sub('[^0-9]', '', data['guest']['phone'])[-4:]
        self.start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        self.end_date = datetime.datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        self.status = data['status']
        self.listing = data['listing']['id']

    def to_dict(self):
        return dict(id=self.id,
                    phone=self.phone,
                    name=self.name,
                    code=self.code,
                    start_date=self.start_date.strftime('%Y-%m-%d'),
                    end_date=self.end_date.strftime('%Y-%m-%d'),
                    status=self.status,
                    listing=self.listing)

## flask routes ################################################
@app.route('/smartbnb', methods=['POST'])
def smarbnb():
    # parse the json payload
    data = json.loads(request.data.decode(), parse_float=float)

    # write the file for later processing
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
    with open('data/{}.json'.format(timestamp), 'w') as outfile:
        json.dump(data, outfile)

    # update the database with this new data
    upsert(data)

    #prune old values from database
    today = datetime.date.today().strftime("%Y-%m-%d")
    results = Reservation.query.filter(Reservation.end_date < today).all()
    for row in results:
        db.session.delete(row)
        db.session.commit()

    #let the caller know this worked
    return "OK"

@app.route('/listing/<listing_id>', methods=['GET'])
def listing(listing_id):
    rows = Reservation.query.filter(Reservation.listing == listing_id)
    return json.dumps([r.to_dict() for r in rows])

@app.route('/today/<listing_id>', methods=['GET'])
def today(listing_id):
    today_date = datetime.date.today()
    rows = Reservation.query.filter(
        Reservation.listing == listing_id,
        Reservation.start_date <= today_date,
        Reservation.end_date >= today_date)
    return json.dumps([r.to_dict() for r in rows])

## helper functions #############################################
def upsert(data):
    # create the new row object
    new_row = Reservation(data)
    # test to see if we should delete or add
    if data['status'] == 'cancelled':
        db.session.delete(new_row)
    else:
        existing = Reservation.query.get(new_row.id)
        if existing:
            # update
            existing = new_row
        else:
            # insert
            db.session.add(new_row)
    #commit the change
    db.session.commit()

# loads the files into the database
def load_files():
    # import the files in order of modification time
    files = [os.path.join('data', f) for f in os.listdir('data')]
    files.sort(key=os.path.getmtime)

    for filename in files:
        with open(filename, 'r') as file:
            data = json.loads(file.read())
            upsert(data)

## main ############################################################
if __name__ == '__main__':
    # create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # create the database
    db.create_all()

    # load the files
    load_files()

    # start the server
    app.run(host='0.0.0.0', port=9004)
