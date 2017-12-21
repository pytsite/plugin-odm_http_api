"""PytSite ODM HTTP API
"""

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def _register_assetman_resources():
    from plugins import assetman

    if not assetman.is_package_registered(__name__):
        assetman.register_package(__name__)
        assetman.t_js(__name__)
        assetman.js_module('odm-http-api', __name__ + '@odm-http-api')

    return assetman


def plugin_install():
    _register_assetman_resources().build(__name__)


def plugin_load():
    _register_assetman_resources()


def plugin_load_uwsgi():
    from plugins import http_api
    from . import _controllers

    http_api.handle('GET', 'odm/entities/<model>', _controllers.GetEntities, 'odm_http_api@get_entities')
    http_api.handle('POST', 'odm/entity/<model>', _controllers.PostEntity, 'odm_http_api@post_entity')
    http_api.handle('GET', 'odm/entity/<model>/<uid>', _controllers.GetEntity, 'odm_http_api@get_entity')
    http_api.handle('PATCH', 'odm/entity/<model>/<uid>', _controllers.PatchEntity, 'odm_http_api@patch_entity')
    http_api.handle('DELETE', 'odm/entity/<model>/<uid>', _controllers.DeleteEntity, 'odm_http_api@delete_entity')
