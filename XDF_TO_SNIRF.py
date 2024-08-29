import pyxdf
import snirf
from utils import *
from xdf_formatter import *
import os
from mne.io import read_raw_snirf
import argparse
import shutil
from functools import partial


class XdfToSnirfMeasurmentListElement():
    """
    This class converts an XDF channel into a corresponding measurement list element in the SNIRF format.
    Each measurement list element contains information about a NIRS channel, such as source/detector indices, 
    wavelength information, data type, and other relevant data.
    """
    def __init__(self, xdf_channel, probe: snirf.Probe):
        """
        Initialize the class with an XDF channel and a SNIRF probe object.
        :param xdf_channel: A dictionary-like object containing channel-specific data from the XDF file. Formated
        accoring to https://github.com/sccn/xdf/wiki/NIRS-Meta-Data
        :param probe: A pysnirf2.Probe object containing information about the probe configuration.
        """
        
        self.xdf_channel = xdf_channel #Store the XDF channel.
        self.snirf_probe = probe #Store the pysnirf2 probe.
        self.measurmentListElement = snirf.MeasurementListElement('', conf) # Populate the pysnirf2 MeasurementListElement with the relevant data from the XDF channel.
        self.populate_measurment_list_element()

    def PopulateSourceIndex(self):
        """
        Populate the source index for the measurement list element.
        The source index refers to the index of the source optode in the pysnirf2 probe.
        """
        # Get the source label from the XDF channel, find its index in the pysnirf2 probe, and set it as the source index.
        self.measurmentListElement.sourceIndex =  get_index(self.snirf_probe.sourceLabels, get(self.xdf_channel, "source")) + 1

    def PopulateDetectorIndex(self):
        """
        Populate the detector index for the measurement list element.
        The detector index refers to the index of the detector optode in the pysnirf2 probe.
        """
        # Get the detector label from the XDF channel, find its index in the pysnirf2 probe, and set it as the detector index.
        self.measurmentListElement.detectorIndex =  get_index(self.snirf_probe.detectorLabels, get(self.xdf_channel, "detector")) + 1

    def PopulateWavelengthIndex(self):
        """
        Populate the wavelength index for the measurement list element.
        The wavelength index refers to the Index of the "nominal" wavelength (in probe.wavelengths).
        """
        # Get the wavelength from the XDF channel, find its index in the pysnirf2 probe, and set it as the wavelength index.
        self.measurmentListElement.wavelengthIndex = get_index(self.snirf_probe.wavelengths, get(self.xdf_channel, "wavelen")) + 1

    def PopulateWavelegnthActual(self):
        """
        Populate the actual measured wavelength for the measurement list element.
        """
        # Get the actual measured wavelength from the XDF channel and set it in the measurement list element.
        self.measurmentListElement.wavelengthActual = get(self.xdf_channel, "wavelen_measured")
        
    def PopulateWavelengthEmissionActual(self):
        """
        Populate the actual measured wavelength for fluorescence emission, if available.
        """
        # Get the fluorescence emission wavelength from the XDF channel and set it in the measurement list element.
        self.measurmentListElement.wavelengthEmissionActual = get(self.xdf_channel, "fluorescence.wavelen_measured")

    def PopulateDataType(self):
        """
        Populate the data type for the measurement list element.
        The data type describes the type of measurement, such as continuous wave, frequency domain, etc.
        """
        # Get the data type from the XDF channel, convert it, and set it in the measurement list element.
        self.measurmentListElement.dataType =  Get_DataType(get(self.xdf_channel, "measure"))

    def PopulateDataUnit(self):
        """
        Populate the data unit for the measurement list element.
        The data unit specifies the SI units identifier for the given channel such as V/us.
        """
        # Get the data unit from the XDF channel and set it in the measurement list element.
        self.measurmentListElement.dataUnit = get(self.xdf_channel, "unit")

    
    def PopulateDataTypeLabel(self):
        """
        Populate the data type label for the measurement list element.
        The data type label provides a descriptive label for the type of data being measured.
        """
        # Get the data type label from the XDF channel and set it in the measurement list element.
        self.measurmentListElement.dataTypeLabel = get(self.xdf_channel, "type")

    
    def PopulateDataTypeIndex(self):
        """
        Populate the data type index for the measurement list element.
        The data type index is used to reference additional properties specific to certain types of measurements,
        such as delay and width for gated time-domain measurements.
        """
        data_type_index = 0
        # Check if the channel is of type DCS (Diffuse Correlation Spectroscopy).
        if Is_DCS(self.measurmentListElement.dataType):
            # Convert delay and width from picoseconds to seconds and find their indices.
            delay = convert("ps", "s", get(self.xdf_channel, "dcs.delay"))
            width = convert("ps", "s", get(self.xdf_channel, "dcs.width"))
            delay_indexes = {i for i, x in enumerate(self.snirf_probe.correlationTimeDelays) if x == delay}
            width_indexes = {i for i, x in enumerate(self.snirf_probe.correlationTimeDelayWidths) if x == width}
            # Find the intersection of delay and width indices to get the data type index.
            data_type_index = delay_indexes.intersection(width_indexes).pop() + 1
        
        # Check if the channel is of type Frequency Domain.
        elif Is_Frequency_Domain(self.measurmentListElement.dataType):
            # Get the frequency from the XDF channel, find its index in the pysnirf2 probe, and set it as the data type index.
            data_type_index = get_index(self.snirf_probe.frequencies, get(self.xdf_channel, "fd.frequency")) + 1
        
        # Check if the measurement is of type Moment Time Domain.
        elif Is_Moment_Time_Domain(self.measurmentListElement.dataType):
            # Get the order from the XDF channel, find its index in the pysnirf2 probe, and set it as the data type index.
            data_type_index = get_index(self.snirf_probe.momentOrders, get(self.xdf_channel, "td.order")) + 1           
        
        # Check if the measurement is of type Gated Time Domain.
        elif Is_Gated_Time_Domain(self.measurmentListElement.dataType):
            # Convert delay and width from picoseconds to seconds and find their indices.
            delay = convert("ps", "s", get(self.xdf_channel, "td.delay"))
            width = convert("ps", "s", get(self.xdf_channel, "td.width"))
            delay_indexes = {i for i, x in enumerate(self.snirf_probe.timeDelays) if x == delay}
            width_indexes = {i for i, x in enumerate(self.snirf_probe.timeDelayWidths) if x == width}
            # Find the intersection of delay and width indices to get the data type index.
            data_type_index = delay_indexes.intersection(width_indexes).pop() + 1
        # Set the data type index in the measurement list element.
        self.measurmentListElement.dataTypeIndex = data_type_index


    def PopulateSourcePower(self):
        """
        Populate the source power for the measurement list element.
        The source power represents the power emitted by the source optode.
        """
        # Get the source power from the XDF channel and set it in the measurement list element.
        self.measurmentListElement.sourcePower = get(self.xdf_channel, "power")

    def PopulateDetectorGain(self):
        """
        Populate the detector gain for the measurement list element.
        The detector gain represents the amplification factor applied to the signal detected by the detector optode.
        """
        # Get the detector gain from the XDF channel and set it in the measurement list element.
        self.measurmentListElement.detectorGain = get(self.xdf_channel, "gain")

    def populate_measurment_list_element(self):
        """
        Populate all fields of the measurement list element by calling the respective methods.
        """
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
    """
    This class converts XDF NIRS channel and optode information into a corresponding probe object 
    in the pysnirf2 format. The probe object includes details like source and detector positions, 
    wavelengths, frequencies, and other relevant measurement properties.
    """
    def __init__(self, xdf_nirs_channels, xdf_nirs_optodes, xdf_nirs_fiducials = []):
        """
        Initialize the class with XDF NIRS channel data, optode data, and optional fiducials.
        
        :param xdf_nirs_channels: A list of channels from the XDF file containing channel specific data.
        :param xdf_nirs_optodes: A list of optodes (sources and detectors) from the XDF file.
        :param xdf_nirs_fiducials: Optional list of fiducial points from the XDF file.
        """
        self.xdf_channels = xdf_nirs_channels #Store the XDF channel data.
        self.xdf_optodes = xdf_nirs_optodes #Store the XDF optode data.
        self.xdf_source_optodes = [] #List to hold source optodes from the XDF data.
        self.xdf_detector_optodes = [] #List to hold detector optodes from the XDF data.
        self.xdf_fiducials = xdf_nirs_fiducials # Store the XDF fiducials data.
        # Create a new probe Group for the SNIRF file.  
        self.probe = snirf.Probe("", conf)
        # Separate the XDF optodes into sources and detectors.
        self.SeperateXdfOptodes()
        # Populate the probe with the relevant data.
        self.PopulateProbe()


    def PopulateProbe(self):
        """
        Populate the probe object with various details from the XDF data.
        """
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
        """
        Populate the landmark labels for the probe.
        Landmark labels represent specific points of reference on the probe, such as fiducials.
        """        
        labels = set()  # Use a set to store unique labels.
        for fiducial in self.xdf_fiducials:
            try_add(labels, get(fiducial, "label"), "None")
        if labels:
            # Sort and set the landmark labels in the probe object.
            self.probe.landmarkLabels = sorted(list(labels))

    def PopulateLandmarkPos(self):
        """
        Populate the 2D or 3D positions of the landmarks.
        This includes the coordinates of fiducial points.
        """
        self.probe.landmarkPos3D = [] #List to hold 3D positions of landmarks.
        self.probe.landmarkPos2D = [] #List to hold 2D positions of landmarks.
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
                #If Z-coordinate is available, it's a 3D position.
                try_append(l, Z)
                try_append(l, label_index)
                self.probe.landmarkPos3D.append(l)
            else:
                # If no Z-coordinate, it's a 2D position.
                try_append(l, label_index)
                self.probe.landmarkPos2D.append(l)

    def PopulateSourcePos(self):
        """
        Populate the 2D or 3D positions of the source optodes.
        """
        self.probe.sourcePos3D = [] #List to hold 3D positions of sources.
        self.probe.sourcePos2D = [] #List to hold 2D positions of sources.
        for optode in self.xdf_source_optodes:
            X = get(optode, "location.X")
            Y = get(optode, "location.Y")
            Z = get(optode, "location.Z")
            l = [X, Y]
            if Z:
                #If Z-coordinate is available, it's a 3D position.
                l.append(Z)
                self.probe.sourcePos3D.append(l)
            else:
                #If no Z-coordinate, it's a 2D position.
                self.probe.sourcePos2D.append(l)

    def PopulateDetectorPos(self):
        """
        Populate the 2D and 3D positions of the detector optodes.
        """
        self.probe.detectorPos3D = [] #List to hold 3D positions of detectors.
        self.probe.detectorPos2D = [] #List to hold 2D positions of detectors.
        for optode in self.xdf_detector_optodes:
            X = get(optode, "location.X")
            Y = get(optode, "location.Y")
            Z = get(optode, "location.Z")
            l = [X, Y]
            if Z:
                #If Z-coordinate is available, it's a 3D position.
                l.append(Z)
                self.probe.detectorPos3D.append(l)
            else:
                #If no Z-coordinate, it's a 2D position.
                self.probe.detectorPos2D.append(l)
        
    def PopulateSourceLabels(self):
        """
        Populate the labels for the source optodes.
        """
        labels = [] #List to hold source labels.
        for source in self.xdf_source_optodes:
            try_append(labels, get(source, "label"))
        self.probe.sourceLabels = labels

    def PopulateDetectorLabels(self):
        """
        Populate the labels for the detector optodes.

        """
        labels = []
        for detector in self.xdf_detector_optodes:
            try_append(labels, get(detector, "label"))
        self.probe.detectorLabels = labels   

    def SeperateXdfOptodes(self):
        """
        Separate the XDF optodes into source and detector lists.
        This is done based on the "function" value of the xdf optode (either "Source" or "Detector").
        """
        for optode in self.xdf_optodes:
            if get(optode, "function") in  ["Source", "source"]:
                self.xdf_source_optodes.append(optode)
            if get(optode, "function") in ["Detector", "detector"]:
                self.xdf_detector_optodes.append(optode)

    def PopulateWaveLegnths(self):
        """
        Populate the nominal wavelengths and, if applicable, nominal fluorescence emission wavelengths.
        """
        s = set() #Set to store unique wavelength and fluorescence wavelength pairs.
        for channel in self.xdf_channels:
            wavelen = get(channel, "wavelen")
            fluorescence_wavelen = get(channel, "fluorescence.wavelen")
            s.add((wavelen, fluorescence_wavelen))

        wavelengths = [] #List to hold wavelengths.
        wavelengthsEmissions = [] #List to hold fluorescence emission wavelengths.
        for wavelength, wavelengthsEmission in s:
            try_append(wavelengths, wavelength) 
            try_append(wavelengthsEmissions, wavelengthsEmission, 0)

        self.probe.wavelengths = wavelengths #store the wavelengths.
        self.probe.wavelengthsEmission = wavelengthsEmissions #store the fluorescence wavelengths.
    
    def PopulateCorrelationTimeDomain(self):
        """
        Populate the correlation time domain data for Diffuse Correlation Spectroscopy (DCS) measurements.
        This includes delays and widths of time windows for correlating light intensity fluctuations.
        """
        dcs = set() #Set to store unique delay and width pairs.
        for channel in self.xdf_channels:
            data_type = Get_DataType(get(channel, "measure"))
            if  Is_DCS(data_type):
                delay = convert("ps", "s", get(channel, "dcs.delay"))
                width = convert("ps", "s", get(channel, "dcs.width"))
                dcs.add((delay, width))

        delays = []  #List to hold delays.
        widths = []  #List to hold widths.
        for delay, width in dcs:
            delays.append(delay)
            widths.append(width)

        #Store the delays and widths in the probe object.
        self.probe.correlationTimeDelays = delays
        self.probe.correlationTimeDelayWidths = widths
           
    def PopulateGatedTimeDomain(self):
        """
        Populate the gated time domain data for measurements with gated time-domain spectroscopy (GTD).
        """
        td = set()  #Set to store unique delay and width pairs for gated time domain measurements.

        for channel in self.xdf_channels:
            data_type = Get_DataType(get(channel, "measure"))
            if  Is_Gated_Time_Domain(data_type):
                delay =  convert("ps", "s" ,get(channel, "td.delay"))
                width = convert("ps", "s" ,get(channel, "td.width"))
                td.add((delay, width))
        
        delays = [] #List to hold delays.
        widths = [] #List to hold widths.
        for delay, width in td:
            delays.append(delay)
            widths.append(width)

        #Store the delays and widths in the probe object.
        self.probe.timeDelays = delays
        self.probe.timeDelayWidths = widths

    def PopulateMomentTimeDomain(self):
        """
        Populate the moment time domain data for measurements involving moment time-domain spectroscopy.
        """
        td = set() # Set to store unique moment orders.
        for channel in self.xdf_channels:
            data_type = Get_DataType(get(channel, "measure"))
            if  Is_Moment_Time_Domain(data_type):
                order = get(channel,"td.order")  #Extract the order of the moment from the channel data.
                td.add(order)
        
        orders = [] #List to hold moment orders.
        for order in td:
            orders.append(order)

        #Store the moment orders in the probe object.
        self.probe.momentOrders = orders
            
        
    def PopulateFrequencies(self):
        """
        Populate the frequency domain data for measurements involving frequency domain spectroscopy (FDS).
        """
        frequencies = [] #List to hold frequencies.
        for channel in self.xdf_channels:
            data_type = Get_DataType(get(channel, "measure"))
            if Is_Frequency_Domain(data_type):
                try_append(frequencies, get(channel, "fd.frequencies"))
        
        #Store the frequencies in the probe object.
        self.probe.frequencies = frequencies


