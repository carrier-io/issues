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
from tools import rpc_tools
from ..models.tags import Tag
from ..models.logs import Log


class RPC:  # pylint: disable=E1101,R0903
    """ RPC Resource """

    @web.rpc("issues_get_tags", "get_tags")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_tags(self, issue_id):
        return Tag.query.filter_by(issue_id=issue_id).all()

    
    @web.rpc("issues_get_logs", "get_logs")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def _get_logs(self, issue_id):
        return Log.query.filter_by(issue_id=issue_id).all()