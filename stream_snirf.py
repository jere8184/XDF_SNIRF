import snirf
import pylsl
import utils
import time as t

#load snirf file
snirf_file : snirf.Snirf = snirf.loadSnirf("./sub-01_task-tapping_nirs.snirf", False, True)

class SnirfStreamer:
    def __init__(self, snirf_file : snirf.Snirf):
        self.snirf_file = snirf_file
        self.resulut = self.snirf_file.validate()
        self.snirf_probe: snirf.Probe = snirf_file.nirs[0].probe
        self.snirf_meta_data: snirf.MetaDataTags = snirf_file.nirs[0].metaDataTags
        self.snirf_measurement_list: snirf.MeasurementList = snirf_file.nirs[0].data[0].measurementList
        self.stream_info: pylsl.StreamInfo = pylsl.stream_info("SNIRF_DATA", "NIRS", len(self.snirf_measurement_list))
        self.PopulateStreamInfo()
        self.StreamOverLSL()

    def PopulateStreamInfo(self):
        channels = self.stream_info.desc().append_child("channels")
        for measurement_list in self.snirf_measurement_list:
            channel = channels.append_child("channel")
            self.PopulateChannel(channel, measurement_list)

        optodes = self.stream_info.desc().append_child("optodes")
    
        for i in range(len(self.snirf_probe.sourceLabels)):
            optode = optodes.append_child("optode")
            self.PopulateOptode(optode, True, i)
        
        for i in range(len(self.snirf_probe.detectorLabels)):
            optode = optodes.append_child("optode")
            self.PopulateOptode(optode, False, i)

         
        if self.snirf_probe.landmarkPos3D is not None:
            fiducials = self.stream_info.desc().append_child("fiducials")
            for i in range(len(self.snirf_probe.landmarkPos3D)):
                fiducial = fiducials.append_child("fiducial")
                self.PopulateFiducial(fiducial, i)  
       
        elif self.snirf_probe.landmarkPos2D is not None:
            fiducials = self.stream_info.desc().append_child("fiducials")
            for i in range(len(self.snirf_probe.landmarkPos2D)):
                fiducial = fiducials.append_child("fiducial")
                self.PopulateFiducial(fiducial, i)     

    def PopulateChannel(self, channel: pylsl.XMLElement, measurement_list_element : snirf.MeasurementListElement): 
        #type
        if measurement_list_element.dataTypeLabel:
            channel.append_child_value("type", measurement_list_element.dataTypeLabel)


        #label
        if self.snirf_probe.sourceLabels.any() and self.snirf_probe.detectorLabels.any():
            channel.append_child_value("label",  str(self.snirf_probe.sourceLabels[measurement_list_element.sourceIndex - 1]) 
                                       + "-" + str(self.snirf_probe.detectorLabels[measurement_list_element.detectorIndex - 1]) 
                                       + "-" +  str(self.snirf_probe.wavelengths[measurement_list_element.wavelengthIndex - 1]))
            #source
            channel.append_child_value("source", self.snirf_probe.sourceLabels[measurement_list_element.sourceIndex - 1])

            #detector
            channel.append_child_value("detector", self.snirf_probe.detectorLabels[measurement_list_element.detectorIndex - 1])

        #measure
        channel.append_child_value("measure", utils.Get_Measure(measurement_list_element.dataType))

        #unit
        if measurement_list_element.dataUnit:
            channel.append_child_value("unit", measurement_list_element.dataUnit)


        if hasattr(self.snirf_meta_data, "PowerUnit") and measurement_list_element.sourcePower:
            power = utils.convert(self.snirf_meta_data.PowerUnit, "mw", measurement_list_element.sourcePower)
            channel.append_child_value("power", str(power))

        
        #gain
        if measurement_list_element.detectorGain:
            channel.append_child_value("gain", measurement_list_element.detectorGain)

        #wavelen
        channel.append_child_value("wavelen", str(self.snirf_probe.wavelengths[measurement_list_element.wavelengthIndex - 1]))

        #wavelen_measured
        if measurement_list_element.wavelengthActual:
            channel.append_child_value("wavelen_measured", str(measurement_list_element.wavelengthActual))

        #frequency domain
        #if utils.Is_Frequency_Domain(measurement_list.dataType):
        if  self.snirf_probe.frequencies:
            frequency = str(utils.convert(self.snirf_meta_data.FrequencyUnit, "Hz", self.snirf_probe.frequencies[measurement_list_element.dataTypeIndex]))
            fd = channel.append_child("fd")
            fd.append_child_value("frequency", frequency)

        
        #time domain
       # if utils.Is_Gated_Time_Domain(measurement_list.dataType):
        if self.snirf_probe.timeDelays and self.snirf_probe.timeDelayWidths:
            delay = utils.convert(self.snirf_meta_data.TimeUnit, "ps", self.snirf_probe.timeDelays[measurement_list_element.dataTypeIndex - 1])
            width = utils.convert(self.snirf_meta_data.TimeUnit, "ps", self.snirf_probe.timeDelayWidths[measurement_list_element.dataTypeIndex])

            td = channel.append_child("td")
            td.append_child_value("delay", delay)
            td.append_child_value("width", width)

        #Diffuse Correlation Spectroscopy
        #if utils.Is_DCS(measurement_list.dataType):
        if self.snirf_probe.correlationTimeDelays and self.snirf_probe.correlationTimeDelayWidths:
            delay = utils.convert(self.snirf_meta_data.TimeUnit, "ps", self.snirf_probe.correlationTimeDelays[measurement_list_element.dataTypeIndex])
            width = utils.convert(self.snirf_meta_data.TimeUnit, "ps", self.snirf_probe.correlationTimeDelayWidths[measurement_list_element.dataTypeIndex])

            dcs = channel.append_child("dcs")
            dcs.append_child_value("delay", self.snirf_probe.correlationTimeDelays[measurement_list_element.dataTypeIndex])
            dcs.append_child_value("width", self.snirf_probe.correlationTimeDelayWidths[measurement_list_element.dataTypeIndex])

        
        #fluorescence
        if self.snirf_probe.wavelengthsEmission:
            fluorescence = channel.append_child("fluorescence")
            fluorescence.append_child_value("wavelen", self.snirf_probe.wavelengthsEmission[measurement_list_element.wavelengthIndex])
            fluorescence.append_child_value("wavelen_measured", measurement_list_element.wavelengthEmissionActual)
        
        #illumination?

    def PopulateOptode(self, optode: pylsl.XMLElement, is_source, i):
        postion2D = None
        postion3D = None
        label = None
        if is_source:
            function = "Source"
            if self.snirf_probe.sourceLabels is not None:
                label = self.snirf_probe.sourceLabels[i]
            if self.snirf_probe.sourcePos2D is not None:
                postion2D = self.snirf_probe.sourcePos2D[i]
            else:
                postion3D = self.snirf_probe.sourcePos3D[i]
        else:
            function = "Detector"
            if self.snirf_probe.detectorLabels is not None:
                label = self.snirf_probe.detectorLabels[i]
            if self.snirf_probe.detectorPos2D is not None:
                postion2D = self.snirf_probe.detectorPos2D[i]
            else:
                postion3D = self.snirf_probe.detectorPos3D[i]

        optode.append_child_value("function", function)
        if label:
            optode.append_child_value("label", label)
        
        location = optode.append_child("location")
        if postion2D is not None:
            location.append_child_value("X", str(utils.convert(self.snirf_meta_data.LengthUnit, "mm", postion2D[0])))
            location.append_child_value("Y", str(utils.convert(self.snirf_meta_data.LengthUnit, "mm", postion2D[1])))
        
        if postion3D is not None:
            location.append_child_value("X", str(utils.convert(self.snirf_meta_data.LengthUnit, "mm", postion3D[0])))
            location.append_child_value("Y", str(utils.convert(self.snirf_meta_data.LengthUnit, "mm", postion3D[1])))
            location.append_child_value("Z", str(utils.convert(self.snirf_meta_data.LengthUnit, "mm", postion3D[2])))
    
    def PopulateFiducial(self, fiducial: pylsl.XMLElement, i):
        location = fiducial.append_child("location")
        if self.snirf_probe.landmarkPos2D is not None:
            postions = self.snirf_probe.landmarkPos2D
            location.append_child_value("X", str(utils.convert(self.snirf_meta_data.LengthUnit, "mm", postions[i][0])))
            location.append_child_value("Y", str(utils.convert(self.snirf_meta_data.LengthUnit, "mm", postions[i][1])))
            if len(postions[i]) == 3:
                label = self.snirf_probe.landmarkLabels[postions[i][2]]
                fiducial.append_child_value("label", label)

        else:
            postions = self.snirf_probe.landmarkPos3D
            location.append_child_value("X", str(utils.convert(self.snirf_meta_data.LengthUnit, "mm", postions[i][0])))
            location.append_child_value("Y", str(utils.convert(self.snirf_meta_data.LengthUnit, "mm", postions[i][1])))
            location.append_child_value("Z", str(utils.convert(self.snirf_meta_data.LengthUnit, "mm", postions[i][2])))
            if len(postions[i]) == 4:
                label = self.snirf_probe.landmarkLabels[postions[i][3]]
                fiducial.append_child_value("label", label)

    def StreamOverLSL(self):
        stream_outlet = pylsl.stream_outlet(self.stream_info)
        for data in snirf_file.nirs[0].data[0].dataTimeSeries:
            stream_outlet.push_sample(data)
            t.sleep(0.01)


SnirfStreamer(snirf_file)