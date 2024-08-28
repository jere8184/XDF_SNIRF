Feature: A xdf stream containing 

  Scenario: run a simple test
      Given xdf channels with the following data
      |wavelen|dcs_delay|dcs_width|measure|
      |230.3  | 10000   | 2200    | DCS_g2|
      |222.3  | 10      | 2222    | CW_Amplitude|
      |240.3  | 777     | 2200    | DCS_g2|
      |222.3  | 777     | 2200    | DCS_BFI|
      When we convert the channels into snirf measumentLists and probe
      Then the probe and the measumentLists will have the following data
      |probe_wavelen1  | probe_wavelen2| probe_wavelen3| |measurmentList_datatype|measurmentList_datatypeindex1|measurmentList_wavelengthIndex|
      |222.3           | 230.3         |  240.3        | |401                    |2                            |2                             |
      |                |               |               | |1                      |0                            |1                             | 
      |                |               |               | |401                    |1                            |3                             |
      |                |               |               | |410                    |1                            |1                             |  

