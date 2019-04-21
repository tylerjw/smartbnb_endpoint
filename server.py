from flask import Flask, request
import json
import datetime, time

app = Flask(__name__)

@app.route('/smartbnb',methods=['POST'])
def smarbnb():
  data = json.loads(request.data.decode(), parse_float=float)
  timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
  with open('data/{}.json'.format(timestamp), 'w') as outfile:
    json.dump(data, outfile)
  return "OK"

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=9004)