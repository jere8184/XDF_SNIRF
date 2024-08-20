import pyxdf
import snirf
import utils
import numpy
import h5py
import traceback
import os


streams, file_header = pyxdf.load_xdf("sub-P001_ses-S001_task-Default_run-001_eeg.xdf")
conf = snirf.SnirfConfig()

xdf_fnirs_streams = []
xdf_aux_streams = []


for stream in streams:
    print(stream["info"]["type"])
    if stream["info"]["type"] == ["NIRS"]:
        xdf_fnirs_streams.append(stream)
    else:
        xdf_aux_streams.append(stream)





class XdfToSnirfMeasurmentListElement():

    def __init__(self, xdf_channel, probe: snirf.Probe):
        self.xdf_channel = xdf_channel
        self.snirf_probe = probe
        self.measurmentListElement = snirf.MeasurementListElement('/nirs/data1/measurementList1', conf)
        self.populate_measurment_list_element()

    def PopulateSourceIndex(self):
        try:
            self.measurmentListElement.sourceIndex = self.snirf_probe.sourceLabels.index(self.xdf_channel["source"][0]) + 1
        except:
            print(traceback.format_exc())


    def PopulateDetectorIndex(self):
        try:
            self.measurmentListElement.detectorIndex = self.snirf_probe.detectorLabels.index(self.xdf_channel["detector"][0]) + 1
        except:
            print(traceback.format_exc())

    def PopulateWavelengthIndex(self):
        try:
            self.measurmentListElement.wavelengthIndex = self.snirf_probe.wavelengths.index(float(self.xdf_channel["wavelen"][0])) + 1
        except:
            print(traceback.format_exc())

    def PopulateWavelegnthActual(self):
        try:
            if self.xdf_channel["wavelen_measured"]:
                self.measurmentListElement.wavelengthActual = self.snirf_probe.wavelengths.index(float(self.xdf_channel["wavelen_measured"][0])) + 1
        except:
            print(traceback.format_exc())
        
    def PopulateWavelengthEmissionActual(self):
        try:
            if self.xdf_channel["fluorescence"]:
                self.measurmentListElement.wavelengthEmissionActual = float(self.xdf_channel["fluorescence"]["wavelen_measured"][0])
        except:
            print(traceback.format_exc())


    def PopulateDataType(self):
        try:
            self.measurmentListElement.dataType = utils.Get_DataType(self.xdf_channel["measure"][0])
        except:
            print(traceback.format_exc())


    def PopulateDataUnit(self):
        try:
            if self.xdf_channel["unit"]:
                self.measurmentListElement.dataUnit = self.xdf_channel["unit"][0]
        except:
            print(traceback.format_exc())
    
    def PopulateDataTypeLabel(self):
        try:
            if self.xdf_channel["type"]:
                self.measurmentListElement.dataTypeLabel = self.xdf_channel["type"][0]
        except:
            if self.measurmentListElement.dataType == 99999:
                pass #throw error
            print(traceback.format_exc())
    
    def PopulateDataTypeIndex(self):
        try:
            if utils.Is_DCS(self.measurmentListElement.dataType):
                self.measurmentListElement.dataTypeIndex = numpy.where(self.snirf_probe.correlationTimeDelays == float(self.xdf_channel["dcs"]["delay"][0])) + 1
            elif utils.Is_Frequency_Domain(self.measurmentListElement.dataType):
                self.measurmentListElement.dataTypeIndex = numpy.where(self.snirf_probe.frequencies == float(self.xdf_channel["fd"]["frequency"][0])) + 1
            elif utils.Is_Gated_Time_Domain(self.measurmentListElement.dataType) or utils.Is_Gated_Time_Domain(self.measurmentListElement.dataType):
                self.measurmentListElement.dataTypeIndex = numpy.where(self.snirf_probe.timeDelays == float(self.xdf_channel["td"]["delay"][0])) + 1
            else:
                self.measurmentListElement.dataTypeIndex = 0
        except:
            print(traceback.format_exc())

    def PopulateSourcePower(self):
        try:
            if self.xdf_channel["sourcePower"]:
                self.measurmentListElementdataUnit = self.xdf_channel["sourcePower"][0]
        except:
            print(traceback.format_exc())

    def PopulateDetectorGain(self):
        try:
            if self.xdf_channel["gain"]:
                self.measurmentListElement.detectorGain = self.xdf_channel["gain"][0]
        except:
            print(traceback.format_exc())


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
        self.xdf_channels = xdf_fnirs_stream["info"]["desc"][0]["channels"][0]["channel"]
        self.xdf_source_optodes = []
        self.xdf_detector_optodes = []
        if xdf_fnirs_stream["info"]["desc"][0]["fiducials"]:
            self.xdf_fiducials = xdf_fnirs_stream["info"]["desc"][0]["fiducials"][0]["fiducial"]
        self.probe = snirf.Probe("PROBEGID", conf)
        self.SeperateXdfOptodes(xdf_fnirs_stream)
        self.PopulateProbe()


    def PopulateProbe(self):
        try:
            self.PopulateWaveLegnths()
        except:
            print(traceback.format_exc())


        try:
            self.PopulateSourcePos2D()
        except:
            print(traceback.format_exc())

        try:
            self.PopulateSourcePos3D()
        except:
            print(traceback.format_exc())

        try:
            self.PopulateDetectorPos2D()
        except:
            print(traceback.format_exc())

        try:
            self.PopulateDetectorPos3D()
        except:
            print(traceback.format_exc())

        try:
            self.PopulateFrequencies()
        except:
            print(traceback.format_exc())


        try:
            self.PopulateTimeDelays()
        except:
            print(traceback.format_exc())

        try:
            self.PopulateCorrelationTimeDelays()
        except:
            print(traceback.format_exc())

        try:
            self.PopulateSourceLabels()
        except:
            print(traceback.format_exc())

        try:
            self.PopulateDetectorLabels()
        except:
            print(traceback.format_exc())


        try:
            self.PopulateLandmarkLabels()
        except:
            print(traceback.format_exc())


        try:
            self.PopulateLandmarkPos2D()
        except:
            print(traceback.format_exc())

        try:
            self.PopulateLandmarkPos3D()
        except:
            print(traceback.format_exc())

        try:
            self.PopulateDetectorPos3D()
        except:
            print(traceback.format_exc())

    


    def PopulateLandmarkLabels(self):
        labels = []
        for fiducial in self.xdf_fiducials:
            if fiducial["label"]:
                labels.append(fiducial["label"][0])
        if labels:
            self.probe.landmarkLabels = labels


    def PopulateLandmarkPos2D(self):
        position = []
        for fiducial in self.xdf_fiducials:
            if fiducial["location"]:
                l = [float(fiducial["location"][0]["X"][0]), float(fiducial["location"][0]["Y"][0])]
            if self.probe.landmarkLabels:
                l.append(numpy.where(self.probe.landmarkLabels == fiducial["label"][0]) + 1)
            position.append(l)
        if position:
            self.probe.landmarkPos2D = position

    def PopulateLandmarkPos3D(self):
        position = []
        for fiducial in self.xdf_fiducials:
            if fiducial["location"]:
                l = [float(fiducial["location"][0]["X"][0]), float(fiducial["location"][0]["Y"][0]), float(fiducial["location"][0]["Z"][0])]
            if self.probe.landmarkLabels:
                l.append(numpy.where(self.probe.landmarkLabels == fiducial["label"][0]) + 1)
            position.append(l)
        if position:
            self.probe.landmarkPos3D = position

    def PopulateSourcePos2D(self):
        postions = []
        for optode in self.xdf_source_optodes:
            postions.append([float(optode["location"][0]["X"][0]), float(optode["location"][0]["Y"][0])])
        self.probe.sourcePos2D = postions

    def PopulateDetectorPos2D(self):
        postion = []
        for optode in self.xdf_detector_optodes:
            postion.append([float(optode["location"][0]["X"][0]), float(optode["location"][0]["Y"][0])])
        self.probe.detectorPos2D = postion

    def PopulateSourcePos3D(self):
        postions = []
        for optode in self.xdf_source_optodes:
            postions.append([float(optode["location"][0]["X"][0]), float(optode["location"][0]["Y"][0]), float(optode["location"][0]["Z"][0])])
        self.probe.sourcePos3D = postions

    def PopulateDetectorPos3D(self):
        postion = []
        for optode in self.xdf_detector_optodes:
            postion.append([float(optode["location"][0]["X"][0]), float(optode["location"][0]["Y"][0]), float(optode["location"][0]["Z"][0])])
        self.probe.detectorPos3D = postion

        
    def PopulateSourceLabels(self):
        labels = []
        for source in self.xdf_source_optodes:
            labels.append(source["label"][0])
        self.probe.sourceLabels = labels

    def PopulateDetectorLabels(self):
        labels = []
        for detector in self.xdf_detector_optodes:
            labels.append(detector["label"][0])
        self.probe.detectorLabels = labels   

    def SeperateXdfOptodes(self, xdf):
        for optode in xdf["info"]["desc"][0]["optodes"][0]["optode"]:
            if optode["function"][0] in  ["Source", "source"]:
                self.xdf_source_optodes.append(optode)
            if optode["function"][0] in ["Detector", "detector"]:
                self.xdf_detector_optodes.append(optode)

    def PopulateWaveLegnths(self):
        wavelengths = []
        wavelengthsEmission = []

        for channel in self.xdf_channels:
            wavelengths.append(channel["wavelen"])
            if channel["fluorescence"]:
                wavelengthsEmission.append(channel["fluorescence"]["wavelen"])

        s = set()
        if wavelengthsEmission:
            for wavelen, f_wavelen in zip(wavelengths, wavelengthsEmission):
                s.add((float(wavelen[0]), float(f_wavelen[0])))
            
            wavelengths.clear()
            wavelengthsEmission.clear()
            for wavelen, f_wavelen in s:
                wavelengths.append(wavelen)
                wavelengthsEmission.append(f_wavelen)
            
            self.probe.wavelengths = wavelengths
            self.probe.wavelengthsEmission = wavelengthsEmission
                
        else:
            for wavelen in wavelengths:
                s.add(float(wavelen[0]))
            self.probe.wavelengths = list(s)
    
    def PopulateCorrelationTimeDelays(self):
        delays = []
        widths = []

        for channel in self.xdf_channels:
            data_type = utils.Get_DataType(channel["measure"][0])
            if  utils.Is_Gated_Time_Domain(data_type) or utils.Is_Moment_Time_Domain(data_type):
                delays.append(channel["delay"][0])
                widths.append(channel["width"][0])

        s = set()
        for delay, width in zip(delays, widths):
            s.add((float(delay[0]), float(width[0])))
        delays.clear()
        widths.clear()
        for delay, width in s:
            delays.append(delay)
            widths.append(width)
        if delays:
            self.probe.correlationTimeDelays = delays
        if widths:
            self.probe.correlationTimeDelayWidths = widths
           
    def PopulateTimeDelays(self):
        delays = []
        widths = []
        orders = []


        for channel in self.xdf_channels:
            data_type = utils.Get_DataType(channel["measure"][0])
            if  utils.Is_Gated_Time_Domain(data_type) or utils.Is_Moment_Time_Domain(data_type):
                delays.append(channel["td"]["delay"][0])
                widths.append(channel["td"]["width"][0])
                orders.append(channel["td"]["order"][0])

        s = set()
        for delay, width, order in zip(delays, widths, orders):
            s.add((float(delay), float(width), float(order)))
        l = list(s)
        delays.clear()
        widths.clear()
        orders.clear()
        for delay, width, order in l:
            delays.append(delay)
            widths.append(width)
            orders.append(order)
        
        if delays:
            self.probe.timeDelays = delays
        if widths:
            self.probe.timeDelayWidths = widths
        if orders:
            self.probe.momentOrders = orders
            
        
    def PopulateFrequencies(self):
        frequencies = []
        if self.xdf_channels[0]["fd"] not in [None, []]:
            for channel in self.xdf_channels:
                    frequencies.append(channel["fd"][0]["frequencies"][0])
            s = set()
            for frequencie in zip(frequencies):
                s.add(frequencie)
            self.frequencies = frequencies


