from flask import Blueprint, jsonify, abort, request
from ..models import User, Tweet, db, likes_table
from sqlalchemy import create_engine
import sqlalchemy
import hashlib
import secrets

engine = create_engine('postgresql://postgres@localhost:5432/twitter')


def scramble(password: str):
    """Hash and salt the given password"""
    salt = secrets.token_hex(16)
    return hashlib.sha512((password + salt).encode('utf-8')).hexdigest()


bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('', methods=['GET'])
def index():
    users = User.query.all()
    result = []
    for u in users:
        result.append(u.serialize())
    return jsonify(result)


@bp.route('/<int:id>', methods=['GET'])
def show(id: int):
    u = User.query.get_or_404(id)
    return jsonify(u.serialize())


@bp.route('', methods=['POST'])
def create():
    if 'username' not in request.json or 'password' not in request.json:
        return abort(400)
    if len(request.json['username']) < 3 or len(request.json['password']) < 8:
        return abort(400)

    u = User(
        username=request.json['username'],
        password=scramble(request.json['password'])
    )

    db.session.add(u)
    db.session.commit()
    return jsonify(u.serialize())


@bp.route('/<int:id>', methods=['DELETE'])
def delete(id: int):
    u = User.query.get_or_404(id)
    try:
        db.session.delete(u)
        db.session.commit()
        return jsonify(True)
    except:
        return jsonify(False)


@bp.route('/<int:id>', methods=['PATCH'])
def update(id: int):
    u = User.query.get_or_404(id)
    u.username = request.json['username'],
    u.password = scramble(request.json['password'])

    try:
        db.session.commit()
        return jsonify(True)
    except:
        return jsonify(False)


@bp.route('/<int:id>/liked_tweets', methods=['GET'])
def liked_tweets(id: int):
    u = User.query.get_or_404(id)
    result = []
    for t in u.liked_tweets:
        result.append(t.serialize())
    return jsonify(result)


@bp.route('/<int:id>/likes', methods=['POST'])
def like(id: int):
    if 'tweet_id' not in request.json:
        return abort(400)
    tweet_id = request.json['tweet_id']

    # check user and tweet exist
    User.query.get_or_404(id)
    Tweet.query.get_or_404(tweet_id)
    try:
        stmt = sqlalchemy.insert(likes_table).values(
            user_id=id, tweet_id=tweet_id)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(True)
    except:
        return jsonify(False)
