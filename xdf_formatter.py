from utils import *

class LumoxdfToStandardxdf():
    def __init__(self, lumo_xdf_stream: dict) -> None:
        self.stream =  lumo_xdf_stream
        self.convert_lumo_to_standard_xdf()
    

    def convert_lumo_to_standard_xdf(self):
        self.stream["info"]["desc"][0]["fiducials"] = self.stream["info"]["desc"][0].pop("fiducial")
        self.stream["info"]["desc"][0]["optodes"] = self.stream["info"]["desc"][0].pop("probes")
        self.stream["info"]["desc"][0]["optodes"][0]["optode"] = self.stream["info"]["desc"][0]["optodes"][0].pop("probe")
        
        for optode, location in zip(self.stream["info"]["desc"][0]["optodes"][0]["optode"], self.stream["info"]["desc"][0]["optodes"][0].pop("location")):
            optode["location"] = location

        a_channels = []
        b_channels = []
        channels = []
        wavelen = self.stream["info"]["desc"][0]["channels"][0]["channel"][0]["wavelen"]
        for channel in self.stream["info"]["desc"][0]["channels"][0].pop("channel"):
            if channel["wavelen"] == wavelen:
                a_channels.append(channel)
            else:
                b_channels.append(channel)
        
        for a_channel, b_channel in zip(a_channels, b_channels):
            channels.append(a_channel)
            channels.append(b_channel)
        
        self.stream["info"]["desc"][0]["channels"][0]["channel"] = channels