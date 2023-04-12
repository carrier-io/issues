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
    tag = Column(String(250), unique=True, nullable=False)
