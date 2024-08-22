import pyxdf
import snirf
from utils import *
from xdf_formatter import LumoxdfToStandardxdf
import os


streams, file_header = pyxdf.load_xdf("sub-P001_ses-S001_task-Default_run-001_eeg.xdf")
conf = snirf.SnirfConfig()







class XdfToSnirfMeasurmentListElement():

    def __init__(self, xdf_channel, probe: snirf.Probe):
        self.xdf_channel = xdf_channel
        self.snirf_probe = probe
        self.measurmentListElement = snirf.MeasurementListElement('', conf)
        self.populate_measurment_list_element()

    def PopulateSourceIndex(self):
        self.measurmentListElement.sourceIndex =  get_index(self.snirf_probe.sourceLabels, get(self.xdf_channel, "source")) + 1

    def PopulateDetectorIndex(self):
            self.measurmentListElement.detectorIndex =  get_index(self.snirf_probe.detectorLabels, get(self.xdf_channel, "detector")) + 1

    def PopulateWavelengthIndex(self):
            self.measurmentListElement.wavelengthIndex = get_index(self.snirf_probe.wavelengths, get(self.xdf_channel, "wavelen")) + 1

    def PopulateWavelegnthActual(self):
        self.measurmentListElement.wavelengthActual = get(self.xdf_channel, "wavelen_measured")
        
    def PopulateWavelengthEmissionActual(self):
        self.measurmentListElement.wavelengthEmissionActual = get(self.xdf_channel, "fluorescence.wavelen_measured")

    def PopulateDataType(self):
        self.measurmentListElement.dataType =  Get_DataType(get(self.xdf_channel, "measure"))

    def PopulateDataUnit(self):
        self.measurmentListElement.dataUnit = get(self.xdf_channel, "unit")

    
    def PopulateDataTypeLabel(self):
        self.measurmentListElement.dataTypeLabel = get(self.xdf_channel, "type")

    
    def PopulateDataTypeIndex(self):
        if Is_DCS(self.measurmentListElement.dataType):
            self.measurmentListElement.dataTypeIndex = get_index(self.snirf_probe.correlationTimeDelays,  get(self.xdf_channel, "dcs.delay")) + 1
        elif Is_Frequency_Domain(self.measurmentListElement.dataType):
            self.measurmentListElement.dataTypeIndex = get_index(self.snirf_probe.frequencies, get(self.xdf_channel, "fd.frequency")) + 1
        elif Is_Gated_Time_Domain(self.measurmentListElement.dataType) or Is_Gated_Time_Domain(self.measurmentListElement.dataType):
            self.measurmentListElement.dataTypeIndex = get_index(self.snirf_probe.timeDelays, get(self.xdf_channel, "td.delay")) + 1
        else:
            self.measurmentListElement.dataTypeIndex = 1 


    def PopulateSourcePower(self):
        self.measurmentListElement.sourcePower = get(self.xdf_channel, "power")

    def PopulateDetectorGain(self):
        self.measurmentListElement.detectorGain = get(self.xdf_channel, "gain")

    def populate_measurment_list_element(self):
        self.PopulateSourceIndex()
        self.PopulateDetectorIndex()
        self.PopulateWavelengthIndex()
        self.PopulateWavelegnthActual()
        self.PopulateWavelengthEmissionActual()
        self.PopulateDataType()
        self.PopulateDataUnit()
        self.PopulateDataTypeLabel()
        self.PopulateDataTypeIndex()
        self.PopulateSourcePower()
        self.PopulateDetectorGain()


