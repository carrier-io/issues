#!/usr/bin/python3
# coding=utf-8

#   Copyright 2022 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

""" API """
import flask  # pylint: disable=E0401,W0611
import flask_restful  # pylint: disable=E0401
from tools import auth  # pylint: disable=E0401
from pydantic import ValidationError
from plugins.issues.serializers.event import EventModel
from ...serializers.event import event_schema
from pylon.core.tools import log  # pylint: disable=E0611,E0401
from ...utils.utils import make_response, make_delete_response


class API(flask_restful.Resource):  # pylint: disable=R0903

    url_params = ['<int:project_id>/<int:id>']

    def __init__(self, module):
        self.module = module

    @auth.decorators.check_api(["orchestration_engineer"])
    def put(self, project_id, id):  # pylint: disable=R0201
        payload = flask.request.json
        try:
            event = EventModel(project_id=project_id, **payload)
        except ValidationError as e:
            return {"ok":False, 'error':str(e)}, 400

        fn = self.module.update_event
        return make_response(fn, event_schema, project_id, id, event.dict())


    @auth.decorators.check_api(["orchestration_engineer"])
    def delete(self, project_id, id):
        fn = self.module.delete_event
        return make_delete_response(fn, project_id, id)
