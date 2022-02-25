from time import process_time_ns
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
import probeinterface as pi
import json

#spikeinterface imports
import spikeinterface as si 
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss

app = Flask(__name__) #boilerplate
CORS(app)
api = Api(app)

processing_pipeline = []

recording_file = 'cambridge_data.bin'
num_channels = 64
sampling_frequency = 20000
gain_to_uV = 0.195
offset_to_uV = 0
dtype="int16"
time_axis = 1
recording = si.read_binary(recording_file, num_chan=num_channels, sampling_frequency=sampling_frequency,
                           dtype=dtype, gain_to_uV=gain_to_uV, offset_to_uV=offset_to_uV, 
                           time_axis=time_axis)
processing_pipeline.append(recording)

class RunPipeline(Resource):
  def post(self):
    pipeline = request.get_json()
    i=0
    for oneStep in pipeline:
      if(oneStep["category"] == "preprocessing"):
        if(oneStep["nameOfStep"] == "Bandpass filter"):
          rec = st.bandpass_filter(processing_pipeline[i], int(oneStep["freq_min"]), int(oneStep["freq_max"]), int(oneStep["margin_ms"]), None if oneStep["dType"]=="None" else oneStep["dType"])
          processing_pipeline.append(rec)
          i+=1
          print('bandpass')
        elif(oneStep["nameOfStep"] == "Scale"):
          print("Scaling")
      elif(oneStep["category"] == "spikesorting"): 
        if(oneStep["nameOfStep"] == "Herdingspikes2"):
          print("Spikesorting")
          params = ss.get_default_params('herdingspikes')
          print(params)
          rec = ss.run_herdingspikes(processing_pipeline[i], output_folder='results_HS', 
                                  filter=False, verbose=True)                 
api.add_resource(RunPipeline, '/run')

#boilerplate 
if __name__ == "__main__":
    app.run(debug=True)