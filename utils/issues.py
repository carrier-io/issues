import uuid
from jira import JIRA  # pylint: disable=E0401
from pylon.core.tools import log  # pylint: disable=E0611,E0401
from ..models.issues import Issue
from ..models.tags import IssueTag
from ..serializers.issue import issue_schema
from tools import db
from .logs import log_create_issue, log_tag_create, log_update_issue
from sqlalchemy.sql import exists
from sqlalchemy import func


def add_issue_tag_line(event_manager, project_id, issue, new_tag, commit=False):
    tag = IssueTag.query.filter_by(project_id=project_id, tag=new_tag['tag']).first()
    if not tag:
        new_tag['project_id'] = project_id
        tag = IssueTag.create(new_tag)
        log_tag_create(
            event_manager,
            project_id,
            issue.id,
            tag.id
        )
    issue.tags.append(tag)
    if commit:
        Issue.commit()

def set_state(event_manager, project_id, issue_id_uuid, state, payload=None):
    """ Tool """
    issue = Issue.query.filter_by(hash_id=issue_id_uuid)
    changes = {
        'state.value': {
            'old_value': issue.state['value'],
            'new_value': state,
        },
        'state.payload': {
            'old_value': issue.state['payload'],
            'new_value': payload,
        }
    }
    issue.state['value'] = state
    issue.state['payload'] = payload
    db.session.commit()
    log_update_issue(event_manager, project_id, issue.id, changes)

def reopen_issues(source_type, issue_ids: list, event_manager=None, user=None):
    log.info(f"Re-opening issues - {issue_ids} - {source_type}")
    query = db.session.query(Issue).filter(
        Issue.source_type==source_type,
        Issue.source_id.in_(issue_ids)
    )
    state = {
        'value': "NEW_ISSUE",
        'payload': None,
    }

    # prepare changes
    issues = query.all()
    user_changes = {}
    for issue in issues:
        user_changes[issue.id] = {
            'state.value': {
                'old_value': issue.state['value'],
                'new_value': state['value'],
            },
            'state.payload': {
                'old_value': issue.state['payload'],
                'new_value': state['payload']
            }
        }

    query.update({
        Issue.status: 'open',
        Issue.state: state
    })
    db.session.commit()
    for issue in issues:
        changes = user_changes[issue.id]
        log_update_issue(event_manager, issue.project_id, issue.id, changes, user)

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

def get_snapshot(module, source_type, issue_id):
    snapshot_rpc = getattr(
        module.context.rpc_manager.call,
        f'{source_type}__get_issue_snapshot',
    )
    snapshot = snapshot_rpc(issue_id)
    snapshot['source_type'] = source_type
    snapshot['issue_id'] = issue_id
    return snapshot

def search_issue(source_id, source_type):
    return db.session.query(
            exists().where(
                Issue.status=='open',
                Issue.source_id==source_id,
                Issue.source_type==source_type
            )
        ).scalar()

def stringify_description(description):
    if not type(description) == str:
        return '\n'.join(description)
    return description

def parse_issue_payload(payload):
    source_type = payload.get('source_type')
    issue_id = payload.get('issue_id')
    report_id = payload.get("report_id")
    engagement = payload.get('engagement')
    project_id = payload.get('project_id')
    board_id = payload.get('board_id')
    title = payload.get('title')
    description = payload.get('description')
    description = stringify_description(description)
    data = {
        "hash_id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "source_type": source_type,
        "source_id": issue_id,
        "report_id": report_id,
        "board_id": board_id,
        "snapshot": payload,
        "severity": payload.get("severity"),
        "scan_project": payload.get("project"),
        "asset": payload.get("asset"),
        "assignee": payload.get('assignee'),
        "type": payload.get("type"),
        "status": "open",
        "start_date": payload.get("start_date"),
        "end_date": payload.get("end_date"),
        "state": {
            "value": "OPEN",
            "payload": None,
        },
        "engagement": engagement,
        "project_id": project_id,
    }
    return data

def _validate_issue(project_id, snapshot):
    snapshot["project_id"] = project_id
    payload = parse_issue_payload(snapshot)
    issue = issue_schema.load(payload)
    return issue

def validate_findings(project_id, findings):
    return [_validate_issue(project_id, finding) for finding in findings]

def open_issue(project_id, snapshot, event_manager=None, user=None):
    issue = _validate_issue(project_id, snapshot)
    issue = Issue.create(issue)
    for tag in snapshot.get('tags', []):
        add_issue_tag_line(event_manager, project_id, issue, tag)
    db.session.commit()
    if event_manager:
        log_create_issue(event_manager, project_id, issue.id, user)
    return issue

def create_finding_issues(event_manager, project_id, issues):
    latest_id = db.session.query(func.max(Issue.id)).scalar()
    latest_id = 0 if latest_id is None else latest_id
    new_issues = _sort_out_new_issues(issues)
    db.session.bulk_save_objects(new_issues)
    db.session.commit()
    for issue in new_issues:
        latest_id += 1
        log_create_issue(event_manager, project_id, latest_id)
    return new_issues

def _sort_out_new_issues(issues) -> list:
    return [
        Issue(**issue)
        for issue in issues
        if not search_issue(issue['source_id'], issue['source_type']) 
    ]