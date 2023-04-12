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

# from pylon.core.tools import log  # pylint: disable=E0611,E0401,W0611
from marshmallow.exceptions import ValidationError
from ...utils.issues import create_finding_issues, validate_findings
from ...utils.utils import make_list_response
from ...serializers.issue import issues_schema
from pylon.core.tools import log


class API(flask_restful.Resource):  # pylint: disable=R0903
    """
    Finding endpoint
    """

    url_params = ['<int:project_id>']

    def __init__(self, module):
        self.module = module


    def post(self, project_id):  # pylint: disable=R0201
        findings = flask.request.json
        try:
            issues = validate_findings(project_id, findings)
        except ValidationError as e:
            log.info(e)
            return {"ok": False, "error": "Validation error"}, 400
        
        return make_list_response(create_finding_issues, issues_schema, issues)




