import os
from pathlib import Path
from flask import Flask, jsonify, make_response, render_template, request
from flask import abort
from flask_restful import Resource, Api
from flask_cors import CORS
import probeinterface as pi
import spikeinterface as si
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import probeinterface as pi
from probeinterface import plotting
import sys

import json

#spikeinterface imports
import spikeinterface as si 

app = Flask(__name__) #boilerplate
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)

errors = {
    'UserAlreadyExistsError': {
        'message': "A user with that username already exists.",
        'status': 409,
    },
    'ResourceDoesNotExist': {
        'message': "A resource with that ID no longer exists.",
        'status': 410,
        'extra': "Any extra information you want.",
    },
}

processing_pipeline = []

# original_sysout = sys.stdout
# commandLineOutput = open('filename.txt', 'w')
# sys.stdout = commandLineOutput

available_datasets = ["cambridge_data.bin",
                      "sub-P29-16-05-14-retina02-left_ecephys.nwb"]

recording_file = "data/sub-P29-16-05-14-retina02-left_ecephys.nwb"
recording = si.extractors.NwbRecordingExtractor(recording_file)
recording_shorter = recording.frame_slice(0, 60000)

# recording_file = 'data/cambridge_data.bin'
# num_channels = 64
# sampling_frequency = 20000
# gain_to_uV = 0.195
# offset_to_uV = 0
# dtype="int16"
# time_axis = 1
# recording = si.read_binary(recording_file, num_chan=num_channels, sampling_frequency=sampling_frequency,
#                            dtype=dtype, gain_to_uV=gain_to_uV, offset_to_uV=offset_to_uV, 
#                            time_axis=time_axis)

# recording.annotate(is_filtered=False)
# manufacturer = 'cambridgeneurotech'
# probe_name = 'ASSY-156-P-1'

# probe = pi.get_probe(manufacturer, probe_name)
# probe.wiring_to_device('ASSY-156>RHD2164')
# recording_prb = recording.set_probe(probe, group_mode="by_shank")
# # brain_area_property_values = ['CA1']*32 + ['CA3']*32
# # recording_prb.set_property(key='brain_area', values=brain_area_property_values)
# # recording_prb.set_property(key='quality', values=["good"]*(recording_prb.get_num_channels() - 3),
# #                            ids=recording_prb.get_channel_ids()[:-3])

processing_pipeline.append(recording_shorter)

#spiketutorials - 12,13,18
#nwbextractor for new data set - no probe info required

#use a certain time period of data - 1st two seconds - nwb dataset 
#is large

#use quality metrics 
#


class RunPipeline(Resource):
  def get(self):
    return jsonify(available_datasets)

  def post(self):
    try:
      pipeline = request.get_json()
      print(pipeline[0])
    except IndexError:
      abort(300, "The pipeline has not been passed properly to the backend")
    i = -1
    for oneStep in pipeline:
      #add error handling from here with informative stack trace
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
          i+=1
          study_path = Path('./')
          study_folder = study_path / 'output/'
          if not study_folder.is_dir():
            print('Setting up study folder:', study_folder)
            os.mkdir(study_folder)
          # print("#############################we are HEREEEEEEEEEEEEEEEEEEEEEEEEE")
          s = ss.run_sorter(oneStep["filename"], processing_pipeline[i], study_folder)
          processing_pipeline.append(s)
          print(processing_pipeline)  
          #can add sorter information to a python dictionary and return that
          #and render that in the browse=
          return s.get_all_spike_trains()
    return  
          
api.add_resource(RunPipeline, '/run')

#boilerplate s
if __name__ == "__main__":
    app.run(debug=True)