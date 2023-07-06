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
from typing import Dict, List

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import web  # pylint: disable=E0611,E0401

# from tools import db_tools  # pylint: disable=E0401
from tools import rpc_tools, db  # pylint: disable=E0401
from plugins.issues.utils.logs import log_attachment_create, log_attachment_update, log_attachment_delete

from plugins.issues.models.attachments import Attachment


class RPC:  # pylint: disable=E1101,R0903
    """ RPC Resource """

    @web.rpc("issues_list_ticket_attachments", "list_ticket_attachments")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _list_ticket_attachments(self, project_id, hash_id):
        return Attachment.query.filter_by(project_id=project_id, issue_id=hash_id)

    @web.rpc("issues_add_batch_attachments", "add_batch_attachments")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _add_batch_attachments(self, project_id, attachments:List[Dict]):
        result = []
        try:
            for attach in attachments:
                attachment = Attachment(project_id=project_id, **attach)
                db.session.add(attachment)
                db.session.flush()
                result.append(attachment)
                log_attachment_create(
                    self.context.event_manager,
                    project_id,
                    attach['issue_id'],
                    attachment.id
                )
            db.session.commit()
        except Exception as e:
            log.error(e)
            db.session.rollback()
            return {"ok":False, "error":str(e)}
        
        return {"ok":True, "items":result}

    @web.rpc("issues_update_attachment", "update_attachment")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _update_attachment(self, project_id, id, payload):
        attachment = Attachment.query.filter_by(id=id, project_id=project_id).first()
        if not attachment:
            return {"ok":False, "error":'Not Found'}


        changes = {}
        for field, value in payload.items():
            changes[field] = {
                'old_value': getattr(attachment,field),
                'new_value': value
            }
            if hasattr(attachment, field):
                setattr(attachment, field, value)

        db.session.commit()
        log_attachment_update(
            self.context.event_manager,
            project_id,
            attachment.issue_id,
            id,
            changes,
        )
        return {"ok":True, "item": attachment}

    @web.rpc("issues_delete_attachment", "delete_attachment")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _delete_attachment(self, project_id, id):
        attachment = Attachment.query.filter_by(project_id=project_id, id=id).first()

        if not attachment:
            return {"ok":False, "error":'Not Found'}
        
        db.session.delete(attachment)
        db.session.commit()

        self.context.event_manager.fire_event(
            'issues_attachment_deleted', 
            {'attachment': attachment}
        )
        log_attachment_delete(
            self.context.event_manager,
            project_id,
            attachment.issue_id,
            id,
        )
        return {"ok":True}