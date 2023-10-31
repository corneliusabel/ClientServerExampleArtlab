import argparse
import random
import time
import requests

parser = argparse.ArgumentParser()
parser.add_argument('--id', dest='client_id', type=int, help='client id')
args = parser.parse_args()

# Get client id from args or generate random one
if args.client_id is None:
    clientID = random.randint(0, 100)
else:
    clientID= args.client_id

# Main loop
while 1:
    # do other stuff e.g. read sensors, lsl, etc.
    # ...

    # Send request to server
    try:
        r = requests.get(f'http://127.0.0.1:5000/talk?clientID={clientID}&status=running')
    except requests.exceptions.ConnectionError:
        print('ConnectionError')
    else:
        print(r.status_code)
        print(r.json())
        if r.json()['cmd'] == 'shutdown':
            print('shutdown')
            requests.get(f'http://127.0.0.1:5000/talk?clientID={clientID}&status=shutdown')
            break

    # wait 1 second
    time.sleep(0.5)

