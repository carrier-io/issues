from .issues import Issue
from .mixins import TimestampModelMixin, CreateReadUpdateDeleteCountMixin
from sqlalchemy import (
    String, 
    Column, 
    Integer,
    ForeignKey,
)
from tools import db


class Log(CreateReadUpdateDeleteCountMixin, TimestampModelMixin, db.Base):
    __tablename__ = "issues_logs"
    
    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey(Issue.id))
    log = Column(String(250), nullable=False)