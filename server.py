import json
import datetime
import time
import os
import re
import sys

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from pprint import pprint
import traceback

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'smartbnb-endpoint.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
data_dir = 'data'

## database objects ################################################

class Reservation(db.Model):
    # reservation table row
    id = db.Column(db.String(10), primary_key=True)
    code = db.Column(db.String(4))
    start_date = db.Column(db.DateTime())
    end_date = db.Column(db.DateTime())
    status = db.Column(db.String(20))
    listing = db.Column(db.Integer())

    # construct a Reservation json data
    def __init__(self, data):
        super().__init__()
        try:
            self.id = data['code']
            if (data['guest']['phone'] != None):
                self.code = re.sub('[^0-9]', '', data['guest']['phone'])[-4:]
            else:
                self.code = ""
            self.start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            self.end_date = datetime.datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            self.status = data['status']
            self.listing = data['listing']['id']
        except Exception as e:
            print("Error processing data")
            pprint(data)
            traceback.print_exc()

    def to_dict(self):
        return dict(id=self.id,
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
    with open('{}/{}.json'.format(data_dir,timestamp), 'w') as outfile:
        json.dump(data, outfile)

    # update the database with this new data
    upsert(data)

    #let the caller know this worked
    return "OK"

@app.route('/listing/<listing_id>', methods=['GET'])
def listing(listing_id):
    rows = Reservation.query.filter(
        Reservation.listing == listing_id).order_by(
        Reservation.start_date)
    return json.dumps([r.to_dict() for r in rows])

@app.route('/today/<listing_id>', methods=['GET'])
def today(listing_id):
    today_date = datetime.date.today()
    rows = Reservation.query.filter(
        Reservation.listing == listing_id,
        Reservation.start_date <= today_date,
        Reservation.end_date >= today_date).order_by(
        Reservation.start_date)
    return json.dumps([r.to_dict() for r in rows])

@app.route('/code/<listing_id>/<date_time>', methods=['GET'])
def code(listing_id, date_time):
    test_date = datetime.datetime.strptime(date_time[:10],"%Y_%m_%d")
    now = datetime.datetime.strptime(date_time,"%Y_%m_%d_%H_%M")
    rows = Reservation.query.filter(
        Reservation.listing == listing_id,
        Reservation.start_date <= test_date,
        Reservation.end_date >= test_date).order_by(
        Reservation.start_date)
    rows = [r.to_dict() for r in rows]
    if len(rows) == 0:
        return 'NONE'
    elif len(rows) == 1:
        return json.dumps(rows[0])
    else:
        if now.hour < 13:
            return json.dumps(rows[0])
        else:
            return json.dumps(rows[1])

## helper functions #############################################
def upsert(data):
    # create the new row object
    new_row = Reservation(data)

    # test to see if we should delete or add
    if data['status'] == 'cancelled':
        new_row = Reservation.query.get(new_row.id)
        if new_row:
            pprint("Deleting reservation: {}".format(new_row.to_dict()))
            db.session.delete(new_row)
            db.session.commit()
    else:
        # replace if it exists
        existing = Reservation.query.get(new_row.id)
        if existing:
            # delete old one
            pprint("Updating reservation: {}".format(new_row.to_dict()))
            db.session.delete(existing)
            db.session.commit()
        # insert the new one
        pprint("Inserting reservation: {}".format(new_row.to_dict()))
        db.session.add(new_row)
        db.session.commit()

    #prune old values from database
    today = datetime.date.today().strftime("%Y-%m-%d")
    results = Reservation.query.filter(Reservation.end_date < today).all()
    for row in results:
        db.session.delete(row)
        db.session.commit()

# loads the files into the database
def load_files(data_dir):
    # import the files in order of modification time
    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
    files.sort(key=os.path.getmtime)

    for filename in files:
        with open(filename, 'r') as file:
            data = json.loads(file.read())
            upsert(data)

## main ############################################################
if __name__ == '__main__':
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]

    print('Using data dir: {}'.format(data_dir))

    # create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # create the database
    db.create_all()

    # load the files
    load_files(data_dir)

    # start the server
    app.run(host='0.0.0.0', port=9004)
