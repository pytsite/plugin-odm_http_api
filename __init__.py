"""PytSite ODM HTTP API
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

# Public API
from . import _controllers as controllers
from ._model import HTTPAPIEntityMixin


def plugin_load_wsgi():
    from pytsite import reg

    if reg.get('odm_http_api.enabled'):
        from plugins import http_api
        from . import _controllers

        http_api.handle('GET', 'odm/entities/<model>', _controllers.GetEntities, 'odm_http_api@get_entities')
        http_api.handle('GET', 'odm/entity/<ref>', _controllers.GetEntity, 'odm_http_api@get_entity')
        http_api.handle('POST', 'odm/entity/<model>', _controllers.PostEntity, 'odm_http_api@post_entity')
        http_api.handle('PATCH', 'odm/entity/<ref>', _controllers.PatchEntity, 'odm_http_api@patch_entity')
        http_api.handle('DELETE', 'odm/entity/<ref>', _controllers.DeleteEntity, 'odm_http_api@delete_entity')