class XdfToSnirfProbe():
    def __init__(self, xdf_fnirs_stream):
        self.xdf_channels = get(xdf_fnirs_stream, "info.desc.channels.channel")
        self.xdf_optodes = get(xdf_fnirs_stream, "info.desc.optodes.optode")
        self.xdf_source_optodes = []
        self.xdf_detector_optodes = []
        self.xdf_fiducials = get(xdf_fnirs_stream, "info.desc.fiducials.fiducial")
        self.probe = snirf.Probe("", conf)
        self.SeperateXdfOptodes()
        self.PopulateProbe()


    def PopulateProbe(self):
        self.PopulateWaveLegnths()
        self.PopulateSourcePos()
        self.PopulateDetectorPos()
        self.PopulateFrequencies()
        self.PopulateTimeDelays()
        self.PopulateCorrelationTimeDelays()
        self.PopulateSourceLabels()
        self.PopulateDetectorLabels()
        self.PopulateLandmarkLabels()
        self.PopulateLandmarkPos()

    
    def PopulateLandmarkLabels(self):
        labels = set()
        for fiducial in self.xdf_fiducials:
            try_add(labels, get(fiducial, "label"), "None")
        if labels:
            self.probe.landmarkLabels = list(labels)

    def PopulateLandmarkPos2D(self):
        position = []
        for fiducial in self.xdf_fiducials:
            l = [get(fiducial, "location.X"), get(fiducial,"location.Y")]
            if self.probe.landmarkLabels:
                try_append(l , get_index(self.probe.landmarkLabels, get(fiducial, "label")) + 1)
            try_append(position, l, all=True)
        self.probe.landmarkPos2D = position

    def PopulateLandmarkPos3D(self):
        position = []
        for fiducial in self.xdf_fiducials:
            l = [get(fiducial, "location.X"), get(fiducial, "location.Y"), get(fiducial, "location.Z")]
            if self.probe.landmarkLabels:
                try_append(l , get_index(self.probe.landmarkLabels, get(fiducial, "label")) + 1)
            try_append(position, l, all=True)
        self.probe.landmarkPos3D = position

    def PopulateLandmarkPos(self):
        self.probe.landmarkPos3D = []
        self.probe.landmarkPos2D = []
        for fiducial in self.xdf_fiducials:
            X = get(fiducial, "location.X")
            Y = get(fiducial, "location.Y")
            Z = get(fiducial, "location.Z")
            label = get(fiducial, "label")
            label_index = None
            if label:
                label_index = get_index(self.probe.landmarkLabels, label) + 1
            l = [X, Y]
            if Z:
                try_append(l, Z)
                try_append(l, label_index)
                self.probe.landmarkPos3D.append(l)
            else:
                try_append(l, label_index)
                self.probe.landmarkPos2D.append(l)


    def PopulateSourcePos2D(self):
        postions = []
        for optode in self.xdf_source_optodes:
            try_append(postions, [get(optode, "location.X"), get(optode, "location.Y")], all=True)
        self.probe.sourcePos2D = postions

    def PopulateDetectorPos2D(self):
        postions = []
        for optode in self.xdf_detector_optodes:
            try_append(postions, [get(optode, "location.X"), get(optode, "location.Y")], all=True)
        self.probe.detectorPos2D = postions

    def PopulateSourcePos3D(self):
        postions = []
        for optode in self.xdf_source_optodes:
            try_append(postions, [get(optode, "location.X"), get(optode, "location.Y"), get(optode, "location.Z")], all=True)
        self.probe.sourcePos3D = postions

    def PopulateSourcePos(self):
        self.probe.sourcePos3D = []
        self.probe.sourcePos2D = []
        for fiducial in self.xdf_detector_optodes:
            X = get(fiducial, "location.X")
            Y = get(fiducial, "location.Y")
            Z = get(fiducial, "location.Z")
            l = [X, Y]
            if Z:
                l.append(Z)
                self.probe.sourcePos3D.append(l)
            else:
                self.probe.sourcePos2D.append(l)

    def PopulateDetectorPos3D(self):
        postions = []
        for optode in self.xdf_detector_optodes:
            try_append(postions, [get(optode, "location.X"), get(optode, "location.Y"), get(optode, "location.Z")], all=True)
        self.probe.detectorPos3D = postions

    def PopulateDetectorPos(self):
        self.probe.detectorPos3D = []
        self.probe.detectorPos2D = []
        for fiducial in self.xdf_detector_optodes:
            X = get(fiducial, "location.X")
            Y = get(fiducial, "location.Y")
            Z = get(fiducial, "location.Z")
            l = [X, Y]
            if Z:
                l.append(Z)
                self.probe.detectorPos3D.append(l)
            else:
                self.probe.detectorPos2D.append(l)
        
    def PopulateSourceLabels(self):
        labels = []
        for source in self.xdf_source_optodes:
            try_append(labels, get(source, "label"))
        self.probe.sourceLabels = labels

    def PopulateDetectorLabels(self):
        labels = []
        for detector in self.xdf_detector_optodes:
            try_append(labels, get(detector, "label"))
        self.probe.detectorLabels = labels   

    def SeperateXdfOptodes(self):
        for optode in self.xdf_optodes:
            if get(optode, "function") in  ["Source", "source"]:
                self.xdf_source_optodes.append(optode)
            if get(optode, "function") in ["Detector", "detector"]:
                self.xdf_detector_optodes.append(optode)

    def PopulateWaveLegnths(self): #assume one to one mapping # assume either no wavelengthsEmission or wavelengthsEmission for each channel

        s = set()
        for channel in self.xdf_channels:
            wavelen = get(channel, "wavelen")
            fluorescence_wavelen = get(channel, "fluorescence.wavelen")
            s.add((wavelen, fluorescence_wavelen))

        wavelengths = []
        wavelengthsEmissions = []
        for wavelength, wavelengthsEmission in s:
            try_append(wavelengths, wavelength)
            try_append(wavelengthsEmissions, wavelengthsEmission, 0)

        self.probe.wavelengths = wavelengths
        self.probe.wavelengthsEmission = wavelengthsEmissions
    
    def PopulateCorrelationTimeDelays(self):
        delays = set()
        widths = set()
        for channel in self.xdf_channels:
            data_type = Get_DataType(get(channel, "measure"))
            if  Is_DCS(data_type):
                try_add(delays, convert("ps", "s", get(channel, "dsc.delay")))
                try_add(widths, convert("ps", "s", get(channel, "dcs.width")))

        self.probe.correlationTimeDelays = list(delays)
        self.probe.correlationTimeDelayWidths = list(widths)
           
    def PopulateTimeDelays(self):
        delays = set()
        widths = set()
        orders = set()

        for channel in self.xdf_channels:
            data_type = Get_DataType(get(channel, "measure"))
            if  Is_Gated_Time_Domain(data_type) or Is_Moment_Time_Domain(data_type):
                try_add(delays, convert("ps", "s" ,get(channel, "td.delay")))
                try_add(widths, convert("ps", "s" ,get(channel, "td.width")))
                try_add(orders, get(channel,"td.order")) #need to look into this
        
        self.probe.timeDelays = list(delays)
        self.probe.timeDelayWidths = list(widths)
        self.probe.momentOrders = list(orders)
            
        
    def PopulateFrequencies(self):
        frequencies = []
        for channel in self.xdf_channels:
            data_type = Get_DataType(get(channel, "measure"))
            if Is_Frequency_Domain(data_type):
                try_append(frequencies, get(channel, "fd.frequencies"))
        self.probe.frequencies = frequencies


