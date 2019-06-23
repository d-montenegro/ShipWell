"""
This module contains all the utility functions to support logic to retrieve temperature from external sources
"""


def translate_from_farenheit_to_celsius(farenheit: float) -> float:
    """
    Translate from Farenheit unit to Celsius unit

    :param farenheit: the value to translate
    :return: the translated value
    """
    return (farenheit - 32) * 5./9.
