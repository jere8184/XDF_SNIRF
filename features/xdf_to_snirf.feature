Feature: A xdf stream containing 

  Scenario: run a simple test
      Given xdf channels with the following data
      |wavelen|dcs_delay|dcs_width|measure|
      |230.3  | 10000   | 2200    | DCS_g2|
      |222.3  | 10      | 2222    | CW_Amplitud|
      |240.3  | 777     | 2200    | DCS_g2|
      |222.3  | 777     | 2200    | DCS_g2|
      When we convert the channels into snirf measumentLists and probe
      Then the probe and the measumentLists will have the following data
      |probe_wavelen1  | probe_wavelen2| probe_wavelen3|
      |222.3           | 230.3         |  240.3        |


      |measurmentList_datatype|measurmentList_datatypeindex|measurmentList_wavelengthIndex|
      |401                    |3,1                         |2                             |