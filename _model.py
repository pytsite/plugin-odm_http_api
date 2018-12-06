"""ODM HTTP API Entity Models
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import List as _List
from pytsite import routing as _routing
from plugins import odm as _odm


class HTTPAPIEntityMixin:
    @classmethod
    def http_api_enabled(cls) -> bool:
        return False

    @classmethod
    def http_api_get_entities(cls, finder: _odm.Finder, args: _routing.ControllerArgs) -> _List[dict]:
        """Called by 'odm_http_api@get_entities' route
        """
        r = []
        for entity in finder.skip(args.pop('skip')).get(args.pop('limit')):  # type: HTTPAPIEntityMixin
            r.append(entity.http_api_get_entity(args))

        return r

    def http_api_get_entity(self, args):
        """Called by 'odm_http_api@get_entity' route

        :type self: _odm.Entity | HTTPAPIEntityMixin
        :type args: _routing.ControllerArgs
        """
        return self.as_jsonable(**dict(args))

    def http_api_post_entity(self, args):
        """Called by 'odm_http_api@post_entity' route

        :type self: _odm.Entity | HTTPAPIEntityMixin
        :type args: _routing.ControllerArgs
        """
        return self.save().as_jsonable(**dict(args))

    def http_api_patch_entity(self, args):
        """Called by 'odm_http_api@patch_entity' route

        :type self: _odm.Entity | HTTPAPIEntityMixin
        :type args: _routing.ControllerArgs
        """
        self.save().as_jsonable(**dict(args))

    def http_api_delete_entity(self, args):
        """Called by 'odm_http_api@delete_entity' route

        :type self: _odm.Entity | HTTPAPIEntityMixin
        :type args: _routing.ControllerArgs
        """
        self.delete()

        return {'status': True}
