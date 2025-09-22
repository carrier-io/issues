from datetime import datetime
from sqlalchemy.ext.mutable import MutableDict
import sqlalchemy.types as types
from sqlalchemy.orm import relationship, backref
from sqlalchemy import (
    String,
    Column,
    Integer,
    Date,
    Table,
    Text,
    ForeignKey,
)

from sqlalchemy.dialects.postgresql import JSON
from tools import db
from .mixins import CreateReadUpdateDeleteCountMixin, NestedGetterSetterMixin


class ChoiceType(types.TypeDecorator):

    impl = types.String
    cache_ok = False

    def __init__(self, choices: dict, **kwargs):
        self.choices = dict(choices)
        super().__init__(**kwargs)

    def process_bind_param(self, value: str, dialect):
        return self.choices.get(value.lower(), value.lower())

    def process_result_value(self, value: str, dialect):
        try:
            return self.choices[value.lower()]
        except KeyError:
            return [k for k, v in self.choices.items() if v.lower() == value.lower()][0]


issues_tags = Table(
    'issues_tags_association', db.Base.metadata,
    Column('issue_id', Integer, ForeignKey('carrier.issues_issues.id', ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('carrier.issues_tags.id', ondelete="CASCADE")),
)


class Issue(CreateReadUpdateDeleteCountMixin, NestedGetterSetterMixin, db.Base):
    __tablename__ = "issues_issues"

    STATUS_CHOICES = {
        'open':'open',
        'closed':'closed',
        'postponed':'postponed',
        'blocked':'blocked',
        'in_review':'in_review',
        'done':'done',
        'in_progress':'in_progress',
    }

    SEVERITY_CHOICES = {
        'critical': 'critical',
        'high': 'high',
        'medium': 'medium',
        'low': 'low',
        'info': 'info',
    }
    id = Column(Integer, primary_key=True)
    hash_id = Column(String(64), unique=True, nullable=False)
    title = Column(String(512), nullable=False)
    project_id = Column(Integer, nullable=False)
    report_id = Column(Integer, nullable=True)
    board_id = Column(String(64), nullable=True, default=None)
    engagement = Column(String(64), nullable=True, default=None)
    severity = Column(ChoiceType(SEVERITY_CHOICES), nullable=False, default='medium')
    scan_project = Column(String(150), nullable=True)
    asset = Column(String(150), nullable=True)
    type = Column(String(150), nullable=True)
    status = Column(ChoiceType(STATUS_CHOICES), nullable=False, default='Open')
    source_type = Column(String(150), nullable=True)
    source_id = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    snapshot = Column(MutableDict.as_mutable(JSON), default={})
    state = Column(MutableDict.as_mutable(JSON), default={})
    external_link = Column(String(250), nullable=True)
    assignee = Column(String(64), nullable=True)
    start_date = Column(Date, default=datetime.utcnow)
    end_date = Column(Date)

    tags = relationship("IssueTag", secondary=issues_tags, backref=backref("issues"))

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "hash_id": self.hash_id,
            "title": self.title,
            "project_id": self.project_id,
            "report_id": self.report_id,
            "board_id": self.board_id,
            "engagement": self.engagement,
            "severity": self.severity,
            "scan_project": self.scan_project,
            "asset": self.asset,
            "type": self.type,
            "status": self.status,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "description": self.description,
            "snapshot": self.snapshot,
            "state": self.state,
            "external_link": self.external_link,
            "assignee": self.assignee,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "tags": [tag.tag for tag in self.tags] if self.tags else [],
        }
