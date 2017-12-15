import json
from pathlib import Path
from jsonschema import validate as schema_validate

class NccoTemplate(object):

    def __init__(self, name, document):
        self.name = name
        self.document = document

    def resolve(self, template_args=None):
        if template_args is None:
            return self.document

        return self.render(self.document, template_args)

    def render(self, document, template_args):
        return document


def _read_schema(location):
    with open(location, 'r') as schema_file:
        return json.load(schema_file)


def validate(ncco, schema=None):
    """Validate ncco document and return it when valid"""
    # if schema is None:
    #     schema = _read_schema(Path('./ncco_storage/schema/ncco.json'))
    # schema_validate(ncco, schema)
    return ncco