class XdfToSnirfMeasurmentList():
    """
    Class to convert a list of XDF NIRS channels into a pysnirf2 MeasurementList.
    
    This class initializes a pysnirf2 MeasurementList object and populates it with MeasurementListElement objects
    created from XDF NIRS channel data.
    """
    def __init__(self, xdf_nirs_stream, snirf_file, probe: snirf.Probe):
        """
        Initialize the XdfToSnirfMeasurmentList class.
        
        :param xdf_nirs_stream: XDF stream containing NIRS channels.
        :param snirf_file: Path to the SNIRF file where the MeasurementList will be saved.
        :param probe: pysnirf2.Probe object containing information about sources, detectors, and other probe details.
        """
        # Initialize the MeasurementList object from pysnirf2 using the provided SNIRF file and configuration.
        self.measurementList = snirf.MeasurementList(snirf_file, conf)

        # Retrieve channels from the XDF stream.
        channels = get(xdf_nirs_stream, "info.desc.channels.channel")
        # Convert each channel to MeasurementListElement and append to pysnir2 measurementList object.
        for channel in channels:
            self.measurementList.append(XdfToSnirfMeasurmentListElement(channel, probe).measurmentListElement)



class XdfToSnirfAuxElement():
    """
    Initialize the XdfToSnirfAuxElement class.
    
    :param xdf_aux_stream: XDF stream containing auxiliary data (e.g., accelerometer, gyroscope).
    """
    def __init__(self, xdf_aux_stream) -> None:
        self.auxElement = snirf.AuxElement("", conf) #Initialize the AuxElement object from pysnirf2 with an empty name and configuration.
        xdf_time_Stamps = get(xdf_aux_stream, "time_stamps") #Retrieve the time stamps from the XDF auxiliary stream.
        self.auxElement.time = numpy.array(xdf_time_Stamps) - xdf_time_Stamps[0] #Normalize time stamps relative to the start time and assign them to the AuxElement.
        self.auxElement.dataTimeSeries = get(xdf_aux_stream, "time_series") #Populate the AuxElement with the time series data from the XDF auxiliary stream.
        self.auxElement.name = get(xdf_aux_stream, "info.name") #Set the name of the AuxElement based on the name provided in the XDF auxiliary stream.