class XdfToSnirfMeasurmentList():
    def __init__(self, xdf_fnirs_stream, probe: snirf.Probe):
        self.measurementList = snirf.MeasurementList(snirf_base, conf)
        for i, channel in enumerate(xdf_fnirs_stream["info"]["desc"][0]["channels"][0]["channel"]):
            self.measurementList.append(XdfToSnirfMeasurmentListElement(channel, probe).measurmentListElement)



class XdfToSnirfDataElement():
    def __init__(self, xdf_fnirs_stream, probe: snirf.Probe):
        self.dataElement = snirf.DataElement("DATAELEMENT_GID", conf)
        self.dataElement.measurementList = XdfToSnirfMeasurmentList(xdf_fnirs_stream, probe).measurementList



class XdfToSnirfData():
    def __init__(self, probe: snirf.Probe, xdf_fnirs_stream):
        snirf_data_elemtent =  XdfToSnirfDataElement(xdf_fnirs_stream, probe)
        self.data = snirf.Data(snirf_base, conf)
        self.data.append(snirf_data_elemtent.dataElement)


        
class XdfToSnirf():
    def __init__(self):
        
        self.nirs = snirf.Nirs(snirf_base, conf) 
        
        if len(xdf_fnirs_streams) == 1:
            self.nirs.append(XdfToSnirfNirsElement(xdf_fnirs_streams[0]).NirsElement)
        else:
            for i, fnirs_stream in enumerate(xdf_fnirs_streams):
                self.nirs.append(XdfToSnirfNirsElement(fnirs_stream).NirsElement)
        

class XdfToSnirfNirsElement():
    def __init__(self, xdf_fnirs_stream):
        self.NirsElement = snirf.NirsElement("NirsElement_GID" , conf)
        self.NirsElement.probe = XdfToSnirfProbe(xdf_fnirs_stream).probe
        self.NirsElement.data = XdfToSnirfData(self.NirsElement.probe, xdf_fnirs_stream).data
        


os.remove("./converted.snirf")
snirf_base = snirf.Snirf("converted.snirf")
converted_snirf = XdfToSnirf()
snirf_base.nirs = converted_snirf.nirs
snirf_base.save(snirf_base)

result = snirf.validateSnirf("converted.snirf")

pass
#snirf_measurement_list = snirf.MeasurementList(s, conf)
#populate_measurment_list(snirf_measurement_list, snirf_probe)