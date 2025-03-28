"""
This module provides functions to anonymize DICOM datasets.

Functions:
    generate_unique_uid(uid=None): Generates a unique UID.
    empty_value(tag): Returns an empty value for a given DICOM tag.
    hash_value(tag): Returns a hashed value for a given DICOM tag.
    change_value(tag, new_value): Changes the value of a given DICOM tag.
    string_to_tag(tag_str): Converts a string representation of a DICOM tag to a Tag object.
    anonymize_dicom(ds, anonymization_config): Anonymizes a DICOM dataset based on the provided 
                                               configuration.
"""

import hashlib
import pydicom
from pydicom.tag import Tag
from pydicom.datadict import keyword_for_tag


def generate_unique_uid(uid=None):
    """
    Generates a unique UID.

    Args:
        uid (str, optional): A string to use as the entropy source for generating the UID. Defaults to None.

    Returns:
        str: A unique UID.
    """
    if uid is None:
        return pydicom.uid.generate_uid()
    else:
        return pydicom.uid.generate_uid(prefix="1.2.826.0.1.", entropy_srcs=uid)


def empty_value(tag):
    """
    Returns an empty value for a given DICOM tag.

    Args:
        tag (pydicom.DataElement): The DICOM tag.

    Returns:
        Any: The empty value for the tag.
    """
    return tag.empty_value


def hash_value(tag):
    """
    Returns a hashed value for a given DICOM tag.

    Args:
        tag (pydicom.DataElement): The DICOM tag.

    Returns:
        str: The hashed value for the tag.
    """
    value = tag.value
    VR = tag.VR

    if value == '':
        return ''

    v = hashlib.sha256(value.encode()).hexdigest()

    if VR == 'SH':
        return v[:16]
    elif VR in ['AE', 'CS', 'LT']:
        return v[:16]
    elif VR == 'DA':
        return '19000101'
    elif VR == 'DA':  # YYYYMMDDHHMMSS.FFFFFF
        return '19000101000000'
    elif VR == 'AS':
        return v[:4]
    elif VR == 'UI':
        return generate_unique_uid(value)
    elif VR == 'PN':
        return 'ANON_' + v[:4]
    elif VR == 'LO':
        return v
    else:
        raise ValueError()


def change_value(tag, new_value):
    """
    Changes the value of a given DICOM tag.

    Args:
        tag (pydicom.DataElement): The DICOM tag.
        new_value (Any): The new value for the tag.

    Returns:
        Any: The new value for the tag.
    """
    return new_value


def string_to_tag(tag_str):
    """
    Converts a string representation of a DICOM tag to a Tag object.

    Args:
        tag_str (str): The string representation of the DICOM tag.

    Returns:
        pydicom.tag.Tag: The Tag object.
    """
    # Remove parentheses and split by hyphen
    group, element = tag_str.strip("()").split("-")
    # Convert hexadecimal strings to integers
    group_int = int(group, 16)
    element_int = int(element, 16)
    # Create and return a Tag object
    return Tag(group_int, element_int)


def anonymize_dicom(ds, anonymization_config):
    """
    Anonymizes a DICOM dataset based on the provided anonymization configuration.

    Args:
        ds (pydicom.Dataset): The DICOM dataset to anonymize.
        anonymization_config (dict): A dictionary specifying how to handle each DICOM tag.

    Returns:
        pydicom.Dataset: The anonymized DICOM dataset.
    """
    # Apply firmlab_dicom_anonymizer rules
    for tag_id, action in anonymization_config.items():
        # tag is a string "(0002-0003)", transform in int
        tag = string_to_tag(tag_id)
        if tag in ds:
            if action == 'X':
                del ds[tag]  # Remove the tag
            elif action == 'Z':
                ds[tag].value = empty_value(ds[tag])  # Keep the tag, but empty the value
            elif action == 'D':
                try:
                    ds[tag].value = hash_value(ds[tag])  # Create a hash value
                except Exception as e:
                    print(f'Could not hash tag {tag}: {e}')
            elif action.startswith('C:'):
                new_value = action.split(':')[1]
                ds[tag].value = new_value  # change_value(ds[tag], new_value)
            elif action == 'U':
                try:
                    ds[tag].value = generate_unique_uid(ds[tag].value)  # Replace with unique UID
                except TypeError:
                    print(f'Could not generate a unique UID for tag {tag}')
    return ds
