from flask import Flask, request
import json
import datetime, time
import os
import dataset
import re

app = Flask(__name__)

@app.route('/smartbnb',methods=['POST'])
def smarbnb():
  data = json.loads(request.data.decode(), parse_float=float)
  db = dataset.connect('sqlite:///database.db')
  table = db.get_table('reservations', 
    primary_id='id', primary_type=db.types.string(10))

  # write the file for later processing
  timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
  with open('data/{}.json'.format(timestamp), 'w') as outfile:
    json.dump(data, outfile)

  # put the new data in the database
  upsert(table, data)

  #prune old values from database
  today = datetime.date.today().strftime("%Y-%m-%d")
  results = table.find(end_date={"<":today})
  for row_id in [row['id'] for row in results]:
    table.delete(id=row_id)

  #let the caller know this worked
  return "OK"

@app.route('/listing/<listing_id>',methods=['GET'])
def listing(listing_id):
  db = dataset.connect('sqlite:///database.db')
  table = db.get_table('reservations', 
    primary_id='id', primary_type=db.types.string(10))
  results = table.find(listing=listing_id)
  rows = [row for row in results]
  return json.dumps(rows)

@app.route('/today/<listing_id>',methods=['GET'])
def today(listing_id):
  db = dataset.connect('sqlite:///database.db')
  table = db.get_table('reservations', 
    primary_id='id', primary_type=db.types.string(10))
  # today = datetime.date.today().strftime("%Y-%m-%d")
  today = '2019-06-25'
  results = table.find(
    listing=listing_id, 
    start_date={"<=":today},
    end_date={">=":today})
  rows = [row for row in results]
  return json.dumps(rows)

def upsert(table, data):
  row = {
    'id': data['code'],
    'phone': data['guest']['phone'],
    'name': data['guest']['first_name'] + ' ' + data['guest']['last_name'],
    'code': re.sub('[^0-9]','',data['guest']['phone'])[-4:],
    'start_date': data['start_date'],
    'end_date': data['end_date'],
    'status': data['status'],
    'listing': data['listing']['id'],
    'updated': datetime.datetime.utcnow().ctime()
  }
  
  if (row['status'] == 'cancelled'):
    table.delete(id=row['id'])
  else:
    table.upsert(row, ['id'])

# loads the files into the database
def load_files():
  db = dataset.connect('sqlite:///database.db')
  table = db.get_table('reservations', 
    primary_id='id', primary_type=db.types.string(10))

  # import the files in order of modification time
  files = [os.path.join('data', f) for f in os.listdir('data')]
  files.sort(key=lambda filename: os.path.getmtime(filename))

  for filename in files:
    with open(filename, 'r') as file:
      data = json.loads(file.read())
      upsert(table, data)
      

if __name__ == '__main__':
  # create data directory if it doesn't exist
  if not os.path.exists('data'):
    os.makedirs('data')

  # load the files
  load_files()

  # start the server
  app.run(host='0.0.0.0', port=9004)