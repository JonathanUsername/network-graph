import json
import os

from flask import Flask, render_template, request

from data import DIR
from process import reload_graph

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route("/")
def index():
    data = {}
    with open("my.json", "r") as f:
        data = {"chart_data": f.read()}
    return render_template("index.html", data=data)

@app.route('/upload_edges', methods = ['POST'])
def upload_edges():
    f = request.files['edges']
    f.save(os.path.join(DIR, 'uploads', 'edges.csv'))
    reload_graph()
    return 'file uploaded successfully'

@app.route('/upload_nodes', methods = ['POST'])
def upload_nodes():
    f = request.files['nodes']
    f.save(os.path.join(DIR, 'uploads', 'nodes.csv'))
    reload_graph()
    return 'file uploaded successfully'

@app.route('/upload_frequencies', methods = ['POST'])
def upload_frequencies():
    f = request.files['frequencies']
    f.save(os.path.join(DIR, 'uploads', 'frequencies.csv'))
    reload_graph()
    return 'file uploaded successfully'

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
