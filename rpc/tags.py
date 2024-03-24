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
import json
from pylon.core.tools import web, log  # pylint: disable=E0611,E0401
from tools import rpc_tools, db
from ..models.tags import IssueTag
from ..models.issues import Issue
from ..utils.issues import add_issue_tag_line
from ..utils.logs import log_update_issue


class RPC:  # pylint: disable=E1101,R0903
    """ RPC Resource """

    @web.rpc("issues_get_tags", "get_tags")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_tags(self, issue_id):
        return IssueTag.query.filter_by(issue_id=issue_id).all()

    @web.rpc("issues_get_all_tags", "get_all_tags")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_all_tags(self, project_id):
        return IssueTag.query.filter_by(project_id=project_id).all()

    @web.rpc("issues_update_tags", "update_tags")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _update_tags(self, project_id, issue_id, tags):
        issue = Issue.get(project_id, issue_id)
        old_tags = json.dumps([tag.tag for tag in issue.tags])
        new_tags = json.dumps([tag['tag'] for tag in tags])
        changes = {
            'tags': {
                'old_value': old_tags,
                'new_value': new_tags,
            }
        }
        issue.tags.clear()
        for tag in tags:
            add_issue_tag_line(self.context.event_manager, project_id, issue, tag)
        db.session.commit()

        log_update_issue(
            self.context.event_manager, 
            project_id, 
            issue.id, 
            changes
        )

        return issue.tags

    