class XdfToSnirfAux():
    """
    Class to convert XDF auxiliary streams into SNIRF Aux objects.
    """
    def __init__(self, snirf_file, xdf_aux_streams) -> None:
        """
        Initialize the XdfToSnirfAux class.

        :param snirf_file: The target SNIRF file to which auxiliary data will be added.
        :param xdf_aux_streams: A list of XDF streams containing auxiliary data.
        """
        #Initialize the SNIRF Aux object using the specified SNIRF file and configuration.
        self.aux = snirf.Aux(snirf_file, conf)
        #Loop through each XDF auxiliary stream and convert it to a SNIRF AuxElement.
        for aux_stream in xdf_aux_streams:
            self.aux.append(XdfToSnirfAuxElement(aux_stream).auxElement)


class XdfToSnirfDataElement():
    """
    Class to convert an XDF NIRS stream into a SNIRF DataElement.
    """
    def __init__(self, xdf_nirs_stream, snirf_file, probe: snirf.Probe):
        """
        Initialize the XdfToSnirfDataElement class.

        :param xdf_nirs_stream: The XDF stream containing NIRS data.
        :param snirf_file: The target SNIRF file to which the data element will be added.
        :param probe: The SNIRF probe object that corresponds to this data element.
        """
        self.dataElement = snirf.DataElement("", conf) #Initialize the SNIRF DataElement object using the specified configuration.
        
        #Retrieve the time stamps from the XDF NIRS stream.
        xdf_time_Stamps = get(xdf_nirs_stream, "time_stamps") 
        self.dataElement.time = numpy.array(xdf_time_Stamps) - xdf_time_Stamps[0]

        #Populate the time series data into the DataElement.
        self.dataElement.dataTimeSeries = get(xdf_nirs_stream, "time_series")
        #Create and assign the MeasurementList to the DataElement.
        self.dataElement.measurementList = XdfToSnirfMeasurmentList(xdf_nirs_stream, snirf_file, probe).measurementList



