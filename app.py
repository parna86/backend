from flask import Flask, jsonify, make_response, render_template, request
from flask import abort
from flask_restful import Resource, Api
from flask_cors import CORS
from pipeline import RunPipeline

import sys

import json

#spikeinterface imports
import spikeinterface as si 

app = Flask(__name__) #boilerplate
api = Api(app)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

          
api.add_resource(RunPipeline, '/run')

#boilerplate s
if __name__ == "__main__":
    app.run(debug=True)