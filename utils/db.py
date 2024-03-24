from tools import db


def init_db():
    from ..models.events import Event
    from ..models.tags import IssueTag
    from ..models.issues import Issue, issues_tags
    from ..models.attachments import Attachment
    from ..models.comments import Comment

    db.get_shared_metadata().create_all(bind=db.engine)

