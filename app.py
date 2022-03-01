import os
from pathlib import Path
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
import probeinterface as pi
import spikeinterface as si
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import probeinterface as pi
from probeinterface import plotting

import json

#spikeinterface imports
import spikeinterface as si 

app = Flask(__name__) #boilerplate
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
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

#spiketutorials - 12,13,18
#nwbextractor for new data set - no probe info required

#use a certain time period of data - 1st two seconds - nwb dataset 
#is large

#use quality metrics 
#
manufacturer = 'cambridgeneurotech'
probe_name = 'ASSY-156-P-1'

probe = pi.get_probe(manufacturer, probe_name)
recording_prb = recording.set_probe(probe, group_mode="by_shank")

processing_pipeline.append(recording_prb)


class RunPipeline(Resource):
  def post(self):
    pipeline = request.get_json()
    # print(pipeline)
    print(pipeline[0]["nameOfStep"])
    i = -1
    for oneStep in pipeline:
      if(oneStep["category"] == "preprocessing"):
        if(oneStep["nameOfStep"] == "Bandpass filter"):
          r = st.bandpass_filter(processing_pipeline[i], float(oneStep["freq_min"]), float(oneStep["freq_max"]), int(oneStep["margin_ms"]), None if oneStep["dType"]=="None" else  oneStep["dType"])
          processing_pipeline.append(r)
          i+=1
          
        elif(oneStep["nameOfStep"] == "Scale"):
          r = st.scale(processing_pipeline[i], float(oneStep["gain"]), float(oneStep["offset"]))
          processing_pipeline.append(r)
          print(processing_pipeline)
          i+=1
        
      elif(oneStep["category"] == "spikesorting"): 
        if(oneStep["nameOfStep"] == "Herdingspikes2"):
          print("entered")
          study_path = Path('./')
          study_folder = study_path / 'output/'
          if not study_folder.is_dir():
            print('Setting up study folder:', study_folder)
            os.mkdir(study_folder)
          s = ss.run_sorter(oneStep["filename"], processing_pipeline[i], study_folder)
          processing_pipeline.append(s)
          i+=1
          print(processing_pipeline)
api.add_resource(RunPipeline, '/run')

#boilerplate 
if __name__ == "__main__":
    app.run(debug=True)