class XdfToSnirfMeasurmentList():
    def __init__(self, xdf_fnirs_stream, snirf_file, probe: snirf.Probe):
        self.measurementList = snirf.MeasurementList(snirf_file, conf)
        for i,channel in enumerate(get(xdf_fnirs_stream, "info.desc.channels.channel")):
            self.measurementList.append(XdfToSnirfMeasurmentListElement(channel, probe).measurmentListElement)
            if i == 999:
                break



class XdfToSnirfAuxElement():
    def __init__(self, xdf_aux_stream) -> None:
        self.auxElement = snirf.AuxElement("", conf)
        self.auxElement.time = get(xdf_aux_stream, "time")
        self.auxElement.dataTimeSeries = get(xdf_aux_stream, "time_series")
        self.auxElement.name = get(xdf_aux_stream, "info.name")



class XdfToSnirfAux():
    def __init__(self, xdf_aux_streams) -> None:
        self.aux = snirf.Aux("", conf)
        for aux_stream in xdf_aux_streams:
            self.aux.append(XdfToSnirfAuxElement(aux_stream).auxElement)


class XdfToSnirfDataElement():
    def __init__(self, xdf_fnirs_stream, snirf_file, probe: snirf.Probe):
        self.dataElement = snirf.DataElement("", conf)
        self.dataElement.time = get(xdf_fnirs_stream, "time_stamps")[:1000]
        self.dataElement.dataTimeSeries = get(xdf_fnirs_stream, "time_series")[:,:1000]
        self.dataElement.measurementList = XdfToSnirfMeasurmentList(xdf_fnirs_stream, snirf_file, probe).measurementList



