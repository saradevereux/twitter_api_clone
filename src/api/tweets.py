from flask import Blueprint, jsonify, abort, request
from ..models import Tweet, User, db

bp = Blueprint('tweets', __name__, url_prefix='/tweets')


@bp.route('', methods=['GET'])
def index():
    tweets = Tweet.query.all()
    result = []
    for t in tweets:
        result.append(t.serialize())
    return jsonify(result)


@bp.route('/<int:id>', methods=['GET'])
def show(id: int):
    t = Tweet.query.get_or_404(id)
    return jsonify(t.serialize())


@bp.route('', methods=['POST'])
def create():
    if 'user_id' not in request.json or 'content' not in request.json:
        return abort(400)
    User.query.get_or_404(request.json['user_id'])
    t = Tweet(
        user_id=request.json['user_id'],
        content=request.json['content']
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(t.serialize())


@bp.route('/<int:id>', methods=['DELETE'])
def delete(id: int):
    t = Tweet.query.get_or_404(id)
    try:
        db.session.delete(t)
        db.session.commit()
        return jsonify(True)
    except:
        return jsonify(False)


@bp.route('/<int:id>/liking_users', methods=['GET'])
def liking_users(id: int):
    t = Tweet.query.get_or_404(id)
    result = []
    for t in t.likes:
        result.append(t.serialize())
    return jsonify(result)
