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
from pylon.core.tools import log  # pylint: disable=E0611,E0401
import bson
from pylon.core.tools import web  # pylint: disable=E0611,E0401
from tools import rpc_tools, mongo  # pylint: disable=E0401



class RPC:  # pylint: disable=E1101,R0903
    """ RPC Resource """

    @web.rpc("issues_insert_events", "insert_events")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _insert_events(self, data):
        try:
            mongo.db.issue_events.insert_one(data)
        except Exception as e:
            return {"ok": False, 'error': str(e)}
        return {"ok": True, "item":data}


    @web.rpc("issues_list_events", "list_events")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _list_events(self):
        result_set = mongo.db.issue_events.find({})
        events = []
        for event in result_set:
            events.append(event)
        return events


    @web.rpc("issues_update_event", "update_event")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _update_event(self, id, payload):
        object_id = bson.ObjectId(id)
        payload = {"$set": payload}
        try:
            mongo.db.issue_events.update_one({"_id": object_id}, payload)
        except Exception as e:
            return {"ok":False, "error": str(e)}
        return {'ok': True}


    @web.rpc("issues_delete_event", "delete_event")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _delete_event(self, id):
        object_id = bson.ObjectId(id)
        try:
            mongo.db.issue_events.delete_one({"_id": object_id})
        except Exception as e:
            return {"ok":True, "error":str(e)}
        return {"ok":True}
