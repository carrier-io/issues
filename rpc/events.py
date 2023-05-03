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
from pylon.core.tools import web  # pylint: disable=E0611,E0401
from tools import rpc_tools, db
from ..models.events import Event


class RPC:  # pylint: disable=E1101,R0903
    """ RPC Resource """

    @web.rpc("issues_insert_events", "insert_events")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _insert_events(self, data):
        return Event.create(data)

    @web.rpc("issues_save_events", "save_events")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _save_events(self, project_id, data):
        # pruning all project events
        Event.query.filter_by(project_id=project_id).delete()
        
        # saving new events
        events = [Event(**event) for event in data]
        db.session.bulk_save_objects(events)
        db.session.commit()

        # retrieving events list
        events = Event.list(project_id)
        return events

    @web.rpc("issues_list_events", "list_events")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _list_events(self, project_id):
        return Event.list(project_id)

    @web.rpc("issues_update_event", "update_event")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _update_event(self, project_id, id, payload):
        return Event.update(project_id, id, payload)

    @web.rpc("issues_delete_event", "delete_event")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _delete_event(self, project_id, id):
        Event.remove(project_id, id)