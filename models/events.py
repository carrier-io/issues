from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import (
    String, 
    Column,
    Integer
)
from tools import db
from typing import Iterable
from .mixins import CreateReadUpdateDeleteCountMixin, NestedGetterSetterMixin


class Event(CreateReadUpdateDeleteCountMixin, NestedGetterSetterMixin, db.Base):
    __tablename__ = "issues_events"
    # __table_args__ = {'schema': 'tenant'}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=False)
    event_name = Column(String(150), nullable=False)
    field = Column(String(150), nullable=False)
    values = Column(
        MutableDict.as_mutable(JSON), 
        default={
            "old_value":None, 
            "new_value":None
        }
    )

    @classmethod
    def list_events_of_fields(cls, project_id, fields: Iterable):
        return db.session.query(cls).filter(
            cls.project_id==project_id, 
            cls.field.in_(fields)
        ).all()