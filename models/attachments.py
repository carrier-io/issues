from .mixins import TimestampModelMixin
from sqlalchemy import String, Column, Integer, ForeignKey
from tools import db_tools, db
from .issues import Issue


class Attachment(db_tools.AbstractBaseMixin, TimestampModelMixin, db.Base):
    __tablename__ = "issues_attachments"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=False)
    issue_id = Column(Integer, ForeignKey(Issue.id, ondelete='CASCADE'))
    file_name = Column(String(300), nullable=False)
    url = Column(String(256), nullable=False, unique=True)
    thumbnail_url = Column(String(256), nullable=True, unique=True)