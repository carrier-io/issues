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
from jira import JIRA  # pylint: disable=E0401
from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import web  # pylint: disable=E0611,E0401
from tools import mongo  # pylint: disable=E0401
from ..tools.issues import (
    open_issue,
    reopen_issues,
    add_log_line,
    get_snapshot
)


class Event:  # pylint: disable=E1101,R0903
    """
        Event Resource
    """

    @web.event("issues_added_issue")
    def _issues_added_issue(self, context, event, payload):
        log.info("Event: %s - %s", event, payload)
        snapshot = get_snapshot(self, payload['source'], payload['id'], payload.get('project_id'))
        open_issue(self, snapshot)


    @web.event("issues_bulk_added_issue")
    def _issues_bulk_added_issue(self, context, event, payload):
        # log.info("Event: %s - %s", event, payload)
        
        new_ids = payload.get('new_ids')
        if not new_ids:
            log.info("New vulnerability id list is empty! No issue created")
            return
        
        try:
            closed_issues = mongo.db.issues.find({
                "source.module": payload["source"],
                "source.id": {
                    "$in": new_ids
                    }
                }, 
                {"source.id": 1, "_id":0}
            )
            closed_issues_ids = [issue['source']['id'] for issue in closed_issues]
            new_issues_ids = set(new_ids) - set(closed_issues_ids)

            # creating new issues
            for id in new_issues_ids:
                log.info(f"Creating new issue - {id} - {payload['source']}")
                snapshot = get_snapshot(self, payload['source'], id, payload['project_id'])
                open_issue(self, snapshot)

            # re-open issues
            if closed_issues_ids:
                reopen_issues(payload['source'], closed_issues_ids)

            log.info("Successfully new issues created/re-opened")
        except Exception as e:
            log.error(e)


    @web.event("issues_deleted_issue")
    def _issues_deleted_issue(self, context, event, payload):
        log.info("Event: %s - %s", event, payload)
        #
        add_log_line({
            "source.module": payload["source"],
            "source.id": payload["id"],
        }, "Closing: source vulnerability removed")
        #
        mongo.db.issues.update_one(
            {
                "source.module": payload["source"],
                "source.id": payload["id"],
            },
            {
                "$set": {
                    "status": "Closed",
                    "state.value": "CLOSED_ISSUE",
                    "state.payload": None,
                },
            },
        )
        #
        item = mongo.db.issues.find_one({
            "source.module": payload["source"],
            "source.id": payload["id"],
        })
        if item.get["jira"] != None:
            jira_client = JIRA(
                self.descriptor.config.get("jira_url")[item["jira"]["server"]],
                basic_auth=(
                    self.descriptor.config.get("jira_login"),
                    self.descriptor.config.get("jira_password")
                )
            )
            jira_client.transition_issue(
                item["jira"]["ticket"], "Close",
                comment="Closing: item is no longer present",
                resolution={"name": "Obsolete"}
            )

    @web.event("issues_enagegement_deleted")
    def engagement_deleted(self, context, event, payload):
        log.info("Event: %s - %s", event, payload)
        issues = mongo.db.issues.find({'engagement': payload['engagement']})
        for issue in issues:
            payload = {
                'source': issue['source']['module'],
                'id': issue['source']['id']
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
        #
        events = mongo.db.issue_events.find({
            'field': {
                '$in': fields
            }
        })
        for event in events:
            change_meta = payload[event['field']]
            if change_meta.get('old_value') == event.get('old_value') and \
                change_meta.get('new_value') == event.get('new_value'):
                #
                context.event_manager.fire_event(event['event_name'])
                #
                context.sio.emit("ticket_updated", {
                    "field": event['field'],
                    "old_value": change_meta.get('old_value'),
                    "new_value": change_meta.get('new_value'),
                    "id": change_meta.get('id') 
                })
