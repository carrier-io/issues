from flask.helpers import url_for
from marshmallow import fields
from plugins.shared_orch.app_objects import ma
from plugins.issues.models.comments import Comment


class CommentSchema(ma.SQLAlchemyAutoSchema):
    username = fields.String(attribute='author.username')
    image_url = fields.Method("get_image")


    class Meta:
        model = Comment
        fields = (
            'id',
            'author_id',
            'comment',
            'updated_at',
            'image_url',
        )
        dump_only = (
            'id',
            'updated_at',
            'image_url',
        )

    def get_image(self, _):
        return url_for('design-system.static', filename='assets/ico/user.svg', _external=True)


comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
