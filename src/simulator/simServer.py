import os
import sys
from threading import Lock
from flask import Flask
from flask_socketio import SocketIO
from . import env

app = Flask(__name__)
socketio = SocketIO(app)

thread = None
thread_lock = Lock()

# Variables used to load the assets into the server directory
tmp_files = []
loaded_entry_point = ['']
sim_folder = os.path.dirname(os.path.realpath(__file__))


def background_thread():
    """Server generated events are broadcast to clients."""
    while True:
        socketio.sleep(0.1)
        if len(env.data_log) > 0:
            socketio.emit('sim_state',
                          {'data': env.data_log}, broadcast=True)
            env.data_log = []


@app.route('/')
def index():
    with open(os.path.join(sim_folder, 'static', loaded_entry_point[0]), 'r') as f:
        resp = f.read()

    return resp


@socketio.on('client_msg')
def handle_client_msg(msg):
    print('Message from client:', msg)


def init_dirs(dirs):
    for dir in dirs:
        d = os.path.join(sim_folder, 'static', dir)
        if not os.path.exists(d):
            os.mkdir(d)


def load_file(source, dest):
    _, filename = os.path.split(source)
    dest = os.path.join(sim_folder, dest, filename)
    tmp_files.append(dest)

    with open(source, 'rb') as f:
        res = f.read()

    with open(dest, 'wb') as f:
        f.write(res)

    return dest


def clean_up():
    for f in tmp_files:
        os.remove(f)


def start_server(dir, entry_point):
    # init_dirs(kwargs.keys())

    # loaded_entry_point[0] = load_file(entry_point, 'static')

    loaded_entry_point[0] = entry_point
    static_path = os.path.join(sim_folder, 'static')

    try:
        os.remove(static_path)
    except:
        pass

    os.symlink(os.path.realpath(dir), static_path)

    # for f in files:
    #     load_file(f, 'static')
    #
    # for dir in kwargs.keys():
    #     for f in kwargs[dir]:
    #         load_file(f, 'static/'+dir)

    try:
        global thread
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(target=background_thread)
        socketio.run(app, port=8000, debug=False)

    except KeyboardInterrupt:
        print('Server stopped. Cleaning up...')
        sys.exit(0)

    finally:
        pass
        #clean_up()


