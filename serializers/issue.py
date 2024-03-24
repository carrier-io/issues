from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from ..models.issues import Issue
from ..models.tags import IssueTag


class TagSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = IssueTag


class IssueSchema(SQLAlchemyAutoSchema):
    tags = fields.Nested(
        TagSchema, 
        exclude=("created_at", "updated_at"), 
        many=True
    )

    class Meta:
        model = Issue
        include_relationships = True



issue_schema = IssueSchema()
issues_schema = IssueSchema(many=True)

tags_schema = TagSchema(many=True)
issue_tags_schema = TagSchema(many=True, exclude=('project_id', ))