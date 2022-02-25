# # from time import process_time_ns
# from flask import Flask, jsonify, request
# from flask_restful import Resource, Api
# from flask_cors import CORS
# import probeinterface as pi
# import spikeinterface as si
# import spikeinterface.toolkit as st

# #spikeinterface imports
# app = Flask(__name__) #boilerplate
# CORS(app)
# api = Api(app)


# processing_pipeline = []

# recording_file = 'cambridge_data.bin'
# num_channels = 64
# sampling_frequency = 20000
# gain_to_uV = 0.195
# offset_to_uV = 0
# dtype="int16"
# time_axis = 1
# recording = si.read_binary(recording_file, num_chan=num_channels, sampling_frequency=sampling_frequency,
#                            dtype=dtype, gain_to_uV=gain_to_uV, offset_to_uV=offset_to_uV, 
#                            time_axis=time_axis)

# processing_pipeline.append(recording)

# class RunPipeline(Resource):
#   def post(self):
#     pipeline = request.get_json()
#     print(pipeline)
#     print(pipeline[0]["nameOfStep"])
#     for oneStep in pipeline:
#       i = 0
#       if(oneStep["category"] == "preprocessing"):
#         if(oneStep["nameOfStep"] == "Bandpass filter"):
#           rec = st.bandpass_filter(processing_pipeline[i], oneStep["freq_min"], oneStep["freq_max"], oneStep["margin_ms"], oneStep["dType"])
#           pipeline.append(rec)
#           i+=1
#           print('--------------------------')
#           print(rec)
#           print("bandpass worked")
#       elif(oneStep["category"] == "spikesorting"): 
#         print("It is spikesorting")
#     return "hello"
  
#   def get(self):
#     print("get")

# api.add_resource(RunPipeline, '/run')

# #boilerplate 
# if __name__ == "__main__":
#     app.run(debug=True)



from time import process_time_ns
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
import probeinterface as pi
import json

#spikeinterface imports
import spikeinterface as si 

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
    # print(pipeline)
    print(pipeline[0]["nameOfStep"])
    for oneStep in pipeline:
      if(oneStep["category"] == "preprocessing"):
        if(oneStep["nameOfStep"] == "Bandpass filter"):
          print("bandpass woot woot")
          print(processing_pipeline)
      elif(oneStep["category"] == "spikesorting"): 
        print("It is spikesorting")

api.add_resource(RunPipeline, '/run')

#boilerplate 
if __name__ == "__main__":
    app.run(debug=True)