from sqlalchemy.ext.mutable import MutableDict
import sqlalchemy.types as types
from sqlalchemy.orm import relationship, backref
from sqlalchemy import (
    String, 
    Column, 
    Integer,
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
        return self.choices[value.lower()]

    def process_result_value(self, value: str, dialect):
        try:
            return self.choices[value.lower()]
        except KeyError:
            return [k for k, v in self.choices.items() if v.lower() == value.lower()][0]


class Issue(CreateReadUpdateDeleteCountMixin, NestedGetterSetterMixin, db.Base):
    __tablename__ = "issues_issues"

    STATUS_CHOICES = {
        'open':'open',
        'closed':'closed',
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
    project_id = Column(Integer, nullable=False)
    report_id = Column(Integer, nullable=True)
    engagement = Column(String(64), nullable=True, default=None)
    severity = Column(ChoiceType(SEVERITY_CHOICES), nullable=False, default='medium')
    scan_project = Column(String(150), nullable=True)
    asset = Column(String(150), nullable=True)
    type = Column(String(150), nullable=True)
    status = Column(ChoiceType(STATUS_CHOICES), nullable=False, default='Open')
    source_type = Column(String(150), nullable=True)
    source_id = Column(String(64), nullable=True)
    snapshot = Column(MutableDict.as_mutable(JSON), default={})
    state = Column(MutableDict.as_mutable(JSON), default={})

    logs = relationship("Log", backref=backref("issue"))
    tags = relationship("Tag", backref=backref("issue"))

