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
                          "mearec_test_10s.h5"]
  #cambridge - with probe interface 
  #nwb retina - herdingspikes 
  #biocam - not working - biocamextractor not found
  #h19.nwb - broken - ValueError: More than one acquisition found! You must specify 'electrical_series_name'.
  #mearec - elephant dependency not compatible on macos
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
    output = {}
    try:
      pipeline = request.get_json()
    except IndexError:
      abort(400, "The pipeline has not been passed properly to the backend")
    i = 0
    for oneStep in pipeline:
      if("dataset" in oneStep):
        nameOfDataset = oneStep["dataset"]
        recording_file = "data/" + nameOfDataset
        fileNameSplit = nameOfDataset.rsplit('.', 1)
        fileFormat = fileNameSplit[len(fileNameSplit) - 1]
        if(fileFormat == 'brw'):
          try:
            recording = se.BiocamRecordingExtractor(recording_file)
            self.processing_pipeline.append(recording)
            listOfInformation = []
            listOfInformation.append({"Number of channels", recording.get_num_channels()})
            listOfInformation.append({"Channel locations", str(recording.get_channel_locations())})
            output["BioCamRecordingExtractor"] = listOfInformation
          except Exception as e:
            print(e)
            abort(400, "Error in parsing biocam format")
        elif(fileFormat == 'nwb'):
          try:
            recording = se.NwbRecordingExtractor(recording_file)
            recording_shorter = recording.frame_slice(0, 60000)
            self.processing_pipeline.append(recording_shorter)
          except Exception as e:
            print(e)
            abort(400, "Error in parsing nwb format")
        elif(fileFormat == 'h5'):
          try:
            recording = se.MEArecRecordingExtractor(recording_file)
            self.processing_pipeline.append(recording)
          except Exception as e:
            print(e)
            abort(400, "Error in parsing MEArc dataset")
        else:
          abort(400, "Data format not supported at the moment")        
      elif(oneStep["category"] == "preprocessing"):
        if(oneStep["nameOfStep"] == "Bandpass filter"):
          try:
            r = st.bandpass_filter(self.processing_pipeline[i], float(oneStep["params"]["freq_min"]), float(oneStep["params"]["freq_max"]), int(oneStep["params"]["margin_ms"]), None if oneStep["params"]["dType"]=="None" else  oneStep["params"]["dType"])
            self.processing_pipeline.append(r)
          except Exception as e:
            print(e)
            abort(400, "Error in running bandpass filter")
          i+=1   
        elif(oneStep["nameOfStep"] == "Scale"):
          try:
            r = st.scale(self.processing_pipeline[i], float(oneStep["params"]["gain"]), float(oneStep["params"]["offset"]))
            self.processing_pipeline.append(r)
            print(self.processing_pipeline)
          except Exception as e:
            print(e)
            abort(400, "Error in running scale preprocessor")
          i+=1
      elif(oneStep["category"] == "spikesorting"):
        study_path = Path('./')
        study_folder = study_path / 'output/'
        if not study_folder.is_dir():
          print('Setting up study folder:', study_folder)
          os.mkdir(study_folder)
        filename = oneStep["params"]["filename"]
        oneStep["params"].pop("filename")
        print(oneStep["params"])
        try:
          s = ss.run_sorter(filename, self.processing_pipeline[i])
          listOfInformation = []
          listOfInformation.append({"Number of units", s.get_num_units()})
          listOfInformation.append({"Sampling frequency", str(s.get_sampling_frequency())})
          output[filename] = listOfInformation
        except Exception as e: 
          print(traceback.format_exc());
          abort(400, "Spikesorter failed with an issue: \n".join(e));
        i+=1
        
        self.processing_pipeline.append(s)
    return(str(output))