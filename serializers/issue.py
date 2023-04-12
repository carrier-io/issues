from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from ..models.issues import Issue
from ..models.tags import Tag
from ..models.logs import Log


class TagSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tag


class LogSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Log


class IssueSchema(SQLAlchemyAutoSchema):
    logs = fields.Pluck(LogSchema, 'log', many=True)
    tags = fields.Nested(
        TagSchema, 
        exclude=("created_at", "updated_at"), 
        many=True
    )

    class Meta:
        model = Issue
        include_relationships = True



issue_schema = IssueSchema()
issues_schema = IssueSchema(many=True, exclude=('logs',))

logs_schame = LogSchema(many=True)
tags_schema = TagSchema(many=True)