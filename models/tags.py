from sqlalchemy import (
    String, 
    Column, 
    Integer,
    ForeignKey
)
from tools import db_tools, db
from .mixins import TimestampModelMixin, CreateReadUpdateDeleteCountMixin
from .issues import Issue


class Tag(CreateReadUpdateDeleteCountMixin, TimestampModelMixin, db.Base):
    __tablename__ = "issues_tags"
    
    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey(Issue.id))
    tag = Column(String(250), nullable=False)


class Log(CreateReadUpdateDeleteCountMixin, TimestampModelMixin, db.Base):
    __tablename__ = "issues_logs"
    
    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey(Issue.id))
    log = Column(String(250), nullable=False)