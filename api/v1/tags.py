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
import flask_restful  # pylint: disable=E0401
from tools import auth  # pylint: disable=E0401

from plugins.issues.serializers.issue import tags_schema
from ...utils.utils import make_list_response


class API(flask_restful.Resource):  # pylint: disable=R0903

    url_params = ['<int:project_id>']

    def __init__(self, module):
        self.module = module

    @auth.decorators.check_api(["orchestration_engineer"])
    def get(self, project_id):  # pylint: disable=R0201
        fn = self.module.get_all_tags
        return make_list_response(fn, tags_schema, project_id)