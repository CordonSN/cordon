from cordon import db
from hashlib import md5
from config import TEMPLATE

ROLE_USER = 0
ROLE_ADMIN = 1


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
    )

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    nickname = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    show_email = db.Column(db.Boolean)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    avatar = db.Column(db.Text)
    cover = db.Column(db.Text)
    sex = db.Column(db.String(128))
    slogan = db.Column(db.String(128))
    status = db.Column(db.String(128))
    location = db.Column(db.String(128))
    bio = db.Column(db.Text)
    create_date = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    post_ids = db.relationship('Post', backref='user', lazy='dynamic',
                               primaryjoin="User.id==Post.user_id")
    post_for_ids = db.relationship('Post', backref='to_user', lazy='dynamic',
                                   primaryjoin="User.id==Post.to_user_id")
    followed = db.relationship('User',
        secondary = followers,
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref = db.backref('followers', lazy = 'dynamic'),
        lazy = 'dynamic')
    like_ids = db.relationship('Like', backref='user', lazy='dynamic',
                               primaryjoin="User.id==Like.user_id")
    comment_ids = db.relationship('Comment', backref='user', lazy='dynamic',
                                  primaryjoin="User.id==Comment.user_id")

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def get_name(self):
        return self.name or self.nickname or 'John Doe'

    def get_avatar(self, size=600):
        if self.avatar:
            return 'data:image/png;base64,%s' % self.avatar
        else:
            #return 'http://www.gravatar.com/avatar/%s?d=mm&s=%s' % (
            #    md5(self.email).hexdigest(),
            #    str(size))
            return '/static/site/%s/img/user_avatar_default.png' % (TEMPLATE)

    def get_cover(self):
        if self.cover:
            return 'data:image/png;base64,%s' % self.cover
        else:
            return '/static/site/%s/img/user_cover_default.png' % (TEMPLATE)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(
                followers,
                (followers.c.followed_id == Post.user_id)
            ).filter(
                db.or_(
                    followers.c.follower_id == self.id,
                    Post.to_user == self,
                )
            ).order_by(
                Post.timestamp.desc())

    # ----- get the user's followers
    def get_followers(self):
        return self.followers.filter(
            followers.c.followed_id != followers.c.follower_id)

    # ----- get who the user follow
    def get_following(self):
        return self.followed.filter(
            followers.c.follower_id == self.id,
            followers.c.followed_id != followers.c.follower_id)


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    nsfw = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # ----- Used to post on a wall of another user (your friend)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # ----- Like from users
    like_ids = db.relationship('Like', backref='post', lazy='dynamic',
                               primaryjoin="Post.id==Like.post_id")
    # ----- Like from users
    comment_ids = db.relationship('Comment', backref='post', lazy='dynamic',
                                  primaryjoin="Post.id==Comment.post_id")

    def __repr__(self):
        return '<Post %r>' % (self.body)

    def user_like(self, user):
        if not user:
            return False
        for like in self.like_ids:
            if like.user == user:
                return True
        return False


class Like(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime)


class Comment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime)
