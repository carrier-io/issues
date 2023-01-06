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
import uuid
from typing import List, Dict
from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import web  # pylint: disable=E0611,E0401
from tools import rpc_tools, mongo  # pylint: disable=E0401



class RPC:  # pylint: disable=E1101,R0903
    """ RPC Resource """


    @web.rpc("issues_get_issue", "get_issue")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_issue(self, hash_id):
        result = {"ok": True}
        try:
            resp = mongo.db.issues.find_one({'id': uuid.UUID(hash_id)}, {'_id':0})
            log.info(resp)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        
        if not resp:
            return {"ok":False, "error": "Not Found"}

        result['item'] =  resp
        return result
            

    @web.rpc("issues_delete_issue", "delete_issue")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _delete_issue(self, hash_id):
        result = {'ok': True}
        try:
            resp = mongo.db.issues.delete_one({
                "id": uuid.UUID(hash_id)
            })
        except Exception as e:
            result['ok'] = False
            result['error'] = str(e)
            return result
        
        if resp.deleted_count == 0:
            result['ok'] = False
            result['error'] = 'Not Found'
        return result 



    @web.rpc("issues_filter_present_issues", "filter_present_issues")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _filter_present_issues(self, source, ids):
        issues = mongo.db.issues.find({
            "source.module": source,
            "source.id": {
                "$in": ids
                }
            }, 
            {"source.id": 1, "_id":0}
        )
        return [issue['source']['id'] for issue in issues]

    @web.rpc("issues_update_issue", "update_issue")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _update_issue(self, id, payload):
        issue = mongo.db.issues.find_one({"id": uuid.UUID(id)})
        if not issue:
            return {'ok':False, 'error': "Not found"}

        query = {"$set": payload}
        response = mongo.db.issues.update_one({"id": uuid.UUID(id)}, query)
        modified = response.modified_count > 0
        output = {'ok': True if modified else False}
        
        event_payload = {}
        for key in payload.keys():
            event_payload[key] = {
                'old_value': get_attr(issue, key),
                'new_value': payload[key],
                'id': id,
            }           
        #
        self.context.event_manager.fire_event(
            'issues_updated_issue',
            event_payload
        )
        #
        return output

    
    @web.rpc('issues_set_engagements', "set_engagements")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _set_engagements(self, ids: List[str], engagement_id: str):
        ids = [uuid.UUID(id) for id in ids]
        filter = {"id": {"$in": ids}}
        query = {"$set": {"engagement": engagement_id}}
        response = mongo.db.issues.update_many(filter, query)
        modified = response.modified_count > 0
        output = {"ok": True if modified else False}
        return output
    

    @web.rpc('issues_filter_issues', 'filter_issues')
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _filter_issues(self, query: Dict[str, object]):
        try:
            result = mongo.db.issues.find(query)
        except Exception as e:
            return {"ok": False, "error": str(e)}

        issues = []
        for issue in result:
            issue.pop('_id')
            issue['id'] = str(issue['id'])
            issues.append(issue)

        return {"ok": True, "items": issues}




# Utility functions
from copy import copy

def get_attr(data, nested_key: str) -> str:
    data = copy(data)
    for key in nested_key.split('.'):
        data = data[key]
    return data
