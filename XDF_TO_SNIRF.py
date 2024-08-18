import pyxdf
import snirf
import utils
import numpy
import h5py


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





class XdfToSnirfMeasurmentListElement(snirf.MeasurementListElement):

    def __init__(self, gid: h5py.h5g.GroupID, cfg: snirf.SnirfConfig, xdf_channel, probe: snirf.Probe):
        super().__init__(gid, cfg)
        self.xdf_channel = xdf_channel
        self.snirf_probe = probe

    def PopulateSourceIndex(self):
        try:
            self.sourceIndex = numpy.where(self.snirf_probe.sourceLabels == self.xdf_channel["source"][0]) + 1
        finally:
            return


    def PopulateDetectorIndex(self):
        try:
            self.detectorIndex = numpy.where(self.snirf_probe.detectorLabels == self.xdf_channel["detector"][0]) + 1
        finally:
            return

    def PopulateWavelengthIndex(self):
        try:
            self.wavelengthIndex = numpy.where(self.snirf_probe.wavelengths == float(self.xdf_channel["wavelen"][0])) + 1
        finally:
            return

    def PopulateWavelegnthActual(self):
        try:
            self.wavelengthActual = float(self.xdf_channel["wavelen_measured"][0])
        finally:
            return
        
    def PopulateWavelengthEmissionActual(self):
        try:
            self.wavelengthEmissionActual = float(self.xdf_channel["fluorescence"]["wavelen_measured"][0])
        finally:
            return


    def PopulateDataType(self):
        try:
            self.dataType = utils.Get_DataType(self.xdf_channel["measure"][0])
        finally:
            return


    def PopulateDataUnit(self):
        try:
            self.dataUnit = self.xdf_channel["unit"][0]
        finally:
            return  
    
    def PopulateDataTypeLabel(self):
        try:
            self.dataTypeLabel = self.xdf_channel["type"][0]
        finally:
            if self.dataType == 99999:
                pass #throw error
            return  
    
    def PopulateDataTypeIndex(self):
        try:
            if utils.Is_DCS(self.dataType):
                self.dataTypeIndex = numpy.where(self.snirf_probe.correlationTimeDelays == float(self.xdf_channel["dcs"]["delay"][0])) + 1
            elif utils.Is_Frequency_Domain(self.dataType):
                self.dataTypeIndex = numpy.where(self.snirf_probe.frequencies == float(self.xdf_channel["fd"]["frequency"][0])) + 1
            elif utils.Is_Gated_Time_Domain(self.dataType) or utils.Is_Gated_Time_Domain(self.dataType):
                self.dataTypeIndex = numpy.where(self.snirf_probe.timeDelays == float(self.xdf_channel["td"]["delay"][0])) + 1
        finally:
            return

    def PopulateSourcePower(self):
        try:
            self.dataUnit = self.xdf_channel["sourcePower"][0]
        finally:
            return  

    def PopulateDetectorGain(self):
        try:
            self.detectorGain = self.xdf_channel["gain"][0]
        finally:
            return


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


s = snirf.loadSnirf("./save.snirf")


