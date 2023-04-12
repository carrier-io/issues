from sqlalchemy import (
    ForeignKey,
    Column, 
    Integer,
    Text,
)
from tools import db_tools, db
from .mixins import TimestampModelMixin
from .issues import Issue


class Comment(db_tools.AbstractBaseMixin, TimestampModelMixin, db.Base):
    __tablename__ = "issues_comments"
    
    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey(Issue.id, ondelete='CASCADE'))
    project_id = Column(Integer, nullable=False)
    author_id = Column(Integer, nullable=True)
    comment = Column(Text)