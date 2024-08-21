from astropy import units as u
import pydash
import traceback


def get(dict_to_search, path: str):
    try:
        value: str = pydash.get(dict_to_search, path)[0]
        if isinstance(value, dict):
            return value
        if value.lstrip('-+').replace('.','', 1).isnumeric():
            value = float(value)
            if value.is_integer():
                value = int(value) 
        return value              
    except:
        try:
            location, new_path  = path.split(".", 1)
            value = get(dict_to_search, location)
            if value:
                return get(value, new_path)
        except:
            pass
        print(f"{path} not founds")


def get_index(in_list, val):
    try:
        return in_list.index(val)
    except ValueError:
        return -1 
    
def try_append(list, val, default = False, all = False):
    if all:
        for x in val:
            if not x:
                return
    
    if val:
        list.append(val)
    elif default:
        list.append(default)

def try_add(set, val):
    if val:
        set.add(val)

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
        
def Get_DataType(xdf_type):
    match xdf_type:
        case "CW_Amplitude":
            return 1
        case "CW_Fluorescence Amplitude":
            return 51
        case "FD_AC_Amplitude":
            return 101
        case "FD_Phase":    
            return 102
        case "FD_Fluorescence_Amplitude":
            return 151
        case "FD_Fluorescence_Phase":
            return 152
        case "TD_Gated_Amplitude":
            return 201
        case "TD_Gated_Fluorescence_Amplitude":
            return 251
        case "TD_Moments_Amplitude":
            return 301
        case "TD_Moments_Fluorescence_Amplitude":
            return 351
        case "DCS_g2":
            return 401
        case "BFi":
            return 410
        case "Processed":
            return 99999

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
    current_unit_per_target_unit = u.Unit(current_unit).to(u.Unit(target_unit))
    return value * current_unit_per_target_unit
