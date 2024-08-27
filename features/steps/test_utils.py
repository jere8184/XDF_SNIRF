
from random import uniform
import numpy as np

def mimic_xdf_meta_data_channel(label="C1", type="Intensity", measure = "Amplitude", source="N1/A",
                                detector="N1/1", wavelen="735.000000", 
                                dcs_width=None, dcs_delay=None, td_order=None, td_width=None, td_delay=None,
                                fd_frequency=None):
    channel = {'label': [label],'type': [type],'measure': [measure],'source': [source],
            'detector': [detector],'wavelen': [wavelen]}
    

    if dcs_width or dcs_delay:
        channel["dcs"] = {}

    if td_delay or td_order or td_width:
        channel["td"] = {}

    if dcs_width:
        channel["dcs"]["width"] = [dcs_width]
    if dcs_delay:
         channel["dcs"]["delay"] = [dcs_delay]
    if td_delay:
        channel["td"]["delay"] = [td_delay]
    if td_order:
        channel["td"]["order"] = [td_order]
    if td_delay:
        channel["td"]["width"] = [td_width]
    if fd_frequency:
         channel["fd"] = {}
         channel["fd"]["frequency"] = [fd_frequency]

    return channel
         
        

    
def mimic_xdf_meta_data_info( name="LUMO HA00030/GA00324", type="NIRS", channel_count="3456", channel_format="float32", source_id="HA00030/GA00324", nominal_srate="6.250000000000000",
                        version="1.100000000000000", created_at="31624682.58859700", uid="7c8192a5-4c27-4ccc-b05a-bddc3d69e1e2", 
                        session_id="default", hostname="DESKTOP-1SMAACB", 
                        v4address=None, v4data_port="16572", v4service_port="16572", v6address=None, v6data_port="16572", v6service_port="16572"):
        
         return {'name': [name], 'type': [type], 'channel_count': [channel_count], 'channel_format': [channel_format], 'source_id': [source_id],
                'nominal_srate': [nominal_srate], 'version': [version], 'created_at': [created_at], 'uid': [uid], 'session_id': [session_id],
                'hostname': [hostname], 'v4address': [v4address], 'v4data_port': [v4data_port], 'v4service_port': [v4service_port],
                'v6address': [v6address], 'v6data_port': [v6data_port], 'v6service_port': [v6service_port]}
        

def mimic_xdf_meta_data(info = mimic_xdf_meta_data_info(), channels = [], fiducials = [], optodes = []):
     desc = [{"channels": [{"channel": channels}], "fiducials": [{"fiducial":fiducials}],  "optodes": [{"optode": optodes}]}]
     info = info
     info["desc"] = desc
     return info


def mimic_xdf_meta_data_optode( label="N1/1", module="N1", function="Detector", location_X= uniform(0, 100), location_Y=uniform(0, 100), location_Z=uniform(0, 100)):
    return {'label': [label], 'module': [module], 'function': [function], 'location': {'X': [location_X],'Y': [location_Y],'Z': [location_Z]}}


def mimic_xdf_meta_data_fiducial( label="Nasion", location_X=uniform(0, 100), location_Y=uniform(0, 100), location_Z=uniform(0, 100)):
    return {'label': [label],'location': { 'X': [location_X], 'Y': [location_Y], 'Z': [location_Z]}}


def mimic_corresponding_optodes(channel):
    source = mimic_xdf_meta_data_optode(label=channel["source"][0], function="Source")
    detector = mimic_xdf_meta_data_optode(label=channel["detector"][0], function="Detector")
    return source, detector


def Generate_Generic_XDF_Data(num_sources, num_detectors, wavelen_1, wavelen_2, num_time_stamps):
    count = 0
    channels = []
    optodes = []
    xdf_data = {}
    for i in range(num_sources):
        for j in range(num_detectors):
            count += 1
            channel_1 = mimic_xdf_meta_data_channel(f"C/{count}", "Intensity", "Amplitude", f"S/{i}", f"D/{j}", wavelen_1)
            channel_2 = mimic_xdf_meta_data_channel(f"C/{count}", "Intensity", "Amplitude", f"S/{i}", f"D/{j}", wavelen_2)
            channels.append(channel_1, channel_2)
    
    for i in range(num_sources):
        optodes.append(mimic_xdf_meta_data_optode(f"S/{i}", None, "Source"))
    
    for i in range(num_detectors):
        optodes.append(mimic_xdf_meta_data_optode(f"D/{i}", None, "Detector"))

    
    info = mimic_xdf_meta_data(channels=channels, optodes=optodes)
    xdf_data["info"] = info

    time_stamps = []
    inital = uniform(100000000000, 0)
    increment = uniform(10, 0.01) 
    for i in range(num_time_stamps):
        time_stamps.append(inital + increment * i)
    
    xdf_data["time_stamps"] = time_stamps

    time_series = []
    for i in range(num_time_stamps):
        time_series.append(np.arange(0, len(channels), uniform(10, 0.001)))
    
    xdf_data["time_series"] = time_series

    return xdf_data



    