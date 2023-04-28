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

""" Module """

# import sqlalchemy  # pylint: disable=E0401
from pylon.core.tools import log  # pylint: disable=E0401
from pylon.core.tools import module  # pylint: disable=E0401

from tools import theme  # pylint: disable=E0401
from .utils.db import init_db


class Module(module.ModuleModel):
    """ Pylon module """

    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor

    def init(self):
        """ Init module """
        log.info("Initializing module")
        init_db()
        # Theme registration
        theme.register_subsection(
            "engagements",
            "table", "Tickets",
            title="Tickets",
            kind="slot",
            prefix="issues_table_slot_",
            icon_class="fas fa-server fa-fw",
            weight=1,
            # permissions=["orchestration_engineer"],
        )
        # Init services
        self.descriptor.init_all()
        

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing module")
        # De-init services
        # self.descriptor.deinit_all()
