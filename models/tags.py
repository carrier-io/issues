from sqlalchemy import (
    String, 
    Column, 
    Integer,
)
from tools import db
from .mixins import TimestampModelMixin, CreateReadUpdateDeleteCountMixin


class Tag(CreateReadUpdateDeleteCountMixin, TimestampModelMixin, db.Base):
    __tablename__ = "issues_tags"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=False)
    tag = Column(String(250), unique=True, nullable=False)
    color = Column(String(15))
