import pyxdf
import snirf
from utils import *
from xdf_formatter import *
import os
from numpy.testing import assert_allclose
from mne.io import read_raw_snirf
import argparse
import shutil


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
        data_type_index = 0
        if Is_DCS(self.measurmentListElement.dataType):
            delay = convert("ps", "s", get(self.xdf_channel, "dcs.delay"))
            width = convert("ps", "s", get(self.xdf_channel, "dcs.width"))
            delay_indexes = {i for i, x in enumerate(self.snirf_probe.correlationTimeDelays) if x == delay}
            width_indexes = {i for i, x in enumerate(self.snirf_probe.correlationTimeDelayWidths) if x == width}
            data_type_index = delay_indexes.intersection(width_indexes).pop() + 1
        elif Is_Frequency_Domain(self.measurmentListElement.dataType):
            data_type_index = get_index(self.snirf_probe.frequencies, get(self.xdf_channel, "fd.frequency")) + 1
        elif Is_Moment_Time_Domain(self.measurmentListElement.dataType):
            data_type_index = get_index(self.snirf_probe.momentOrders, get(self.xdf_channel, "td.order")) + 1           
        elif Is_Gated_Time_Domain(self.measurmentListElement.dataType):
            delay = convert("ps", "s", get(self.xdf_channel, "td.delay"))
            width = convert("ps", "s", get(self.xdf_channel, "td.width"))
            delay_indexes = {i for i, x in enumerate(self.snirf_probe.timeDelays) if x == delay}
            width_indexes = {i for i, x in enumerate(self.snirf_probe.timeDelayWidths) if x == width}
            data_type_index = delay_indexes.intersection(width_indexes).pop() + 1
        self.measurmentListElement.dataTypeIndex = data_type_index


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
    def __init__(self, xdf_fnirs_channels, xdf_fnirs_optodes, xdf_fnirs_fiducials = []):
        self.xdf_channels = xdf_fnirs_channels
        self.xdf_optodes = xdf_fnirs_optodes
        self.xdf_source_optodes = []
        self.xdf_detector_optodes = []
        self.xdf_fiducials = xdf_fnirs_fiducials
        self.probe = snirf.Probe("", conf)
        self.SeperateXdfOptodes()
        self.PopulateProbe()


    def PopulateProbe(self):
        self.PopulateWaveLegnths()
        self.PopulateSourcePos()
        self.PopulateDetectorPos()
        self.PopulateFrequencies()
        self.PopulateGatedTimeDomain()
        self.PopulateMomentTimeDomain()
        self.PopulateCorrelationTimeDomain()
        self.PopulateSourceLabels()
        self.PopulateDetectorLabels()
        self.PopulateLandmarkLabels()
        self.PopulateLandmarkPos()

    
    def PopulateLandmarkLabels(self):
        labels = set()
        for fiducial in self.xdf_fiducials:
            try_add(labels, get(fiducial, "label"), "None")
        if labels:
            self.probe.landmarkLabels = sorted(list(labels))

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

    def PopulateSourcePos(self):
        self.probe.sourcePos3D = []
        self.probe.sourcePos2D = []
        for optode in self.xdf_source_optodes:
            X = get(optode, "location.X")
            Y = get(optode, "location.Y")
            Z = get(optode, "location.Z")
            l = [X, Y]
            if Z:
                l.append(Z)
                self.probe.sourcePos3D.append(l)
            else:
                self.probe.sourcePos2D.append(l)

    def PopulateDetectorPos(self):
        self.probe.detectorPos3D = []
        self.probe.detectorPos2D = []
        for optode in self.xdf_detector_optodes:
            X = get(optode, "location.X")
            Y = get(optode, "location.Y")
            Z = get(optode, "location.Z")
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

        self.probe.wavelengths = sorted(wavelengths)
        self.probe.wavelengthsEmission = sorted(wavelengthsEmissions)
    
    def PopulateCorrelationTimeDomain(self):
        dcs = set()
        for channel in self.xdf_channels:
            data_type = Get_DataType(get(channel, "measure"))
            if  Is_DCS(data_type):
                delay = convert("ps", "s", get(channel, "dcs.delay"))
                width = convert("ps", "s", get(channel, "dcs.width"))
                dcs.add((delay, width))

        delays = []
        widths = []
        for delay, width in dcs:
            delays.append(delay)
            widths.append(width)


        self.probe.correlationTimeDelays = delays
        self.probe.correlationTimeDelayWidths = widths
           
    def PopulateGatedTimeDomain(self):
        td = set()

        for channel in self.xdf_channels:
            data_type = Get_DataType(get(channel, "measure"))
            if  Is_Gated_Time_Domain(data_type):
                delay =  convert("ps", "s" ,get(channel, "td.delay"))
                width = convert("ps", "s" ,get(channel, "td.width"))
                td.add((delay, width))
        
        delays = []
        widths = []
        for delay, width in td:
            delays.append(delay)
            widths.append(width)

        self.probe.timeDelays = delays
        self.probe.timeDelayWidths = widths

    def PopulateMomentTimeDomain(self):
        td = set()

        for channel in self.xdf_channels:
            data_type = Get_DataType(get(channel, "measure"))
            if  Is_Moment_Time_Domain(data_type):
                order = get(channel,"td.order") #need to look into this
                td.add(order)
        
        orders = []
        for order in td:
            orders.append(order)

        self.probe.momentOrders = orders
            
        
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
        channels = get(xdf_fnirs_stream, "info.desc.channels.channel")
        for channel in channels:
            self.measurementList.append(XdfToSnirfMeasurmentListElement(channel, probe).measurmentListElement)



