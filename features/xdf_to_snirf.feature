Feature: XDF Channels To Snirf Measurment List and Probe

  Scenario: Convert XDF channels containg DCS data to SNIRF
      Given xdf channels populated with the following DCS data
      |wavelen|dcs_delay|dcs_width|measure|
      |230.3  |10000    |2200     |DCS_g2 |
      |222.3  |10       |2222     |DCS_g2 |
      |240.3  |777      |7777     |DCS_g2 |
      |222.3  |777      |2200     |DCS_BFI|
      When we convert the channels into snirf measumentLists and probe
      Then the probe and the measumentLists will contain corresponding DCS data
      |datatype|dcs_delay|wavelen|dcs_width|
      |401     |10000    |230.3  |2200     |
      |401     |10       |222.3  |2222     |
      |401     |777      |240.3  |7777     |
      |410     |777      |222.3  |2200     |

  Scenario: Convert XDF channels containg Gated TD data to SNIRF
      Given xdf channels populated with the following Gated TD data
      |wavelen|td_delay|td_width|measure           |
      |444.333|3332.434|2200.000|TD_Gated_Amplitude|
      |222.3  |1.113399|22224444|TD_Gated_Amplitude|
      |240.3  |777.8866|7777.111|TD_Gated_Amplitude|
      |222.3  |777.8888|2200.333|TD_Gated_Amplitude|
      When we convert the channels into snirf measumentLists and probe
      Then the probe and the measumentLists will contain corresponding Gated TD data
      |datatype|td_delay|wavelen|td_width|
      |201     |3332.434|444.333|2200.000|
      |201     |1.113399|222.3  |22224444|
      |201     |777.8866|240.3  |7777.111|
      |201     |777.8888|222.3  |2200.333|