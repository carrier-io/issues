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
from ...serializers.issue import issues_schema


class API(flask_restful.Resource):  # pylint: disable=R0903
    """
        API Resource

        Endpoint URL structure: <pylon_root>/api/<api_version>/<plugin_name>/<resource_name>

        Example:
        - Pylon root is at "https://example.com/"
        - Plugin name is "demo"
        - We are in subfolder "v1"
        - Current file name is "myapi.py"

        API URL: https://example.com/api/v1/demo/myapi

        API resources use check_api auth decorator
        auth.decorators.check_api takes the following arguments:
        - permissions
        - scope_id=1
        - access_denied_reply={"ok": False, "error": "access_denied"},
    """

    url_params = ['<int:project_id>']

    def __init__(self, module):
        self.module = module
        self.rpc = module.context.rpc_manager.call


    def get(self, project_id):  # pylint: disable=R0201
        args = flask.request.args
        if args.get('retrieve_options'):
            return self.module.get_filter_options(project_id, args.getlist('filter_fields[]'))

        total, resp = self.module.get_tickets(project_id, args)
        
        # engagement hash_ids mapping to engagement names
        hash_ids = (issue.engagement for issue in resp)
        names = self.rpc.engagement_get_engagement_names(hash_ids)
        issues = issues_schema.dump(resp)
        for issue in issues:
            name = names.get(issue['engagement'], issue['engagement'])
            issue['engagement'] = {
                'hash_id': issue['engagement'],
                'name': name
            }
    
        return {
            "total": total,
            "rows": issues,
        }