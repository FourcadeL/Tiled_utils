# Basic functions to access a tiled .json file

# A Tiled json file is called here a **Tiled_blob**
# A Tiled layer object is called here a **Tiled_layer**
# Tiled objects are a bit weird since their properties can either be embeded in json or found in a model file

# A Tiled object is called here a **Tiled_object**
# A Tiled model is called here a **Tiled_model**


import os
import json
from types import SimpleNamespace
from lxml import objectify


# This defines where the module will search for Tiled_model files
MODELS_DIRECTORIES = "./"


###############################
# XML utils


def get_typed_named_property(xml_properties_node, name):
    """
    Returns the property 'name' in the xml node
    """
    for prop in xml_properties_node.findall('property'):
        if prop.get('name') == name:
            content = prop.get('value')
            match prop.get('type'):
                case "int":
                    return int(content)
                case "bool":
                    return content == "true"
                case _:
                    return content
    raise ValueError(f"XML object does not have the attribute {name}")


###############################
# Tiled utils


def read_tiled_json(input_path: str):
    """
    Reads a Tiled file and returs a Tiled_blob
    """
    with open(input_path, "r") as j_file:
        return json.load(j_file, object_hook=lambda d: SimpleNamespace(**d))


def get_named_layer(tiled_blob, name):
    """
    Returns a Tiled_layer from a Tiled_blob
    By its layer name
    """
    for e in tiled_blob.layers:
        if e.name == name:
            return e
    raise ValueError(f"'{name}' layer not found")


def get_model_property(tiled_model_path, name):
    """
    Returns the property 'name' from
    a Tiled_model
    """
    with open(tiled_model_path, "rb") as f:
        objprop = objectify.fromstring(f.read()).object.properties
        return get_typed_named_property(objprop, name)


def get_named_property(tiled_object, name):
    """
    Returns the property 'name' from
    a Tiled_object
    """
    if hasattr(tiled_object, "properties"):
        for p in tiled_object.properties:
            if p.name == name:
                return p.value
    # not found try searching in model files
    if not hasattr(tiled_object, "template"):
        raise ValueError(f"Object has no property '{name}'")
    model_file = tiled_object.template
    for dir in MODELS_DIRECTORIES:
        try:
            spath = os.path.join(dir, model_file)
            return get_model_property(spath, name)
        except FileNotFoundError:
            pass
    # not found in models either
    raise ValueError(f"Object has no property '{name}'")
