from ..models.issues import Issue
from ..models.tags import Tag, Log
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields


class TagSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tag


class LogSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Log


class IssueSchema(SQLAlchemyAutoSchema):
    logs = fields.Pluck(LogSchema, 'log', many=True)
    tags = fields.Pluck(TagSchema, 'tag', many=True)

    class Meta:
        model = Issue
        include_relationships = True


issue_schema = IssueSchema()
issues_schema = IssueSchema(many=True, exclude=('logs', 'tags'))

logs_schame = LogSchema(many=True)
tags_schema = TagSchema(many=True)