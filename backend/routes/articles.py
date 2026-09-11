from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models import Article, ArticleBodyBlock, ArticleStatus, Category, Media, Tag, UserRole
from backend.utils.auth_helpers import role_required
from backend.utils.body_blocks import parse_body_input, replace_blocks, serialize_blocks
from backend.utils.content import (
    can_manage_draft,
    iso,
    is_admin,
    optional_user,
    published_at_for,
    valid_slug,
    valid_text,
)
from backend.utils.media import serialize_media

blueprint = Blueprint("articles", __name__, url_prefix="/api/articles")


def _serialize(article):
    return {
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "body": article.body,
        "body_blocks": serialize_blocks(article),
        "status": article.status.value,
        "author_id": article.author_id,
        "category_id": article.category_id,
        "featured_image_id": article.featured_image_id,
        "featured_image": (
            serialize_media(article.featured_image)
            if article.featured_image is not None
            else None
        ),
        "tag_ids": sorted(tag.id for tag in article.tags),
        "created_at": iso(article.created_at),
        "updated_at": iso(article.updated_at),
        "published_at": iso(article.published_at),
    }


def _invalid():
    return jsonify(error="Invalid content data"), 400


def _load_relations(payload, partial=False):
    changes = {}
    for name, maximum in (("title", 255), ("slug", 255)):
        if name not in payload:
            if not partial:
                raise ValueError
            continue
        value = payload[name]
        if (name == "slug" and not valid_slug(value, maximum)) or (
            name != "slug" and not valid_text(value, maximum)
        ):
            raise ValueError
        changes[name] = value.strip()

    if "category_id" in payload:
        category_id = payload["category_id"]
        if (
            not isinstance(category_id, int)
            or isinstance(category_id, bool)
            or db.session.get(Category, category_id) is None
        ):
            raise ValueError
        changes["category_id"] = category_id
    elif not partial:
        raise ValueError

    if "featured_image_id" in payload:
        media_id = payload["featured_image_id"]
        if media_id is not None and (
            not isinstance(media_id, int)
            or isinstance(media_id, bool)
            or (media := db.session.get(Media, media_id)) is None
            or media.source_type != "upload"
            or media.media_type != "image"
        ):
            raise ValueError
        changes["featured_image_id"] = media_id

    if "tag_ids" in payload:
        tag_ids = payload["tag_ids"]
        if not isinstance(tag_ids, list) or any(
            not isinstance(tag_id, int) or isinstance(tag_id, bool) for tag_id in tag_ids
        ):
            raise ValueError
        unique_ids = list(dict.fromkeys(tag_ids))
        tags = (
            list(db.session.scalars(db.select(Tag).where(Tag.id.in_(unique_ids))))
            if unique_ids
            else []
        )
        if len(tags) != len(unique_ids):
            raise ValueError
        changes["tags"] = tags
    return changes


def _visible_statement(user):
    statement = db.select(Article).order_by(Article.id)
    if is_admin(user):
        return statement
    if user is not None and user.role is UserRole.PUBLISHER:
        return statement.where(
            or_(
                Article.status == ArticleStatus.PUBLISHED,
                Article.author_id == user.id,
            )
        )
    return statement.where(Article.status == ArticleStatus.PUBLISHED)


@blueprint.get("")
def list_articles():
    user = optional_user()
    items = db.session.scalars(_visible_statement(user)).unique().all()
    return jsonify(items=[_serialize(item) for item in items])


@blueprint.get("/<int:article_id>")
def get_article(article_id):
    user = optional_user()
    article = db.session.get(Article, article_id)
    visible = db.session.execute(
        _visible_statement(user).where(Article.id == article_id)
    ).scalar_one_or_none()
    if article is None or visible is None:
        return jsonify(error="Not found"), 404
    return jsonify(item=_serialize(article))


@blueprint.get("/slug/<slug>")
def get_article_by_slug(slug):
    user = optional_user()
    article = db.session.execute(
        _visible_statement(user).where(Article.slug == slug)
    ).scalar_one_or_none()
    if article is None:
        return jsonify(error="Not found"), 404
    return jsonify(item=_serialize(article))


@blueprint.post("")
@role_required("publisher")
def create_article():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _invalid()
    user = get_current_user()
    if not is_admin(user) and payload.get("status", "draft") != "draft":
        return jsonify(error="Insufficient permissions"), 403
    try:
        body, blocks = parse_body_input(payload)
        changes = _load_relations(payload)
        status = (
            ArticleStatus(payload.get("status", "draft"))
            if is_admin(user)
            else ArticleStatus.DRAFT
        )
    except (ValueError, TypeError):
        return _invalid()
    tags = changes.pop("tags", [])
    article = Article(**changes, body=body, author_id=user.id, status=status)
    article.tags = tags
    replace_blocks(article, blocks, ArticleBodyBlock)
    article.published_at = published_at_for(status)
    db.session.add(article)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Slug is already in use"), 409
    return jsonify(item=_serialize(article)), 201


@blueprint.put("/<int:article_id>")
@role_required("publisher")
def update_article(article_id):
    article = db.session.get(Article, article_id)
    if article is None:
        return jsonify(error="Not found"), 404
    user = get_current_user()
    if not can_manage_draft(user, article):
        return jsonify(error="Insufficient permissions"), 403
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not payload:
        return _invalid()
    try:
        body, blocks = parse_body_input(payload, partial=True)
        changes = _load_relations(payload, partial=True)
        status = ArticleStatus(payload.get("status", article.status.value))
    except (ValueError, TypeError):
        return _invalid()
    if not is_admin(user) and status not in {ArticleStatus.DRAFT, ArticleStatus.PENDING_REVIEW}:
        return jsonify(error="Insufficient permissions"), 403
    tags = changes.pop("tags", None)
    if body is not None:
        changes["body"] = body
    for name, value in changes.items():
        setattr(article, name, value)
    if tags is not None:
        article.tags = tags
    if blocks is not None:
        replace_blocks(article, blocks, ArticleBodyBlock)
    article.status = status
    article.published_at = published_at_for(status, article.published_at)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Slug is already in use"), 409
    return jsonify(item=_serialize(article))


@blueprint.delete("/<int:article_id>")
@role_required("publisher")
def delete_article(article_id):
    article = db.session.get(Article, article_id)
    if article is None:
        return jsonify(error="Not found"), 404
    if not can_manage_draft(get_current_user(), article):
        return jsonify(error="Insufficient permissions"), 403
    db.session.delete(article)
    db.session.commit()
    return "", 204
