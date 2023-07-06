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

""" Slot """
from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import web  # pylint: disable=E0611,E0401
from tools import db, MinioClient  # pylint: disable=E0401
from ..utils.issues import (
    open_issue,
    reopen_issues,
    get_snapshot
)
from ..utils.logs import log_update_issue
from ..models.events import Event as EventModel
from ..models.issues import Issue


class Event:  # pylint: disable=E1101,R0903
    """
        Event Resource
    """

    @web.event("issues_attachment_deleted")
    def _issues_attachment_deleted(self, context, event, payload):
        attachment = payload['attachment']
        if not attachment:
            return
        
        for field in ('url', 'thumbnail_url'):
            filename = getattr(attachment, field).split('/')[-1]
            bucket = getattr(attachment, field).split('/')[-2]
            project_id = attachment.project_id
            project = context.rpc_manager.call.project_get_or_404(project_id=project_id)
            client = MinioClient(project)
            client.remove_file(bucket, filename)

    @web.event("issues_added_issue")
    def _issues_added_issue(self, context, event, payload):
        log.info("Event: %s - %s", event, payload)
        project_id = payload.get('project_id')
        snapshot = get_snapshot(self, payload['source'], payload['id'])
        open_issue(project_id, snapshot, context.event_manager)

    @web.event("issues_bulk_added_issue")
    def _issues_bulk_added_issue(self, context, event, payload):
        # log.info("Event: %s - %s", event, payload)
        
        new_ids = payload.get('new_ids')
        if not new_ids:
            log.info("New vulnerability id list is empty! No issue created")
            return
        
        try:
            user = payload['user']
            closed_issues_ids = self.filter_present_issues(payload["source"], new_ids)
            new_issues_ids = set(new_ids) - set(closed_issues_ids)
            # creating new issues
            for id in new_issues_ids:
                log.info(f"Creating new issue - {id} - {payload['source']}")
                snapshot = get_snapshot(self, payload['source'], id)
                with self.context.app.app_context():
                    open_issue(payload['project_id'], snapshot, context.event_manager, user)

            # re-open issues
            if closed_issues_ids:
                with self.context.app.app_context():
                    reopen_issues(payload['source'], closed_issues_ids, context.event_manager, user)

            log.info("Successfully new issues created/re-opened")
        except Exception as e:
            log.error(e)

    @web.event("issues_deleted_issue")
    def _issues_deleted_issue(self, context, event, payload):
        log.info("Event: %s - %s", event, payload)
        #
        issue = Issue.query.filter_by(
            source_type=payload['source'],
            source_id=payload['id']
        ).first()
        project_id = issue.project_id
        changes = {
            'state.value': {
                'old_value': issue.state['value'],
                'new_value': "CLOSED_ISSUE",
            },
            'state.payload': {
                'old_value': issue.state['payload'],
                'new_value': None,
            },
            'status': {
                'old_value': issue.status,
                'new_value': 'closed'
            }
        }
        
        issue.status = "closed"
        issue.state['value'] = "CLOSED_ISSUE"
        issue.state['payload'] = None
        db.session.commit()
        with self.context.app.app_context():
            user = payload['user']
            log_update_issue(self.context.event_manager, project_id, issue.id, changes, user)

    @web.event("issues_enagegement_deleted")
    def engagement_deleted(self, context, event, payload):
        log.info("Event: %s - %s", event, payload)
        issues: list[Issue] = self.context.rpc_manager\
            .call.issues_filter_issues({'engagement': payload['engagement']})
        for issue in issues:
            payload = {
                'source': issue.source_type,
                'id': issue.source_id
            }
            Event._issues_deleted_issue(self, context, 'issues_deleted_issue', payload)

    @web.event("issues_updated_issue")
    def issue_updated(self, context, event, payload):
        '''
            payload = {
                '<field>':{
                    'old_value':'a'
                    'new_value':'b'
                }
                ...
            }
        '''
        
        log.info("Event: %s - %s", event, payload)
        #
        fields = list(payload.keys())
        project_id = payload['project_id']
        #
        events = EventModel.list_events_of_fields(project_id, fields)
        #
        for event in events:
            change_meta = payload[event.field]
            if change_meta.get('old_value') == event.values.get('old_value') and \
                change_meta.get('new_value') == event.values.get('new_value'):
                #
                context.event_manager.fire_event(event.event_name)
                #
                context.sio.emit("ticket_updated", {
                    "field": event.field,
                    "old_value": change_meta.get('old_value'),
                    "new_value": change_meta.get('new_value'),
                    "id": change_meta.get('id') 
                })