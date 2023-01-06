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
from pylon.core.tools import log  # pylint: disable=E0611,E0401,W0611
from tools import auth  # pylint: disable=E0401
from plugins.issues.serializers.event import EventModel


class API(flask_restful.Resource):  # pylint: disable=R0903

    def __init__(self, module):
        self.module = module

    def _handle_ids(self, event: dict):
        event['id'] = str(event.pop('_id'))

    @auth.decorators.check_api(["orchestration_engineer"])
    def get(self):  # pylint: disable=R0201
        events = self.module.list_events()
        for event in events:
            self._handle_ids(event)
        return {"ok":True, "items":events}, 200

    @auth.decorators.check_api(["orchestration_engineer"])
    def post(self):
        payload = flask.request.json
        try:
            event = EventModel(**payload)
        except Exception as e:
            return {"ok":False, 'error':str(e)}, 400
        
        result = self.module.insert_events(event.dict())
        if not result['ok']:
            return result, 400
        self._handle_ids(result['item'])
        return result, 200
