from config.database import db
from models.discussion_model import DiscussionPost
from models.group_model import ReadingGroup
from models.user_model import User


def _ensure_group_membership(group, user):
    if group.owner_id == user.id:
        return True
    return user in group.members


def create_group_post_service(group_id, user_id, data):
    content = data.get("content")
    if not content:
        return {"message": "content is required"}, 400

    group = ReadingGroup.query.get(group_id)
    if not group:
        return {"message": "Group not found"}, 404

    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404

    if not _ensure_group_membership(group, user):
        return {"message": "Must be a group member to post"}, 403

    post = DiscussionPost(group_id=group_id, user_id=user_id, content=content)
    db.session.add(post)
    db.session.commit()

    return {
        "message": "Post created",
        "post": {
            "id": post.id,
            "group_id": post.group_id,
            "user_id": post.user_id,
            "content": post.content,
            "created_at": post.created_at.isoformat() if post.created_at else None,
        },
    }, 201


def list_group_posts_service(group_id, user_id):
    group = ReadingGroup.query.get(group_id)
    if not group:
        return {"message": "Group not found"}, 404

    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404

    if not _ensure_group_membership(group, user):
        return {"message": "Must be a group member to view posts"}, 403

    posts = DiscussionPost.query.filter_by(group_id=group_id).order_by(DiscussionPost.created_at.desc()).all()
    return [
        {
            "id": post.id,
            "group_id": post.group_id,
            "user_id": post.user_id,
            "author_name": post.author.name or post.author.username,
            "content": post.content,
            "created_at": post.created_at.isoformat() if post.created_at else None,
        }
        for post in posts
    ], 200
