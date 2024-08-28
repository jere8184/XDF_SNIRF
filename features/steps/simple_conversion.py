from behave import *
import test_utils
import XDF_TO_SNIRF
import utils
import random

@given("xdf channels populated with the following DCS data")
def step_impl(context):
    context.channels = []
    context.optodes = []
    for i, row in enumerate(context.table):
        channel = test_utils.mimic_xdf_meta_data_channel(label=f"C/{i}", type="Intensity", measure=row["measure"], source=f"S/{i}", detector=f"D/{i}", wavelen=row["wavelen"], dcs_delay=row["dcs_delay"], dcs_width=row["dcs_width"])
        source_optode,  detector_optode = test_utils.mimic_corresponding_optodes(channel)
        context.optodes.append(source_optode)
        context.optodes.append(detector_optode)
        context.channels.append(channel)

@given("xdf channels populated with the following Gated TD data")
def step_impl(context):
    context.channels = []
    context.optodes = []
    for i, row in enumerate(context.table):
        channel = test_utils.mimic_xdf_meta_data_channel(label=f"C/{i}", type="Intensity", measure=row["measure"], source=f"S/{i}", detector=f"D/{i}", wavelen=row["wavelen"], td_delay=row["td_delay"], td_width=row["td_width"])
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

@Then("the probe and the measumentLists will contain corresponding DCS data")
def step_impl(context):
    for row, measurmentList in zip(context.table, context.snirf_channels):
        assert measurmentList.dataType == int(row["datatype"])
        assert context.snirf_probe.correlationTimeDelays[measurmentList.dataTypeIndex - 1] == utils.convert("ps", "s", float(row["dcs_delay"]))
        assert context.snirf_probe.wavelengths[measurmentList.wavelengthIndex - 1] == float(row["wavelen"])
        assert context.snirf_probe.correlationTimeDelayWidths[measurmentList.dataTypeIndex - 1] == utils.convert("ps", "s", float(row["dcs_width"]))

@Then("the probe and the measumentLists will contain corresponding Gated TD data")
def step_impl(context):
    for row, measurmentList in zip(context.table, context.snirf_channels):
        assert measurmentList.dataType == int(row["datatype"])
        assert context.snirf_probe.timeDelays[measurmentList.dataTypeIndex - 1] == utils.convert("ps", "s", float(row["td_delay"]))
        assert context.snirf_probe.wavelengths[measurmentList.wavelengthIndex - 1] == float(row["wavelen"])
        assert context.snirf_probe.timeDelayWidths[measurmentList.dataTypeIndex - 1] == utils.convert("ps", "s", float(row["td_width"]))



