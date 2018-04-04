# -*- coding: utf-8 -*-

# Redistribution and use in source and binary forms of this file,
# with or without modification, are permitted. See the Creative
# Commons Zero (CC0 1.0) License for more details.

# Temperature Bricklet 2.0 communication config

from commonconstants import THRESHOLD_OPTION_CONSTANTS
from commonconstants import add_callback_value_function

com = {
    'author': 'Olaf Lüke <olaf@tinkerforge.com>',
    'api_version': [2, 0, 0],
    'category': 'Bricklet',
    'device_identifier': 2113,
    'name': 'Temperature V2',
    'display_name': 'Temperature 2.0',
    'manufacturer': 'Tinkerforge',
    'description': {
        'en': 'Measures ambient temperature with 0.1°C accuracy',
        'de': 'Misst Umgebungstemperatur mit 0,1°C Genauigkeit'
    },
    'comcu': True,
    'released': False,
    'documented': False,
    'discontinued': False,
    'packets': [],
    'examples': []
}

temperature_doc = {
'en':
"""
Returns the temperature measured by the sensor. The value
has a range of -4500 to 13000 and is given in °C/100,
i.e. a value of 3200 means that a temperature of 32.00 °C is measured.
""",
'de':
"""
Gibt die gemessene Temperatur des Sensors zurück. Der Wertebereich ist von
-4500 bis 13000 und wird in °C/100 angegeben, z.B. bedeutet
ein Wert von 3200 eine gemessene Temperatur von 32,00 °C.
"""
}

add_callback_value_function(
    packets   = com['packets'],
    name      = 'Get Temperature',
    data_name = 'Temperature',
    data_type = 'int16',
    doc       = temperature_doc
)