class XdfToSnirfData():
    def __init__(self, probe: snirf.Probe, xdf_fnirs_stream, snirf_file):
        snirf_data_elemtent =  XdfToSnirfDataElement(xdf_fnirs_stream, snirf_file, probe)
        self.data = snirf.Data(snirf_file, conf)
        self.data.append(snirf_data_elemtent.dataElement)


class XdfToSnirfNirsElement():
    def __init__(self, xdf_streams, snirf_file):
        xdf_fnirs_stream = None
        xdf_aux_streams = []
        for stream in xdf_streams:
            if get(stream, "info.type") == "NIRS":
                if get(stream, "info.name") == 'LUMO HA00030/GA00324':
                    stream = LumoxdfToStandardxdf(stream).stream
                xdf_fnirs_stream = stream #assume only one nirs stream peer snirf
            else:
                xdf_aux_streams.append(stream)

        self.NirsElement = snirf.NirsElement("" , conf)


        for xdf_aux_stream in xdf_aux_streams:
            self.NirsElement.aux = XdfToSnirfAux(xdf_aux_stream).aux

        self.NirsElement.metaDataTags.FrequencyUnit = "Hz"
        self.NirsElement.metaDataTags.TimeUnit = "s"
        self.NirsElement.metaDataTags.LengthUnit = "mm"
        self.NirsElement.metaDataTags.add("PowerUnit", "mW")
        self.NirsElement.metaDataTags.MeasurementDate = "2024-08-21"
        self.NirsElement.metaDataTags.MeasurementTime = "00:00:00"
        self.NirsElement.metaDataTags.SubjectID = "Jeremiah"
        self.NirsElement.probe = XdfToSnirfProbe(xdf_fnirs_stream).probe
        self.NirsElement.data = XdfToSnirfData(self.NirsElement.probe, xdf_fnirs_stream, snirf_file).data


class XdfToSnirfNirs():
    def __init__(self, xdf_streams, snirf_file): #how do we map aux xdf data stream to nirs stream? for now assume only 1 nirs stream
        self.nirs = snirf.Nirs(snirf_file, conf) 
        self.nirs.append(XdfToSnirfNirsElement(xdf_streams, snirf_file).NirsElement)





class XdfToSnirf():
    def __init__(self, path_to_snirf, path_to_xdf, validate) -> None:
        self.snirf = snirf.Snirf(path_to_snirf)
        self.snirf.formatVersion = 1.0
        xdf_streams, file_header = pyxdf.load_xdf(path_to_xdf)
        self.snirf.nirs = XdfToSnirfNirs(xdf_streams, self.snirf).nirs
        self.snirf.save(path_to_snirf)
        if validate:
            print("validating ", path_to_snirf)
            self.result = snirf.validateSnirf(path_to_snirf)


path_to_xdf = "sub-P001_ses-S001_task-Default_run-001_eeg.xdf"
path_to_snirf = "./converted.snirf"
conf = snirf.SnirfConfig()

os.remove(path_to_snirf) #need to remove
converted_snirf = XdfToSnirf(path_to_snirf, path_to_xdf, False)
pass



import snirf
from mne.io import read_raw_snirf

snirf_intensity = read_raw_snirf("converted.snirf")
snirf_intensity.plot(n_channels=64, duration=30000, show_scrollbars=False)
