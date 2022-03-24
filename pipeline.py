import os
import traceback

from pathlib import Path
from flask import jsonify, request
from flask import abort
from flask_restful import Resource

from werkzeug.http import HTTP_STATUS_CODES

import probeinterface as pi
import spikeinterface as si
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import probeinterface as pi
from probeinterface import plotting

class RunPipeline(Resource):
  def __init__(self):
    self.processing_pipeline = []
    available_datasets = ["cambridge_data.bin",
                          "sub-P29-16-05-14-retina02-left_ecephys.nwb"]

    recording_file = "data/sub-P29-16-05-14-retina02-left_ecephys.nwb"
    recording = si.extractors.NwbRecordingExtractor(recording_file)
    recording_shorter = recording.frame_slice(0, 60000)
    self.processing_pipeline.append(recording_shorter)

  def post(self):
    try:
      pipeline = request.get_json()
    except IndexError:
      abort(400, "The pipeline has not been passed properly to the backend")
    i = 0
    for oneStep in pipeline:
      #add error handling from here with informative stack trace
      if(oneStep["category"] == "preprocessing"):
        if(oneStep["nameOfStep"] == "Bandpass filter"):
          r = st.bandpass_filter(self.processing_pipeline[i], float(oneStep["params"]["freq_min"]), float(oneStep["params"]["freq_max"]), int(oneStep["params"]["margin_ms"]), None if oneStep["params"]["dType"]=="None" else  oneStep["params"]["dType"], sorter_params=jsonify(oneStep["params"]))
          self.processing_pipeline.append(r)
          i+=1
          
        elif(oneStep["nameOfStep"] == "Scale"):
          r = st.scale(self.processing_pipeline[i], float(oneStep["params"]["gain"]), float(oneStep["params"]["offset"]))
          self.processing_pipeline.append(r)
          print(self.processing_pipeline)
          i+=1
        
      elif(oneStep["category"] == "spikesorting"):
        study_path = Path('./')
        study_folder = study_path / 'output/'
        if not study_folder.is_dir():
          print('Setting up study folder:', study_folder)
          os.mkdir(study_folder)
        print(self.processing_pipeline[i])
        print("Before running sorter")
        try:
          s = ss.run_sorter(oneStep["params"]["filename"], self.processing_pipeline[i], study_folder)
        except Exception as e: 
          print("Printing the exception")
          print("------")
          print(traceback.format_exc());
          print("------")
          print("----------")
          abort(400, "Spikesorter failed with an issue");
        i+=1
        self.processing_pipeline.append(s)
        return(jsonify(self.processing_pipeline[i-1])) 
    return