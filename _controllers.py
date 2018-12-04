""" PytSite ODM HTTP API
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import List as _List
from json import loads as _json_loads, JSONDecodeError as _JSONDecodeError
from pytsite import routing as _routing, formatters as _formatters
from plugins import odm as _odm


def _fill_entity_fields(entity: _odm.Entity, fields_data: dict):
    """Helper function
    """
    for field_name, field_value in fields_data.items():
        # Fields to skip
        if field_name.startswith('_') or not entity.has_field(field_name):
            raise RuntimeError("Invalid field: '{}'".format(field_name))

        # Get field
        field = entity.get_field(field_name)

        # Parse JSON values
        if isinstance(field, (_odm.field.List, _odm.field.Dict)):
            if isinstance(field_value, str):
                try:
                    field_value = _json_loads(field_value)
                except _JSONDecodeError as e:
                    raise RuntimeError("JSON decoding error at field '{}': {}".format(field_name, e))
            else:
                raise RuntimeError("JSON decoding error at field '{}'".format(field_name))

        # Set field's value
        try:
            entity.f_set(field_name, field_value)
        except (TypeError, ValueError) as e:
            raise RuntimeError("Invalid format of the field '{}': {}".format(field_name, e))


class GetEntities(_routing.Controller):
    """Get entities
    """

    def __init__(self):
        super().__init__()

        self.args.add_formatter('skip', _formatters.PositiveInt())
        self.args.add_formatter('limit', _formatters.PositiveInt(default=10, maximum=100))

    def exec(self) -> _List[dict]:
        model = self.args.pop('model')
        mock = _odm.dispense(model)

        # Check entity's class
        try:
            if not hasattr(mock, 'http_api_get'):
                raise self.forbidden("Model '{}' does not support transfer via HTTP".format(model))
        except _odm.error.ModelNotRegistered as e:
            raise self.not_found(e)

        # Create finder
        f = _odm.find(model)

        # Alter finder
        if hasattr(mock, 'http_api_finder'):
            mock.http_api_finder(f, **dict(self.args))

        # Build response
        r = []
        for entity in f.skip(self.args.pop('skip')).get(self.args.pop('limit')):
            r.append(entity.http_api_get(**dict(self.args)))

        return r


class GetEntity(_routing.Controller):
    """Get an entity
    """

    def __init__(self):
        super().__init__()

        self.args.add_formatter('ref', _formatters.Str())

    def exec(self) -> dict:
        # Load entity
        try:
            entity = _odm.get_by_ref(self.args.pop('ref'))
        except _odm.error.ModelNotRegistered as e:
            raise self.not_found(e)
        if not entity:
            raise self.not_found('Entity not found')

        # Check for entity's class
        if not hasattr(entity, 'http_api_get'):
            raise self.forbidden("Model '{}' does not support transfer via HTTP".format(entity.model))

        return entity.http_api_get(**dict(self.args))


class PostEntity(_routing.Controller):
    """Create a new entity
    """

    def exec(self) -> dict:
        # Dispense new entity
        try:
            entity = _odm.dispense(self.args.pop('model'))
        except _odm.error.ModelNotRegistered as e:
            raise self.not_found(e)

        # Check entity's class
        if not hasattr(entity, 'http_api_get'):
            raise self.forbidden("Model '{}' does not support transfer via HTTP".format(entity.model))

        # Fill entity's fields with values
        _fill_entity_fields(entity, self.args)

        # Call entity's hook
        if hasattr(entity, 'http_api_post'):
            entity.http_api_post(**dict(self.args))

        # Save entity
        entity.save()

        return entity.http_api_get(**dict(self.args))


class PatchEntity(_routing.Controller):
    """Update an entity
    """

    def exec(self) -> dict:
        # Load entity
        try:
            entity = _odm.get_by_ref(self.args.pop('ref'))
        except _odm.error.ModelNotRegistered as e:
            raise self.not_found(e)
        if not entity:
            raise self.not_found('Entity not found')

        # Check entity's class
        if not hasattr(entity, 'http_api_get'):
            raise self.forbidden("Model '{}' does not support transfer via HTTP".format(entity.model))

        # Fill fields with values and save
        _fill_entity_fields(entity, self.args)

        # Call entity's hook
        if hasattr(entity, 'http_api_patch'):
            entity.http_api_patch(**dict(self.args))

        # Save entity
        entity.save()

        return entity.http_api_get(**dict(self.args))


class DeleteEntity(_routing.Controller):
    """Delete an entity
    """

    def exec(self) -> dict:
        # Load entity
        try:
            entity = _odm.get_by_ref(self.args.pop('ref'))
        except _odm.error.ModelNotRegistered as e:
            raise self.not_found(e)
        if not entity:
            raise self.not_found('Entity not found')

        # Check entity's class
        if not hasattr(entity, 'http_api_get'):
            raise self.forbidden("Model '{}' does not support transfer via HTTP".format(entity.model))

        # Call entity's hook
        if hasattr(entity, 'http_api_delete'):
            entity.http_api_delete(**dict(self.args))

        # Delete entity
        entity.delete()

        return {'status': True}