class XdfToSnirfData():
    """
    Class to convert XDF NIRS streams into SNIRF Data object.
    """
    def __init__(self, probe: snirf.Probe, xdf_nirs_stream, snirf_file):
        """
        Initialize the XdfToSnirfData class.

        :param probe: The SNIRF probe object that corresponds to the data.
        :param xdf_nirs_stream: The XDF stream containing NIRS data.
        :param snirf_file: The target SNIRF file to which the data will be added.
        """
        #Convert the XDF NIRS stream to a SNIRF DataElement.
        snirf_data_elemtent =  XdfToSnirfDataElement(xdf_nirs_stream, snirf_file, probe)
        self.data = snirf.Data(snirf_file, conf) #Initialize the SNIRF Data object using the specified configuration.
        self.data.append(snirf_data_elemtent.dataElement) #Append the converted DataElement to the SNIRF Data object.


class XdfToSnirfNirsElement():
    """
    Class to convert XDF streams into a SNIRF NirsElement.
    """
    def __init__(self, xdf_streams, xdf_file_header, snirf_file):
        """
        Initialize the XdfToSnirfNirsElement class.

        :param xdf_streams: A list of XDF streams, including fNIRS and auxiliary data.
        :param xdf_file_header: Header information from the XDF file.
        :param snirf_file: The target SNIRF file to which the NirsElement will be added.
        """
        xdf_nirs_stream = None
        xdf_aux_streams = []
        #xdf_date, xdf_time = get(xdf_file_header, "info.datetime", "").split("T")
        
        #Loop through streams to separate NIRS and auxiliary data streams.
        for stream in xdf_streams:
            if get(stream, "info.type") == "NIRS":
                #Handle any special cases for specific devices (e.g., LUMO device).
                if get(stream, "info.name") == 'LUMO HA00030/GA00324':
                    stream = LumoxdfToStandardXdf(stream).stream
                xdf_nirs_stream = stream  #Assume only one NIRS stream per XDF file.
            else:
                xdf_aux_streams.append(stream)

        #Initialize the SNIRF NirsElement object.
        self.NirsElement = snirf.NirsElement("" , conf)

        #Convert and assign auxiliary data to the NirsElement.
        self.NirsElement.aux = XdfToSnirfAux(snirf_file, xdf_aux_streams).aux


        #Populate the metaDataTags for units and subject information.
        self.NirsElement.metaDataTags.FrequencyUnit = "Hz"
        self.NirsElement.metaDataTags.TimeUnit = "s"
        self.NirsElement.metaDataTags.LengthUnit = "mm"
        self.NirsElement.metaDataTags.add("PowerUnit", "mW")
        #self.NirsElement.metaDataTags.MeasurementDate = xdf_date
        #self.NirsElement.metaDataTags.MeasurementTime = xdf_time
        self.NirsElement.metaDataTags.SubjectID = get(xdf_nirs_stream, "info.name")

        #Retrieve and assign channel, optode, and fiducial information from the XDF NIRS stream.
        self.xdf_channels = get(xdf_nirs_stream, "info.desc.channels.channel")
        self.xdf_optodes = get(xdf_nirs_stream, "info.desc.optodes.optode")
        self.xdf_fiducials = get(xdf_nirs_stream, "info.desc.fiducials.fiducial")

        #Convert and assign the probe and data to the NirsElement.
        self.NirsElement.probe = XdfToSnirfProbe(self.xdf_channels, self.xdf_optodes, self.xdf_fiducials).probe
        self.NirsElement.data = XdfToSnirfData(self.NirsElement.probe, xdf_nirs_stream, snirf_file).data


