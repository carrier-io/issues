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
from flask import request, url_for
from werkzeug.utils import secure_filename
from plugins.issues.utils.utils import make_unique_filename
import flask_restful  # pylint: disable=E0401

from pylon.core.tools import log

from tools import auth, api_tools, minio_client  # pylint: disable=E0401
from plugins.issues.serializers.attachment import attachments_schema
from plugins.issues.utils.utils import generate_thumbnail


class API(flask_restful.Resource):  # pylint: disable=R0903
    """ API Resource """

    url_params = ['<int:project_id>/<int:issue_id>']

    def __init__(self, module):
        self.module = module


    @auth.decorators.check_api(['global_admin'])
    def get(self, project_id, issue_id):
        """ Get all attachments"""
        attachments = self.module.list_ticket_attachments(project_id, issue_id)
        attachments = attachments_schema.dump(attachments)
        return {"ok": True, "items":attachments}


    @auth.decorators.check_api(['global_admin'])
    def post(self, project_id, issue_id):
        """ Get all attachments"""

        files = request.files.getlist("files[]")
        if not files:
            return {"ok":False, "error": "Empty payload"}

        project = self.module.context.rpc_manager.call.project_get_or_404(project_id=project_id)
        client = minio_client.MinioClient(project)
        
        attachments = []
        for file in files:
            bucket = "issue-attachments"
            original_name = file.filename
            file.filename = make_unique_filename(secure_filename(file.filename))
            project = self.module.context.rpc_manager.call.project_get_or_404(project_id=project_id)
            api_tools.upload_file(bucket, file, project, create_if_not_exists=True)
            
            # thumbnail
            try:
                thumb_file_name, thumb_file_obj = generate_thumbnail(file)
                client.upload_file(bucket, thumb_file_obj, thumb_file_name)
                thumbnail_url = url_for(
                    'api.v1.artifacts.artifact', 
                    project_id=project_id,
                    bucket=bucket,
                    filename=thumb_file_name,
                    _external=True,
                )
            except IOError:
                thumbnail_url = None

            
            attachments.append({
                'file_name': original_name,
                'url': url_for(
                    'api.v1.artifacts.artifact', 
                    project_id=project_id, 
                    bucket=bucket, 
                    filename=file.filename, 
                _external=True),
                'thumbnail_url': thumbnail_url,
                'issue_id':issue_id,
            })

        result = self.module.add_batch_attachments(project_id, attachments)
        if not result['ok']:
            return result, 400
        
        result['items'] = attachments_schema.dump(result['items'])
        return result, 200

