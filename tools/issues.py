import uuid
from jira import JIRA  # pylint: disable=E0401
from tools import mongo  # pylint: disable=E0401
from pylon.core.tools import log  # pylint: disable=E0611,E0401


def add_log_line(issue_id_uuid, log_line):
    """ Tool """
    mongo.db.issues.update_one(
        {"id": issue_id_uuid},
        {
            "$push": {
                "log": log_line,
            },
        },
    )


def add_tag(issue_id_uuid, tag):
    """ Tool """
    mongo.db.issues.update_one(
        {"id": issue_id_uuid},
        {
            "$push": {
                "tags": tag,
            },
        },
    )


def set_state(issue_id_uuid, state, payload=None):
    """ Tool """
    mongo.db.issues.update_one(
        {"id": issue_id_uuid},
        {
            "$set": {
                "state.value": state,
                "state.payload": payload,
            },
        },
    )


def reopen_issues(source_type, issue_ids: list):
    log.info(f"Re-opening issues - {issue_ids} - {source_type}")
    mongo.db.issues.update_many(
        {
            "source.module": source_type,
            "source.id": {
                "$in": issue_ids
            }
        },
        {
            "$set": {
                "status": "Open",
                "state.value": "NEW_ISSUE",
                "state.payload": None,
            },
        }
    )


def prepare_issue(payload: dict):
    source_type = payload.pop('source_type', None)
    issue_id = payload.pop('issue_id', None)
    report_id = payload.pop("report_id", None)
    engagement = payload.pop('engagement', None)
    centry_project_id = payload.pop('centry_project_id', None)
    data = {
        "id": uuid.uuid4(),
        "source": {
            "module": source_type,
            "id": issue_id,
        },
        "report_id": report_id,
        "snapshot": payload,
        "severity": payload.get("severity"),
        "project": payload.get("project"),
        "asset": payload.get("asset"),
        "type": payload.get("type"),
        "status": "Open",
        "state": {
            "value": "NEW_ISSUE",
            "payload": None,
        },
        "tags": [],
        "engagement": engagement,
        "centry_project_id": centry_project_id,
        "comments": [],
        "attachments": [],
        "jira": None,
        "log": [],
    }
    return data


def insert_issue(payload) -> dict:
    data = prepare_issue(payload)
    mongo.db.issues.insert_one(data)
    return data


def create_jira_ticket(self, issue_data):
    #
    jira_mapping = self.context.rpc_manager.call.system_get_jira_mapping()
    # log.info("JIRA mapping: %s", jira_mapping)
    #
    priority_map = {
        "Critical": "Critical",
        "High": "Major",
        "Medium": "Medium",
        "Low": "Minor",
        "Info": "Trivial",
    }
    #
    item = issue_data
    #
    if item["project"] not in jira_mapping:
        add_log_line(
            item["id"],
            f"JIRA ticket creation failed: no JIRA mapping for {item['project']}",
        )
        add_tag(item["id"], "Action required")
        add_tag(item["id"], "Failed on JIRA ticket creation")
        set_state(item["id"], "TICKET_CREATION_FAILED")
        return
    #
    jira_map = jira_mapping.get(item["project"])
    jira_client = JIRA(
        self.descriptor.config.get("jira_url")[jira_map["jira"]],
        basic_auth=(
            self.descriptor.config.get("jira_login"),
            self.descriptor.config.get("jira_password")
        )
    )
    #
    fields_data = {
        "project": {"key": jira_map["jira_project"]},
        "issuetype": "Bug",
        "summary": item["snapshot"]["title"],
        "description": item["snapshot"]["description"],
        "priority": {"name": priority_map[item["severity"]]},
        "customfield_14500": jira_map["jira_epic"],
    }
    ticket = jira_client.create_issue(fields=fields_data)
    #
    mongo.db.issues.update_one(
        {"id": item["id"]},
        {
            "$set": {
                "jira": {
                    "server": jira_map["jira"],
                    "ticket": str(ticket.key),
                },
            },
        },
    )
    #
    add_log_line(
        item["id"],
        f"Created JIRA ticket: {jira_map['jira']}:{str(ticket.key)}",
    )
    #
    set_state(item["id"], "TICKET_CREATED")


def get_snapshot(module, source_type, issue_id, project_id=None):
    snapshot_rpc = getattr(
        module.context.rpc_manager.call,
        f'{source_type}__get_issue_snapshot',
    )
    snapshot = snapshot_rpc(issue_id)
    snapshot['source_type'] = source_type
    snapshot['issue_id'] = issue_id
    snapshot['centry_project_id'] = project_id
    return snapshot


def open_issue(snapshot):
    insert_issue(snapshot)


def search_issue(hash_id):
    result = mongo.db.issues.find(
        {
            'status': 'Open',
            'source.id': hash_id
        }
    )
    return bool(tuple(result))