class XdfToSnirfNirs():
    """
    Class to manage the conversion of XDF streams to SNIRF Nirs objects.
    """
    def __init__(self, xdf_streams, xdf_file_header, snirf_file): 
        """
        Initialize the XdfToSnirfNirs class.

        :param xdf_streams: A list of XDF streams, including NIRS and auxiliary data.
        :param xdf_file_header: Header information from the XDF file.
        :param snirf_file: The target SNIRF file to which the Nirs object will be added.
        """
        self.nirs = snirf.Nirs(snirf_file, conf) #Initialize the SNIRF Nirs object using the specified configuration.
        self.nirs.append(XdfToSnirfNirsElement(xdf_streams, xdf_file_header, snirf_file).NirsElement) #Convert the XDF streams to a SNIRF NirsElement and append it to the Nirs object.


class XdfToSnirf():
    """
    Main class for converting an XDF file containing NIRS data into a SNIRF file.
    """
    def __init__(self, path_to_snirf, path_to_xdf, validate) -> None:
        self.snirf = snirf.Snirf(path_to_snirf)     #Initialize the SNIRF object using the specified path.
        self.snirf.formatVersion = 1.1              #Set the SNIRF format version to 1.1
        xdf_streams, xdf_file_header = pyxdf.load_xdf(path_to_xdf)      #Load the XDF file, retrieving both the streams and file header information.
        self.snirf.nirs = XdfToSnirfNirs(xdf_streams, xdf_file_header, self.snirf).nirs #Convert the XDF streams to a SNIRF Nirs object and assign it to the SNIRF file.
        self.snirf.save() #Save the SNIRF file to disk.
        
        #Validate the SNIRF file if requested.
        if validate:
            print("validating ", path_to_snirf)
            self.result = snirf.validateSnirf(path_to_snirf)
            print(self.result.display())
            read_raw_snirf(path_to_snirf)