class XdfToSnirfProbe(snirf.Probe):
    def __init__(self, var, cfg: snirf.SnirfConfig, xdf_fnirs_stream):
        super().__init__(var, cfg)
        self.xdf_channels = xdf_fnirs_stream["info"]["desc"][0]["channels"][0]["channel"]
        self.xdf_source_optodes = []
        self.xdf_detector_optodes = []
        self.xdf_fiducials = xdf_fnirs_stream["info"]["desc"][0]["fiducials"][0]

        self.SeperateXdfOptodes(xdf_fnirs_stream)
        self.PopulateProbe()
        self._validate()


    def PopulateProbe(self):
        self.PopulateWaveLegnths()
        self.PopulateSourcePos2D()
        self.PopulateSourcePos3D()
        self.PopulateDetectorPos2D()
        self.PopulateDetectorPos3D()
        self.PopulateFrequencies()
        self.PopulateTimeDelays()
        self.PopulateCorrelationTimeDelays()
        self.PopulateSourceLabels()
        self.PopulateDetectorLabels()
        self.PopulateLandmarkLabels()
        self.PopulateLandmarkPos2D()
        self.PopulateDetectorPos3D()

    


    def PopulateLandmarkLabels(self):
        labels = []
        for fiducial in self.xdf_fiducials:
            labels.append(fiducial["label"][0])
        self.landmarkLabels = labels


    def PopulateLandmarkPos2D(self):
        position = []
        for fiducial in self.xdf_fiducials:
            position.append([float(fiducial["X"][0]), float(fiducial["Y"][0]), numpy.where(self.landmarkLabels == fiducial["location"][0]) + 1])

        self.landmarkPos2D = position

    def PopulateLandmarkPos3D(self):
        position = []
        for fiducial in self.xdf_fiducials:
            position.append([float(fiducial["X"][0]), float(fiducial["Y"][0]), float(fiducial["Z"][0]), numpy.where(self.landmarkLabels == fiducial["location"][0]) + 1])
        self.landmarkPos3D = position

    def PopulateSourcePos2D(self):
        postions = []
        for optode in self.xdf_source_optodes:
            postions.append([optode["location"]["X"], optode["location"]["Y"]])
        self.sourcePos2D = postions

    def PopulateDetectorPos2D(self):
        postion = []
        for optode in self.xdf_detector_optodes:
            postion.append([optode["location"]["X"], optode["location"]["Y"]])
        self.detectorPos2D = postion

    def PopulateSourcePos3D(self):
        postions = []
        for optode in self.xdf_source_optodes:
            postions.append([optode["location"]["X"], optode["location"]["Y"], optode["location"]["Z"]])
        self.sourcePos3D = postions

    def PopulateDetectorPos3D(self):
        postion = []
        for optode in self.xdf_detector_optodes:
            postion.append([optode["location"]["X"], optode["location"]["Y"], optode["location"]["Z"]])
        self.detectorPos3D = postion

        
    def PopulateSourceLabels(self):
        labels = []
        for source in self.xdf_source_optodes:
            labels.append(source["label"])
        self.sourceLabels = labels

    def PopulateDetectorLabels(self):
        labels = []
        for detector in self.xdf_detector_optodes:
            labels.append(detector["label"])
        self.detectorLabels = labels   

    def SeperateXdfOptodes(self, xdf):
        for optode in xdf["info"]["desc"][0]["optodes"][0]["optode"]:
            if optode["function"][0] == "source":
                self.xdf_source_optodes.append(optode)
            if optode["function"][0] == "detector":
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
            
            self.wavelengths = wavelengths
            self.wavelengthsEmission = wavelengthsEmission
                
        else:
            for wavelen in wavelengths:
                s.add(float(wavelen[0]))
            self.wavelengths = list(s)
    
    def PopulateCorrelationTimeDelays(self):
        delays = []
        widths = []

        for channel in self.xdf[0]["info"]["desc"][0]["channels"][0]["channel"]["dcs"]:
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
        self.correlationTimeDelays = delays
        self.correlationTimeDelayWidths = widths
           
    def PopulateTimeDelays(self):
        delays = []
        widths = []
        orders = []


        for channel in self.xdf[0]["info"]["desc"][0]["channels"][0]["channel"]["td"]:
            delays.append(channel["delay"][0])
            widths.append(channel["width"][0])
            orders.append(channel["order"][0])

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
        self.timeDelays = delays
        self.widths = widths
        self.momentOrders = orders
            
        
    def PopulateFrequencies(self):
        frequencies = []

        for channel in self.xdf_channels:
                frequencies.append(channel["fd"][0]["frequencies"][0])
        s = set()
        for frequencie in zip(frequencies):
            s.add(frequencie)
        self.frequencies = frequencies


class XdfToSnirfDataElement(snirf.DataElement):
    def __init__(self, gid: h5py.h5g.GroupID, cfg: snirf.SnirfConfig, xdf_fnirs_stream):
        super().__init__(gid, cfg)
        self.measurementList = snirf.MeasurementList(snirf.snirf, conf)
        for i, channel in enumerate(xdf_fnirs_stream["info"]["desc"][0]["channels"][0]["channel"]):
            XdfToSnirfMeasurmentListElement(gid + f"/measurmentList{i}", conf, channel, )


class XdfToSnirfData(snirf.Data):
    def __init__(self, h: h5py.File, cfg: snirf.SnirfConfig, probe: snirf.Probe):
        super().__init__(h, cfg)
        self.append(XdfToSnirfDataElement("/data", conf))

        
class XdfToSnirf(snirf.Nirs):
    def __init__(self, h: h5py.File, cfg: snirf.SnirfConfig):
        super().__init__(h, cfg)
        for i, fnirs_stream in enumerate(xdf_fnirs_streams):
            self.append(XdfToSnirfNirsElement(f"/nirs{i}", conf, fnirs_stream))




class XdfToSnirfNirsElement(snirf.NirsElement):
    def __init__(self, gid: h5py.h5g.GroupID, cfg: snirf.SnirfConfig, xdf_fnirs_streams):
        super().__init__(gid, cfg)
        self.probe = XdfToSnirfProbe(gid + "/probe", conf, xdf_fnirs_streams)
        self.data = XdfToSnirfData(snirf.snirf, conf, self.probe)

XdfToSnirf(snirf.Snirf("./new_snirf.snirf"), conf)
#snirf_measurement_list = snirf.MeasurementList(s, conf)
#populate_measurment_list(snirf_measurement_list, snirf_probe)