def digital_to_voltage(value=0, bits=10, voltage_range=5):
    return value / (2**bits-1) * voltage_range


def voltage_to_temperature(voltage=0):
    intrinsic_conversion = 100  # 1V = 100 C
    gain = 6.82
    return voltage * intrinsic_conversion / gain


def voltage_to_power(voltage=0):
    coefficient = 1 / 0.35
    exponent = 1 / 0.09
    return (coefficient*voltage)**exponent
