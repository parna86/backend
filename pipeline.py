import os
import traceback
from numpy import record

from pathlib import Path
from flask import jsonify, request, send_file
from flask import abort
from flask_restful import Resource

from werkzeug.http import HTTP_STATUS_CODES

import probeinterface as pi
import spikeinterface as si
import spikeinterface.extractors as se
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import probeinterface as pi
from probeinterface import plotting

class RunPipeline(Resource):
  def __init__(self):
    self.processing_pipeline = []
    available_datasets = ["cambridge_data.bin",
                          "sub-P29-16-05-14-retina02-left_ecephys.nwb",
                          "biocam_hw3.0_fw1.6.brw",
                          "H19.29.141.11.21.01.nwb",
                          "mearec_test_10s.h5"
                          ]
  #cambridge - with probe interface 
  #nwb retina - herdingspikes 
  #biocam - not working - biocamextractor not found
  #h19.nwb - broken - ValueError: More than one acquisition found! You must specify 'electrical_series_name'.
  #mearec - elephant dependency not compatible on macos

    recording_file = "data/biocam_hw3.0_fw1.6.brw"
    recording = se.BiocamRecordingExtractor(recording_file)
    self.processing_pipeline.append(recording)
    # recording_file = "data/biocam_hw3.0_fw1.6.brw"
    # recording = se.BiocamRecordingExtractor(recording_file)
    # self.processing_pipeline.append(recording)

  #   recording_file = "data/H19.29.141.11.21.01.nwb"
  #   recording = si.extractors.NwbRecordingExtractor(recording_file)
  #   # recording_shorter = recording.frame_slice(0, 60000)
  #   self.processing_pipeline.append(recording)
  # #frame_slice recording throws error in sorter
  # #sorter params issue fixed - added non-positional arguments? 

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
          r = st.bandpass_filter(self.processing_pipeline[i], float(oneStep["params"]["freq_min"]), float(oneStep["params"]["freq_max"]), int(oneStep["params"]["margin_ms"]), None if oneStep["params"]["dType"]=="None" else  oneStep["params"]["dType"])
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
        filename = oneStep["params"]["filename"]
        oneStep["params"].pop("ref")
        oneStep["params"].pop("filename")
        print(oneStep["params"])
        try:
          s = ss.run_sorter(filename, self.processing_pipeline[i])
          print(s)
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
    return(str(self.processing_pipeline))