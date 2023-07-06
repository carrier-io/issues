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
from pylon.core.tools import log  # pylint: disable=E0611,E0401,W0611
from ...serializers.issue import issues_schema, issue_schema
from ...utils.issues import open_issue
from ...utils.utils import get_users
from ...utils.utils import make_create_response, make_delete_response


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
        self.event_manager = module.context.event_manager

    @auth.decorators.check_api({
        "permissions": ["engagements.issues.issues.view"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": True, "editor": True},
            "default": {"admin": True, "viewer": True, "editor": True},
            "developer": {"admin": True, "viewer": True, "editor": True},
        }})
    def get(self, project_id):  # pylint: disable=R0201
        args = flask.request.args
        total, resp = self.module.filter_issues(project_id, args)
        
        # engagement hash_ids mapping to engagement names
        hash_ids = (issue.engagement for issue in resp)
        names = self.rpc.engagement_get_engagement_names(hash_ids)
        issues = issues_schema.dump(resp)
        
        users = get_users()
        for issue in issues:
            name = names.get(issue['engagement'], issue['engagement'])
            issue['engagement'] = {
                'hash_id': issue['engagement'],
                'name': name
            }
            user = users.get(issue['assignee'])
            issue['assignee'] = user
        
        return {
            "total": total,
            "rows": issues,
        }

    @auth.decorators.check_api({
        "permissions": ["engagements.issues.issues.create"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": False, "editor": True},
            "default": {"admin": True, "viewer": False, "editor": True},
            "developer": {"admin": True, "viewer": False, "editor": True},
        }
    })
    def post(self, project_id):
        return make_create_response(
            open_issue, 
            issue_schema, 
            project_id, 
            flask.request.json,
            self.event_manager,
        )
    
    @auth.decorators.check_api({
        "permissions": ["engagements.issues.issues.delete"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": False, "editor": True},
            "default": {"admin": True, "viewer": False, "editor": True},
            "developer": {"admin": True, "viewer": False, "editor": True},
        }
    })
    def delete(self, project_id):
        ids = flask.request.args.getlist('id[]')
        fn = self.module.bulk_delete_issues
        return make_delete_response(
            fn,
            project_id,
            ids
        )
        

