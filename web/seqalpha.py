#!/usr/bin/env python
from flask import Flask, redirect, url_for, render_template, flash, request, session, abort, jsonify, Response
from werkzeug.utils import secure_filename
import os
import pickle
import genomedb
import glob
import runner, runnable

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    DATA_PATH='data',
    UPLOAD_FOLDER = 'data',
    HOST='0.0.0.0',
    PORT=5000
))

ALLOWED_EXTENSIONS = set(['fasta', 'gff', 'gz'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

''' Jinja2 extensions '''
@app.context_processor
def utility_processor():
    def basename(path):
        return os.path.basename(path)
    return dict(basename = basename)

g_searches = {}
g_runner = runner.Runner()
g_datadb = genomedb.GenomeDB(app.config['DATA_PATH'])


def search_filename(uuid):
    ''' Assume uuid is safe as it was found in the g_searches map. '''
    return '%s/%s.pkl' % (runnable.RESULT_PATH, uuid)

def find_task(uuid):
    for search in g_searches.values():
        for task in search.task_list:
            if task.uid == uuid:
                return task
    return None

def remove_task(uuid):
    for search in g_searches.values():
        for task in search.task_list:
            if task.uid == uuid:
                # @todo Some destructor to remove data as well
                search.task_list.remove(task)
                if search.task_list == 0:
                    del g_searches[search.uid]
                return True
    return False

def make_search_persistent(uuid):
    if uuid in g_searches:
        search = g_searches[uuid]
        search.persistent = True
        pickle.dump(search, open(search_filename(uuid), 'wb'))

def make_search_volatile(uuid):
    if uuid in g_searches:
        search = g_searches.pop(uuid, None)
        os.remove(search_filename(uuid))

def load_persistent():
    for pkl in glob.glob(runnable.RESULT_PATH + '/*.pkl'):
        search = pickle.load(open(pkl, 'rb'))
        if len(search.task_list) > 0:
            g_searches[search.uid] = search

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route("/")
def index():
    if 'search_id' in session:
        if session['search_id'] in g_searches:
            return redirect(url_for('search', search_id = session['search_id']))
    return render_template('query.html', datasets = g_datadb.list(), runnables = g_runner.info_list())

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return index()
    abort(404)

@app.route("/examples")
def examples():
    return render_template('examples.html', datasets = g_datadb.list(), runnables = g_runner.info_list())

@app.route("/saved")
def saved():
    return render_template('saved.html', searches = filter(lambda k: k.persistent, g_searches.values()), \
                           datasets = g_datadb.list(), runnables = g_runner.info_list())

@app.route('/query', methods=['POST'])
def query():
    # Decide if refining current search
    dataset = None
    if 'dataset' in request.form:
        dataset = request.form['dataset']
    elif 'uuid' in request.form:
        task = find_task(request.form['uuid'])
        if task is None:
            abort(404)
        dataset = task.data_out
    else:
        abort(404)

    # Run a new task
    task = g_runner.run(request.form['runner'], dataset, request.form)

    # Start a new session if not exists
    if ('search_id' not in session) or (session['search_id'] not in g_searches):
        session['search_id'] = task.uid
        g_searches[task.uid] = runnable.Search(task.uid)

    g_searches[ session['search_id'] ].task_list.insert(0, task)
    return redirect(url_for('search', search_id = session['search_id']))

@app.route('/reset')
def reset():
    if 'search_id' in session:
        uuid = session['search_id']
        if uuid in g_searches:
            if not g_searches[uuid].persistent:
                g_searches.pop(uuid, None)
    session.clear()
    return redirect(url_for('index'))

@app.route('/search/<search_id>')
def search(search_id):
    if not search_id in g_searches:
        abort(404)
    else:
        session['search_id'] = search_id
    return render_template('search.html', search = g_searches[search_id], datasets = g_datadb.list(), runnables = g_runner.info_list())

@app.route('/_result')
def _result():
    uuid = request.args.get('uuid', '', type=str)
    task = find_task(uuid)
    if not task:
        abort(404)
    return jsonify(task = task.pickle())

@app.route('/_remove')
def _remove():
    uuid = request.args.get('uuid', '', type=str)
    task_removed = remove_task(uuid)
    if not task_removed:
        abort(404)
    return jsonify(result = True)

@app.route('/_persist')
def _persist():
    uuid = request.args.get('uuid', '', type=str)
    state = request.args.get('state', 1, type=int)
    if state:
        make_search_persistent(uuid)
    else:
        make_search_volatile(uuid)
    return jsonify(result = True)

@app.route('/_call')
def _call():
    runner = request.args.get('runner', '', type=str)
    method = request.args.get('method', '', type=str)
    param  = request.args.getlist('param[]')
    param  = [str(item) for item in param]

    # Fetch a runnable instance
    runnable = g_runner.runnable(runner)
    callable = getattr(runnable, method)
    if not callable:
        abort(404)
    # Execute and return
    result = callable(param)
    return jsonify(result = result)

@app.route('/result/<uuid>')
def result(uuid):
    task = find_task(uuid)
    if not task:
        abort(404)
    return render_template('result.html', task = task)

@app.route('/getfile/<uuid>/<inout>')
def getfile(uuid, inout):
    task = find_task(uuid)
    if not task:
        abort(404)
    file_name = task.data_in 
    if 'out' in inout:
        file_name = task.data_out
    file_object = open(file_name)
    def generate():
        yield file_object.read(4096)
    return Response(generate(), mimetype='text/plain')

if __name__ == "__main__":

    # Load pickled searches
    load_persistent()

    # Run app
    app.run(host = app.config['HOST'], port = app.config['PORT'])
