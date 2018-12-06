""" PytSite ODM HTTP API
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Type as _Type, List as _List, Union as _Union
from inspect import isclass as _isclass
from json import loads as _json_loads, JSONDecodeError as _JSONDecodeError
from pytsite import http as _http, routing as _routing, formatters as _formatters, errors as _errors
from plugins import odm as _odm
from . import _model

_EntityCls = _Union[_Type[_odm.Entity], _Type[_model.HTTPAPIEntityMixin]]
_Entity = _Union[_odm.Entity, _model.HTTPAPIEntityMixin]
_EntityOrCls = _Union[_EntityCls, _Entity]


def _fill_entity_fields(entity: _Entity, fields_data: dict) -> _Entity:
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

    return entity


def _check_api_enabled(o: _EntityOrCls) -> _EntityOrCls:
    if (_isclass(o) and not issubclass(o, _model.HTTPAPIEntityMixin)) or not o.http_api_enabled():
        raise _errors.ForbidOperation('Usage of HTTP API is not allowed for this model')

    return o


def _dispense_entity(ref: str = None, model: str = None) -> _Entity:
    # Load entity
    try:
        entity = _odm.get_by_ref(ref) if ref else _odm.dispense(model)

        if not entity:
            raise _http.error.NotFound('Entity not found')

        if not isinstance(entity, _model.HTTPAPIEntityMixin):
            raise _http.error.Forbidden("Model '{}' does not support transfer via HTTP".format(entity.model))

        return entity

    except _odm.error.ModelNotRegistered as e:
        raise _http.error.NotFound(e)


class GetEntities(_routing.Controller):
    """Get entities
    """

    def __init__(self):
        super().__init__()

        self.args.add_formatter('skip', _formatters.PositiveInt())
        self.args.add_formatter('limit', _formatters.PositiveInt(default=10, maximum=100))
        self.args.add_formatter('refs', _formatters.JSONArrayToList())

    def exec(self) -> _List[dict]:
        try:
            model = self.args.pop('model')
            refs = self.args.pop('refs')
            cls = _check_api_enabled(_odm.get_model_class(model))
            finder = _odm.find(model)

            if refs:
                finder.inc('_ref', refs)

            return cls.http_api_get_entities(finder, self.args)
        except _odm.error.ModelNotRegistered as e:
            raise self.not_found(e)


class GetEntity(_routing.Controller):
    """Get an entity
    """

    def __init__(self):
        """Init
        """
        super().__init__()

        self.args.add_formatter('ref', _formatters.Str())

    def exec(self) -> dict:
        return _check_api_enabled(_dispense_entity(self.args.pop('ref'))).http_api_get_entity(self.args)


class PostEntity(_routing.Controller):
    """Create a new entity
    """

    def __init__(self):
        """Init
        """
        super().__init__()

        self.args.add_formatter('ref', _formatters.Str())

    def exec(self) -> dict:
        entity = _fill_entity_fields(_check_api_enabled(_dispense_entity(model=self.args.pop('model'))), self.args)

        return entity.http_api_post_entity(self.args)


class PatchEntity(_routing.Controller):
    """Update an entity
    """

    def __init__(self):
        """Init
        """
        super().__init__()

        self.args.add_formatter('ref', _formatters.Str())

    def exec(self) -> dict:
        entity = _fill_entity_fields(_check_api_enabled(_dispense_entity(model=self.args.pop('model'))), self.args)

        return entity.http_api_patch_entity(self.args)


class DeleteEntity(_routing.Controller):
    """Delete an entity
    """

    def __init__(self):
        """Init
        """
        super().__init__()

        self.args.add_formatter('ref', _formatters.Str())

    def exec(self) -> dict:
        return _check_api_enabled(_dispense_entity(self.args.pop('ref'))).http_api_delete_entity(self.args)
