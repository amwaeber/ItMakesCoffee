import datetime
import numpy as np


def digital_to_voltage(value=0, bits=10, voltage_range=5.0):
    return (value / 2**bits) * voltage_range


def voltage_to_temperature_thermocouple(voltage=0):
    intrinsic_conversion = 100  # 1V = 100 C
    gain = 6.82
    return voltage * intrinsic_conversion / gain


def voltage_to_temperature(voltage=0, voltage_range=5):  # with 100kOhm thermistor
    serial_resistance = 58
    if voltage <= 0:
        return -1
    try:
        resistance = voltage * serial_resistance / (voltage_range - voltage)
        temperature = - 21.39443 * np.log(resistance) + 123.62807
        return temperature
    except ZeroDivisionError:
        return -1


def voltage_to_power(voltage=0):
    coefficient = 1 / 0.35
    exponent = 1 / 0.09
    if voltage >= 0:
        return (coefficient*voltage)**exponent
    else:
        return -1


def timestamp_to_datetime_hour(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')


def metric_prefix(values, errors=None, label=''):
    errors = list() if errors is None else errors
    prefix_list = ((24, 'Y'), (21, 'Z'), (18, 'E'), (15, 'P'), (12, 'T'), (9, 'G'), (6, 'M'), (3, 'k'), (0, ''),
                   (-3, 'm'), (-6, 'u'), (-9, 'n'), (-12, 'p'), (-15, 'f'), (-18, 'a'), (-21, 'z'), (-24, 'y'))
    val = np.amax(values)
    i = 0
    while i < len(prefix_list):
        if 10 * val // 10**prefix_list[i][0] != 0:
            label = label.split('(')
            if len(label) > 1:
                label.insert(-1, '(%s' % prefix_list[i][1])
            return [value / 10**prefix_list[i][0] for value in values], \
                   [error / 10**prefix_list[i][0] for error in errors], ''.join(label)
        i += 1
    return values, errors, label
