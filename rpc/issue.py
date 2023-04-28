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
import operator
from sqlalchemy import and_, or_
from typing import List
from ..utils.utils import delete_attachments_from_minio
from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import web  # pylint: disable=E0611,E0401
from tools import rpc_tools, db # pylint: disable=E0401
from ..models.issues import Issue
from ..models.tags import Tag
from ..models.attachments import Attachment
from ..serializers.attachment import attachments_schema, attachment_schema
from sqlalchemy import func




class RPC:  # pylint: disable=E1101,R0903
    """ RPC Resource """

    @web.rpc("issues_get_issue", "get_issue")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_issue(self, project_id, hash_id):
        return Issue.get(project_id, hash_id)

    @web.rpc("issues_delete_issue", "delete_issue")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _delete_issue(self, project_id, id):
        try:
            attachment = attachment_schema.dump(
                Attachment.query.filter_by(issue_id=id).first()
            )
            Issue.remove(project_id, id)
            Issue.commit()
        except Exception as e:
            log.error(e)
            db.session.rollback()
        else:
            delete_attachments_from_minio(self, attachment)


    @web.rpc("issues_bulk_delete_issues", "bulk_delete_issues")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _bulk_delete_issues(self, project_id, ids):
        attachments = attachments_schema.dump(db.session.query(Attachment).filter(
            Attachment.project_id==project_id,
            Attachment.issue_id.in_(ids)
        ).all())

        query = db.session.query(Issue).filter(
            Issue.project_id==project_id,
            Issue.id.in_(ids)
        )
        query.delete()
        db.session.commit()
        for attachment in attachments:
            delete_attachments_from_minio(self, attachment)

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
        
    
    @web.rpc('issues_get_stats', 'get_stats')
    @rpc_tools.wrap_exceptions(RuntimeError)
    def get_stats(self, project_id, eng_hash):
        query = db.session.query(Issue.id)
        query = query.filter(Issue.project_id==project_id)
        query = query.filter(Issue.engagement==eng_hash) if eng_hash else query
        total = query.count()

        query = db.session.query(Issue.type, func.count(Issue.id).label('count'))
        query = query.filter(Issue.project_id==project_id)
        query = query.filter(Issue.engagement==eng_hash) if eng_hash else query
        types_count = {item[0]:item[1] for item in query.group_by(Issue.type).all()}

        query = db.session.query(Issue.id)
        query = query.filter(Issue.project_id==project_id)
        query = query.filter(Issue.engagement==eng_hash) if eng_hash else query
        done_count = query.filter(Issue.state['value'].astext=="DONE").count()
        in_progress_count = query.filter(Issue.state['value'].astext=='IN_PROGRESS').count()
        state_count = {'done': done_count, 'in_progress': in_progress_count}
        return {'total': total, 'types_count': types_count, 'state_count': state_count}
        


    @web.rpc('issues_filter_issues', 'filter_issues')
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _filter_issues(self, project_id, flask_args):
        args = dict(flask_args)
        limit = args.pop('limit', 10)
        offset = args.pop('offset', 0)
        search = args.pop('search', None)
        sort = args.pop('sort', None)
        order = args.pop('order', None)
        multiselect_filters = ('severity', 'type', 'status', 'source')

        query = db.session.query(Issue).filter(Issue.project_id==project_id)
        for filter_ in multiselect_filters:
            values = flask_args.getlist(filter_)
            if values:
                del args[filter_]
                query = query.filter(and_(
                    getattr(Issue, filter_).in_(values)
                ))
        
        tags = flask_args.getlist('tags')
        if tags:
            tags = [int(x) for x in tags]
            query = query.filter(Issue.tags.any(Tag.id.in_(tags)))
            del args['tags']
        
        if search:
            query = query.filter(or_(
                Issue.title.like(f'%{search}%'),
                Issue.description.like(f'%{search}%'),
                Issue.type.like(f'%{search}%'),
                Issue.source_type.like(f'%{search}%'),
                Issue.status==search,
                Issue.severity==search,
            ))

        filter_ = list()
        for key, value in args.items():
            filter_.append(operator.eq(getattr(Issue, key), value))
        filter_ = and_(*tuple(filter_))

        query = query.filter(filter_)
        total = query.count()

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return total, query.all() 


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