class XdfToSnirfAuxElement():
    def __init__(self, xdf_aux_stream) -> None:
        self.auxElement = snirf.AuxElement("", conf)
        self.auxElement.time = get(xdf_aux_stream, "time")
        xdf_time_Stamps = get(xdf_aux_stream, "time_stamps")
        self.auxElement.time = numpy.array(xdf_time_Stamps) - xdf_time_Stamps[0]
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
        xdf_time_Stamps = get(xdf_fnirs_stream, "time_stamps")
        self.dataElement.time = numpy.array(xdf_time_Stamps) - xdf_time_Stamps[0]
        self.dataElement.dataTimeSeries = get(xdf_fnirs_stream, "time_series")
        self.dataElement.measurementList = XdfToSnirfMeasurmentList(xdf_fnirs_stream, snirf_file, probe).measurementList



class XdfToSnirfData():
    def __init__(self, probe: snirf.Probe, xdf_fnirs_stream, snirf_file):
        snirf_data_elemtent =  XdfToSnirfDataElement(xdf_fnirs_stream, snirf_file, probe)
        self.data = snirf.Data(snirf_file, conf)
        self.data.append(snirf_data_elemtent.dataElement)


class XdfToSnirfNirsElement():
    def __init__(self, xdf_streams, xdf_file_header, snirf_file):
        xdf_fnirs_stream = None
        xdf_aux_streams = []
        xdf_date, xdf_time = get(xdf_file_header, "info.datetime").split("T")
        for stream in xdf_streams:
            if get(stream, "info.type") == "NIRS":
                if get(stream, "info.name") == 'LUMO HA00030/GA00324':
                    stream = LumoxdfToStandardXdf(stream).stream
                xdf_fnirs_stream = stream #assume only one nirs stream per snirf
            else:
                xdf_aux_streams.append(stream)

        self.NirsElement = snirf.NirsElement("" , conf)


        for xdf_aux_stream in xdf_aux_streams:
            self.NirsElement.aux = XdfToSnirfAux(xdf_aux_stream).aux

        self.NirsElement.metaDataTags.FrequencyUnit = "Hz"
        self.NirsElement.metaDataTags.TimeUnit = "s"
        self.NirsElement.metaDataTags.LengthUnit = "mm"
        self.NirsElement.metaDataTags.add("PowerUnit", "mW")
        self.NirsElement.metaDataTags.MeasurementDate = xdf_date
        self.NirsElement.metaDataTags.MeasurementTime = xdf_time
        self.NirsElement.metaDataTags.SubjectID = get(xdf_fnirs_stream, "info.name")
        self.xdf_channels = get(xdf_fnirs_stream, "info.desc.channels.channel")
        self.xdf_optodes = get(xdf_fnirs_stream, "info.desc.optodes.optode")
        self.xdf_fiducials = get(xdf_fnirs_stream, "info.desc.fiducials.fiducial")


        self.NirsElement.probe = XdfToSnirfProbe(self.xdf_channels, self.xdf_optodes, self.xdf_fiducials).probe
        self.NirsElement.data = XdfToSnirfData(self.NirsElement.probe, xdf_fnirs_stream, snirf_file).data


class XdfToSnirfNirs():
    def __init__(self, xdf_streams, xdf_file_header, snirf_file): #how do we map aux xdf data stream to nirs stream? for now assume only 1 nirs stream
        self.nirs = snirf.Nirs(snirf_file, conf) 
        self.nirs.append(XdfToSnirfNirsElement(xdf_streams, xdf_file_header, snirf_file).NirsElement)





class XdfToSnirf():
    def __init__(self, path_to_snirf, path_to_xdf, validate) -> None:
        self.snirf = snirf.Snirf(path_to_snirf)
        self.snirf.formatVersion = 1.0
        xdf_streams, xdf_file_header = pyxdf.load_xdf(path_to_xdf)
        self.snirf.nirs = XdfToSnirfNirs(xdf_streams, xdf_file_header, self.snirf).nirs
        self.snirf.save()
        if validate:
            print("validating ", path_to_snirf)
            self.result = snirf.validateSnirf(path_to_snirf)
            print(self.result.display())


conf = snirf.SnirfConfig()

if __name__ == "__main__":
    parser = argparse.ArgumentParser("XDF to SNIRF Converter", 
            """This Program takes input in the form of an XDF file which must contain a
            captured LSL NIRS stream and produces a SNIRF file as output""")
    parser.add_argument("xdf_file_path")
    parser.add_argument("save_snirf_path")
    args = parser.parse_args()
    path_to_xdf = args.xdf_file_path
    save_location = args.save_snirf_path

    if os.path.exists(save_location):
        shutil.copy2(save_location, save_location + ".old")
        os.remove(save_location)
    converted_snirf = XdfToSnirf(save_location, path_to_xdf, True)
