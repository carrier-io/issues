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
from flask import request, make_response, jsonify, g
import flask_restful  # pylint: disable=E0401
from marshmallow.exceptions import ValidationError

# from pylon.core.tools import log  # pylint: disable=E0611,E0401
from tools import auth  # pylint: disable=E0401
from pylon.core.tools import log
from plugins.issues.serializers.comment import comments_schema, comment_schema


class API(flask_restful.Resource):  # pylint: disable=R0903
    """ API Resource """

    url_params = ['<int:project_id>/<int:issue_id>']

    def __init__(self, module):
        self.module = module
        self.rpc = self.module.context.rpc_manager.call


    @auth.decorators.check_api({
        "permissions": ["engagements.issues.comments.view"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": True, "editor": True},
            "default": {"admin": True, "viewer": True, "editor": True},
            "developer": {"admin": True, "viewer": True, "editor": True},
        }})
    def get(self, project_id, issue_id):
        """ Get all comments"""
        comments = self.module.list_ticket_comments(project_id, issue_id)
        comments = comments_schema.dump(comments)
        for comment in comments:
            user = self.rpc.auth_get_user(comment['author_id'])
            comment['email'] = user['email']
            comment['name'] = user['name']
        return {"ok": True, "items":comments}


    @auth.decorators.check_api({
        "permissions": ["engagements.issues.comments.create"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": False, "editor": True},
            "default": {"admin": True, "viewer": False, "editor": True},
            "developer": {"admin": True, "viewer": False, "editor": True},
        }})
    def post(self, project_id, issue_id):
        """ Get all comments"""
        try:
            user = auth.current_user()
            payload = comment_schema.load(request.json)
            payload['issue_id'] = issue_id
            payload['author_id'] = user['id']
        except ValidationError as err:
            messages = getattr(err, 'messages', None)
            return make_response(jsonify({**messages}), 400)

        result = self.module.add_comment(project_id, payload)
        if not result['ok']:
            return result, 400

        result['item'] = comment_schema.dump(result['item'])
        result['item']['email'] = user['email']
        result['item']['name'] = user['name'] 
        return result, 200

