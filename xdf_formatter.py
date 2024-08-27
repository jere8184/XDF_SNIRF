from utils import *

class LumoxdfToStandardXdf():
    def __init__(self, lumo_xdf_stream: dict) -> None:
        self.stream =  lumo_xdf_stream
        self.convert_lumo_to_standard_xdf()
    

    def convert_lumo_to_standard_xdf(self):
        self.stream["info"]["desc"][0]["fiducials"] = self.stream["info"]["desc"][0].pop("fiducial")
        self.stream["info"]["desc"][0]["optodes"] = self.stream["info"]["desc"][0].pop("probes")
        self.stream["info"]["desc"][0]["optodes"][0]["optode"] = self.stream["info"]["desc"][0]["optodes"][0].pop("probe")
        
        for optode, location in zip(self.stream["info"]["desc"][0]["optodes"][0]["optode"], self.stream["info"]["desc"][0]["optodes"][0].pop("location")):
            optode["location"] = location
