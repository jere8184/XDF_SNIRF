from behave import *
import test_utils
import XDF_TO_SNIRF

@given("xdf channels with the following data")
def step_impl(context):
    context.channels = []
    context.optodes = []
    for i, row in enumerate(context.table):
        channel = test_utils.mimic_xdf_meta_data_channel(label=f"C/{i}", type="Intensity", measure=row["measure"], source=f"S/{i}", detector=f"D/{i}", wavelen=row["wavelen"], dcs_delay=row["dcs_delay"], dcs_width=row["dcs_width"])
        source_optode,  detector_optode = test_utils.mimic_corresponding_optodes(channel)
        context.optodes.append(source_optode)
        context.optodes.append(detector_optode)
        context.channels.append(channel)


@When("we convert the channels into snirf measumentLists and probe")
def step_impl(context):
    context.snirf_probe =  XDF_TO_SNIRF.XdfToSnirfProbe(context.channels, context.optodes).probe
    context.snirf_channels = []
    for channel in context.channels:
        context.snirf_channels.append(XDF_TO_SNIRF.XdfToSnirfMeasurmentListElement(channel, context.snirf_probe).measurmentListElement)

@Then("the probe and the measumentLists will have the following data")
def step_impl(context):
        wavelen1 = context.table[0]["probe_wavelen1"]
        wavelen2 = context.table[0]["probe_wavelen2"]
        wavelen3 = context.table[0]["probe_wavelen3"]
        assert wavelen1; wavelen2; wavelen3 in context.snirf_probe.wavelengths
        for i, measurmentList in enumerate(context.snirf_channels):
            assert measurmentList.dataType == int(context.table[i]["measurmentList_datatype"])
            assert measurmentList.dataTypeIndex[0] == int(context.table[i]["measurmentList_datatypeindex1"])
            assert measurmentList.wavelengthIndex == int(context.table[i]["measurmentList_wavelengthIndex"])



