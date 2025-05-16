#!/usr/bin/python3
# coding=utf-8

#   Copyright 2025 getcarrier.io
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
import requests
from tools import auth, VaultClient  # pylint: disable=E0401
from pylon.core.tools import log  # pylint: disable=E0611,E0401,W0611


class API(flask_restful.Resource):  # pylint: disable=R0903

    url_params = ['<int:project_id>']

    def __init__(self, module):
        self.module = module
        self.rpc = module.context.rpc_manager.call
        self.event_manager = module.context.event_manager


    @auth.decorators.check_api({
        "permissions": ["engagements.issues.issues.create"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": False, "editor": True},
            "default": {"admin": True, "viewer": False, "editor": True},
            "developer": {"admin": True, "viewer": False, "editor": True},
        }
    })
    def post(self, project_id):
        vault_client = VaultClient.from_project(project_id)
        secrets = vault_client.get_all_secrets()
        data = flask.request.json
        title = data["title"] if "title" in data and data["title"] != "" else None
        if not title:
            return {"ok": False, "description": f"Title should not be empty"}
        elitea_project_id = secrets.get("ELITEA_PROJECT_ID", 592)
        elitea_base_url = secrets.get("ELITEA_BASE_URL", "https://nexus.elitea.ai/api/v1/prompt_lib")
        elitea_token = secrets.get("ELITEA_TOKEN")
        prompt_version = secrets.get("PROMPT_VERSION")
        if not elitea_token:
            return {"ok": False, "description": f"Please add ELITEA_TOKEN to the project secrets"}
        if not prompt_version:
            return {"ok": False, "description": f"Please add PROMPT_VERSION to the project secrets"}

        elitea_headers = {
            'Authorization': f'Bearer {elitea_token}',
            'Accept': '*/*',
            'User-Agent': 'python-requests/2.25.1',
            'Content-Type': 'application/json'
        }
        url = f"{elitea_base_url}/predict/prompt_lib/{elitea_project_id}/{prompt_version}"
        body = {
            "user_input": title,
            "format_response": True
        }
        predict = requests.post(url, json=body, headers=elitea_headers).json()

        response = predict["messages"][0]['content']

        # Ensure `response` is a string; use an empty string if it's None
        response = response if response is not None else ""

        result = {"ok": True, "description": f"{response}"}
        return result, 200
