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
from typing import List, Dict
# from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import web  # pylint: disable=E0611,E0401
from tools import rpc_tools, db # pylint: disable=E0401
from ..models.issues import Issue



class RPC:  # pylint: disable=E1101,R0903
    """ RPC Resource """

    @web.rpc("issues_get_issue", "get_issue")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_issue(self, project_id, hash_id):
        return Issue.get(project_id, hash_id)

    @web.rpc("issues_delete_issue", "delete_issue")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _delete_issue(self, project_id, hash_id):
        return Issue.remove(project_id, hash_id)

    @web.rpc("issues_filter_present_issues", "filter_present_issues")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _filter_present_issues(self, source, source_ids):
        query = db.session.query(Issue)
        query = query.filter(
            Issue.source_id.in_(source_ids),
            Issue.source_type == source,
        )
        issues = query.all()
        return [issue.source_id for issue in issues]

    @web.rpc("issues_update_issue", "update_issue")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _update_issue(self, project_id, hash_id, payload:dict):    
        issue = Issue.get(project_id, hash_id)
        event_data = get_event_data(project_id, hash_id, payload, issue)
        issue.update_obj(payload)
        self.context.event_manager.fire_event(
            'issues_updated_issue', 
            event_data
        )
        return {"ok": True, "item": issue}

    @web.rpc('issues_set_engagements', "set_engagements")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _set_engagements(self, ids: List[str], engagement_id: str):
        query = db.session.query(Issue).filter(Issue.hash_id.in_(ids))
        query.update({Issue.engagement: engagement_id})
        db.session.commit()
        return {"ok": True}
    
    @web.rpc('issues_filter_issues', 'filter_issues')
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _filter_issues(self, query: Dict[str, object]):
        return Issue.query.filter_by(**query)


# Utility functions
from copy import copy

def get_attr(data, nested_key: str) -> str:
    data = copy(data)
    for key in nested_key.split('.'):
        data = data[key]
    return data


def get_event_data(project_id, hash_id, payload, obj: Issue):
    event_payload = {'project_id': project_id}
    for key in payload.keys():
        event_payload[key] = {
            'old_value': obj.get_field_value(key),
            'new_value': payload[key],
            'id': hash_id,
        }
    return event_payload
