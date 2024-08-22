from astropy import units as u
import pydash
import array
import numpy

def get(dict_to_search: dict, path: str):
    try:
        value = pydash.get(dict_to_search, path)
        if isinstance(value, dict) or isinstance(value, numpy.ndarray):
            return value
        elif isinstance(value, list):
            if len(value) == 1:
                return value[0]
            else:
                return value
        elif value.lstrip('-+').replace('.','', 1).isnumeric():
            value = float(value)
            if value.is_integer():
                value = int(value) 
        return value              
    except:
        try:
            location, remaining_path  = path.split(".", 1)
            if not remaining_path:
                return None
            value = get(dict_to_search, location)
            if value:
                return get(value, remaining_path)
        except:
            pass
        print(f"{path} not founds")


def get_index(in_list, val):
    try:
        return in_list.index(val)
    except ValueError:
        return None 
    
def try_append(list, val, default: str = None, all = False):
    if all:
        for x in val:
            if not x:
                return
    
    if val:
        list.append(val)
    elif default:
        list.append(default)

def try_add(set, val, default: str = None, all = False):
    if all:
        for x in val:
            if not x:
                return
    if val:
        set.add(val)
    elif default:
        set.add(default)
    

def search(key, var):
    if hasattr(var,'items'): # hasattr(var,'items') for python 3
        for k, v in var.items(): # var.items() for python 3
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in search(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in search(key, d):
                        yield result

def Get_Measure(snirf_data_type):
    match snirf_data_type:
        case 1:
            return "CW_Amplitude"
        case 51:
            return "CW_Fluorescence Amplitude"
        case 101:
            return "FD_AC_Amplitude"
        case 102:    
            return "FD_Phase"
        case 151:
            return "FD_Fluorescence_Amplitude"
        case 152:
            return "FD_Fluorescence_Phase"
        case 201:
            return "TD_Gated_Amplitude"
        case 251:
            return "TD_Gated_Fluorescence_Amplitude"
        case 301:
            return "TD_Moments_Amplitude"
        case 351:
            return "TD_Moments_Fluorescence_Amplitude"
        case 401:
            return "DCS_g2"
        case 410:
            return "BFi"
        case 99999:
            return "Processed"
        
def Get_DataType(measure: str = "", modality: str = ""):
    data_third_digit = "0"
    measure = measure.upper()
    modality = modality.upper()

    if measure.find("AMPLITUDE") != -1 or modality.find("AMPLITUDE") != -1:
        data_third_digit = "1"

    elif measure.find("PHASE") != -1 or modality.find("PHASE") != -1:
        data_third_digit = "2" 
    
    data_second_digit = "0"
    if measure.find("FLUORESCENCE") != -1 or modality.find("FLUORESCENCE") != -1:
        data_second_digit = "5"

    data_first_digit = "0"
    if measure.find("FD") != -1 or modality.find("fd") != -1:
        data_first_digit = "1"

    elif measure.find("TD") != -1 or modality.find("TD") != -1:
        data_first_digit = "2"
        if measure.find("MOMENTS") != -1 or modality.find("MOMENTS") != -1:
            data_first_digit = "3"

    elif measure.find("DCS") != -1 or modality.find("DCS") != -1:
        data_first_digit = "4"

    if measure.find("PROCESSED") != -1 or modality.find("PROCESSED") != -1:
        return 99999

    return int(data_first_digit + data_second_digit + data_third_digit)

def Is_Frequency_Domain(snirf_data_type):
    if snirf_data_type > 100 and snirf_data_type < 201:
        return True
    else:
        return False
    
def Is_Gated_Time_Domain(snirf_data_type):
    if snirf_data_type > 201 and snirf_data_type < 300:
        return True
    else:
        return False
    

def Is_Moment_Time_Domain(snirf_data_type):
    if snirf_data_type > 301 and snirf_data_type < 400:
        return True
    else:
        return False

def Is_DCS(snirf_data_type):
    if snirf_data_type > 401 and snirf_data_type < 500:
        return True
    else:
        return False 

def convert(current_unit, target_unit, value):
    if value:
        current_unit_per_target_unit = u.Unit(current_unit).to(u.Unit(target_unit))
        return value * current_unit_per_target_unit