conf = snirf.SnirfConfig()

if __name__ == "__main__":
    """
    Command-line interface for the XDF to SNIRF conversion tool.
    """
    parser = argparse.ArgumentParser("XDF to SNIRF Converter",
    """This program takes an XDF file containing a captured LSL NIRS stream 
                    and produces a SNIRF file as output.""")
    parser.add_argument("xdf_file_path", help="Path to the input XDF file.")
    parser.add_argument("save_snirf_path", help="Path to save the output SNIRF file.")
    parser.add_argument("-v", help="validate the created SNIRF file", action="store_true")
    parser.add_argument("-q", help="The will output minimal text to terminal", action="store_true")

    args = parser.parse_args()
    path_to_xdf = args.xdf_file_path
    save_location = args.save_snirf_path
 
    validate = True if args.v else False
    quiet = True if args.q else False


    if quiet:
        # If the quiet mode is enabled (i.e. the user passed the `-q` flag),
        # modify the `get` function to always use `report=False`. Hence reducing logging
        get = partial(get, report=False)

    #Backup the existing SNIRF file if it exists, then remove it.
    if os.path.exists(save_location):
        shutil.copy2(save_location, save_location + ".old")
        os.remove(save_location)
  
    # Convert the XDF file to SNIRF and validate if requested.
    converted_snirf = XdfToSnirf(save_location, path_to_xdf, validate)
