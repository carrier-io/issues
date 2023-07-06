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

""" RPC """
from typing import Dict

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import web  # pylint: disable=E0611,E0401
# from tools import db_tools  # pylint: disable=E0401
from tools import rpc_tools, db  # pylint: disable=E0401
from plugins.issues.utils.logs import log_comment_create, log_comment_update, log_comment_delete

from plugins.issues.models.comments import Comment


class RPC:  # pylint: disable=E1101,R0903
    """ RPC Resource """

    @web.rpc("issues_list_ticket_comments", "list_ticket_comments")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def list_ticket_comments(self, project_id, issue_id):
        return Comment.query.filter_by(project_id=project_id, issue_id=issue_id).all()

    @web.rpc("issues_add_comment", "add_comment")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def add_comment(self, project_id, payload:Dict):
        try:
            comment = Comment(project_id=project_id, **payload)
            db.session.add(comment)
            db.session.flush()
            db.session.commit()
            log_comment_create(
                self.context.event_manager,
                project_id,
                comment.issue_id,
                comment.id
            )
        except Exception as e:
            log.error(e)
            db.session.rollback()
            return {"ok":False, "error":str(e)}
        
        return {"ok":True, "item":comment}


    @web.rpc("issues_update_comment", "update_comment")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def update_comment(self, project_id, id, payload):
        comment = Comment.query.filter_by(project_id=project_id, id=id).first()
        if not comment:
            return {"ok":False, "error":'Not Found'}

        changes = {}
        for field, value in payload.items():
            changes[field] = {
                'old_value': getattr(comment, field),
                'new_value': value
            }
            if hasattr(comment, field):
                setattr(comment, field, value)

        db.session.commit()
        log_comment_update(
            self.context.event_manager,
            project_id,
            comment.issue_id,
            id,
            changes,
        )
        return {"ok":True, "item": comment}


    @web.rpc("issues_delete_comment", "delete_comment")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def delete_comment(self, project_id, id):
        comment = Comment.query.filter_by(project_id=project_id, id=id).first()
        if not comment:
            return {"ok":False, "error":'Not Found'}
        
        db.session.delete(comment)
        db.session.commit()
        
        log_comment_delete(
            self.context.event_manager,
            project_id,
            comment.issue_id,
            id,
        )
        return {"ok":True}