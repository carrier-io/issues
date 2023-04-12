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
import flask
import flask_restful  # pylint: disable=E0401

from pylon.core.tools import log  # pylint: disable=E0611,E0401

from tools import auth  # pylint: disable=E0401
from ...serializers.issue import issue_schema
from ...utils.utils import make_delete_response, make_response


class API(flask_restful.Resource):  # pylint: disable=R0903
    """ API Resource """

    url_params = [
        '<int:project_id>/<string:id>',
        '<int:project_id>/<int:id>',
    ]

    def __init__(self, module):
        self.module = module

    @auth.decorators.check_api(["global_admin"])
    def get(self, project_id, id):
        fn = self.module.get_issue
        return make_response(fn, issue_schema, project_id, id)

    @auth.decorators.check_api(["global_admin"])
    def put(self, project_id, id):
        payload = flask.request.json
        fn = self.module.update_issue
        return make_response(fn, issue_schema, project_id, id, payload)
  
    @auth.decorators.check_api(["global_admin"])
    def delete(self, project_id, id):
        fn = self.module.delete_issue
        return make_delete_response(fn, project_id, id)
