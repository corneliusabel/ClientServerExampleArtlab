from datetime import datetime

from flask import Flask, jsonify, render_template
from flask_caching import Cache
from flask import request
from http import HTTPStatus

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
cache = Cache(app, config=config)


@app.route('/talk', methods=['GET'])
def client_entry_point():
    clientTime= ''
    cmd = None
    clients = cache.get("clients")
    if clients is None:
        clients = {}

    clientID = request.args.get('clientID')
    status = request.args.get('status')

    if clientID not in clients:
        clients[clientID] = {'ID': clientID,
                             'status': status,
                             'cmd': None,
                             'timestamp': datetime.now(),
                             'last_request':0,}
    else:
        # Update status
        clients[clientID]['status'] = status

        # if shutdown remove client
        if status == 'shutdown':

            clients.pop(clientID)
        else:
            # Update timestamp
            clients[clientID]['timestamp'] = datetime.now()

            # Get command and reset it (so its only send once)
            cmd = clients[clientID]['cmd']
            clients[clientID]['cmd'] = None

    cache.set("clients", clients)
    d = {'code': 200, 'RequestTime': clientTime, 'cmd': cmd, }
    return jsonify(d)


# Endpoint to set shutdown command
@app.route('/<clientID>/shutdown', methods=['GET'])
def shutdown_client(clientID=None):
    clients = cache.get("clients")

    # Check if clientID is valid
    if clientID is None or clientID not in clients:
        return '', HTTPStatus.BAD_REQUEST

    # Set command to shutdown
    clients[clientID]['cmd'] = 'shutdown'
    cache.set("clients", clients)

    return '', HTTPStatus.NO_CONTENT


# Show dashboard clients
@app.route('/clients')
def clients():
    clients = cache.get("clients")
    clients_to_remove = []
    if clients:
        # calc last request time
        for id, client in clients.items():
            client['last_request'] = (datetime.now() - client['timestamp']).total_seconds()

            # remove client if last request was more than 10 seconds ago
            if client['last_request'] > 10:
                clients_to_remove.append(id)

        # remove clients
        for id in clients_to_remove:
            clients.pop(id)

    return render_template('clients.html',clients=clients)

# Show dashboard
@app.route('/')
def dashboard():
    clients = cache.get("clients")
    return render_template('dashboard.html',clients=clients)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)