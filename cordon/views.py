from werkzeug import secure_filename
from flask import render_template, flash, redirect, session, url_for, \
    request, g, Flask, request, abort
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from hashlib import sha256
from cordon import cordon, db, lm
from forms import LoginForm, EditProfileForm, EditAvatarForm, PostForm, \
    RegisterForm, CommentForm, EditCoverForm
from models import ROLE_USER, ROLE_ADMIN, Post, User, Like, Comment
from datetime import datetime
from config import POSTS_PER_PAGE, FRIENDS_PER_PAGE
from base64 import b64encode


@cordon.route('/', methods=['GET', 'POST'])
@cordon.route('/index', methods=['GET', 'POST'])
@cordon.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        import pdb; pdb.set_trace()
        post = Post(body=form.post.data,
                    nsfw=form.nsfw.data,
                    timestamp=datetime.utcnow(),
                    user=g.user,
                    to_user=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!', 'success')
        return redirect(url_for('index', page=page))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template(
        "site/%s/index.html" % (cordon.config['TEMPLATE']),
        title = 'Cordon',
        form = form,
        SHOW_COMMENT_FORM = False,
        user = g.user,
        posts = posts)

@cordon.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    comment_form = CommentForm()
    if post:
        # ----- Add the comment if exists
        if comment_form.validate_on_submit():
            comment = Comment(body=comment_form.comment.data,
                              post=post,
                              user=g.user,
                              timestamp=datetime.utcnow(),
                              )
            db.session.add(comment)
            db.session.commit()
        else:
            comment_form.comment.data = ''
        return render_template(
            "site/%s/post.html" % (cordon.config['TEMPLATE']),
            title='Cordon',
            user=g.user,
            post=post,
            comment_form=comment_form,
            SHOW_COMMENT_FORM=True)
    return redirect(url_for('index'))

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@cordon.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        nickname = form.nickname.data
        password = form.password.data
        session['remember_me'] = form.remember_me.data
        registered_user = User.query.filter_by(
            nickname=nickname,
            password=sha256(password).hexdigest()
            ).first()
        if registered_user is None:
            flash('Username or Password is invalid', 'danger')
            return redirect(url_for('login'))
        if login_user(registered_user):
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
    return render_template(
        "site/%s/login.html" % (cordon.config['TEMPLATE']),
        title = 'Sign In',
        form = form)

@cordon.route('/register', methods=['GET', 'POST'])
def register():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        nickname = form.nickname.data
        email = form.email.data
        password = form.password.data
        r_password = form.r_password.data
        if password != r_password:
            flash('Different Password', 'danger')
            return redirect(url_for('register'))
        # ----- Check if email exist yet
        exist_user = User.query.filter_by(email=email).first()
        if exist_user:
            flash('Email exist, yet', 'danger')
            return redirect(url_for('register'))
        # ----- Check if username exist yet
        exist_user = User.query.filter_by(nickname=nickname).first()
        if exist_user:
            flash('Username exist, yet', 'danger')
            return redirect(url_for('register'))
        # ----- Register user!
        user = User(nickname=nickname,
                    email=nickname,
                    password=sha256(password).hexdigest(),
                    create_date=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        # ----- An user follow itself to read the own posts
        db.session.add(user.follow(user))
        db.session.commit()
        flash('User successfully registered', 'success')
        return redirect(url_for('login'))
    return render_template(
        "site/%s/register.html" % (cordon.config['TEMPLATE']),
        title='Sign Up',
        form=form)

@cordon.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@cordon.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@cordon.route('/user/<nickname>', methods=['GET', 'POST'])
@cordon.route('/user/<nickname>/<int:page>', methods=['GET', 'POST'])
@login_required
def user(nickname, page = 1):
    user = User.query.filter_by(nickname=nickname).first()
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.post.data,
                    timestamp = datetime.utcnow(),
                    user = g.user,
                    to_user = user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!', 'success')
        return redirect(url_for('user',
                                nickname=user.nickname,
                                page=page))
    if user == None:
        flash('User ' + nickname + ' not found.', 'warning')
        return redirect(url_for('index'))
    posts = user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template(
        "site/%s/user.html" % (cordon.config['TEMPLATE']),
        user=user,
        posts=posts,
        form=form,
        SHOW_COMMENT_FORM = False,
        )

# ------------------------------------------------------------------------------
# Show who follow the user
# ------------------------------------------------------------------------------
@cordon.route('/user/<nickname>/followers')
@cordon.route('/user/<nickname>/followers/<int:page>')
@login_required
def followers(nickname, page = 1):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.', 'warning')
        return redirect(url_for('index'))
    friends = user.get_followers().paginate(
        page, FRIENDS_PER_PAGE, False)
    return render_template(
        "site/%s/followers.html" % (cordon.config['TEMPLATE']),
        user=user, friends=friends)

# ------------------------------------------------------------------------------
# Show who the user is following
# ------------------------------------------------------------------------------
@cordon.route('/user/<nickname>/following')
@cordon.route('/user/<nickname>/following/<int:page>')
@login_required
def following(nickname, page = 1):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.', 'warning')
        return redirect(url_for('index'))
    friends = user.get_following().paginate(
        page, FRIENDS_PER_PAGE, False)
    return render_template(
        "site/%s/following.html" % (cordon.config['TEMPLATE']),
        user=user, friends=friends)

@cordon.route('/user/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    #form = EditProfileForm(g.user.nickname)
    form = EditProfileForm()
    avatar_form = EditAvatarForm()
    cover_form = EditCoverForm()
    # ----- If form is used
    print 'EP', form.validate_on_submit()
    if form.validate_on_submit():
        g.user.name = form.name.data
        g.user.show_email = form.show_email.data
        g.user.bio = form.bio.data
        g.user.sex = form.sex.data
        g.user.slogan = form.slogan.data
        g.user.status = form.status.data
        g.user.location = form.location.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('edit_profile'))
    else:
        form.name.data = g.user.name
        form.show_email.data = g.user.show_email
        form.bio.data = g.user.bio
        form.sex.data = g.user.sex
        form.slogan.data = g.user.slogan
        form.status.data = g.user.status
        form.location.data = g.user.location
    return render_template(
        "site/%s/edit_profile.html" % (cordon.config['TEMPLATE']),
        user = g.user,
        form = form,
        avatar_form = avatar_form,
        cover_form = cover_form,
        )

@cordon.route('/user/edit/avatar', methods=['POST'])
@login_required
def edit_avatar():
    avatar_form = EditAvatarForm()
    if avatar_form.validate_on_submit():
        # ----- Check image validity
        #       TO CHANGE: This code is shit!!!
        if str(type(avatar_form.avatar.data.stream)) == "<type '_io.BytesIO'>":
            filename = secure_filename(avatar_form.avatar.file.filename)
            # ------ Check if user pass an image
            if not filename:
                flash('Select an image', 'danger')
                return redirect(url_for('edit_profile'))
            if not filename.split('.')[-1].lower() in ('png', 'gif', 'jpg',
                                                       'jpeg'):
                flash('Not valid image', 'danger')
                return redirect(url_for('edit_profile'))
            b64_avatar = b64encode(avatar_form.avatar.data.stream.getvalue())
            g.user.avatar = str(b64_avatar)
            db.session.add(g.user)
            db.session.commit()
            flash('Avatar changed', 'success')
        else:
            flash('Not valid image', 'danger')
    return redirect(url_for('edit_profile'))

@cordon.route('/user/edit/cover', methods=['POST'])
@login_required
def edit_cover():
    cover_form = EditCoverForm()
    if cover_form.validate_on_submit():
        # ----- Check image validity
        #       TO CHANGE: This code is shit!!!
        if str(type(cover_form.cover.data.stream)) == "<type '_io.BytesIO'>":
            filename = secure_filename(cover_form.cover.file.filename)
            # ------ Check if user pass an image
            if not filename:
                flash('Select an image', 'danger')
                return redirect(url_for('edit_profile'))
            if not filename.split('.')[-1].lower() in ('png', 'gif', 'jpg',
                                                       'jpeg'):
                flash('Not valid image', 'danger')
                return redirect(url_for('edit_profile'))
            b64_cover = b64encode(cover_form.cover.data.stream.getvalue())
            g.user.cover = str(b64_cover)
            db.session.add(g.user)
            db.session.commit()
            flash('Cover changed', 'success')
        else:
            flash('Not valid image', 'danger')
    return redirect(url_for('edit_profile'))

@cordon.errorhandler(404)
def not_found_error(error):
    return render_template(
        "site/%s/404.html" % (cordon.config['TEMPLATE'])), 404

@cordon.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template(
        "site/%s/500.html" % (cordon.config['TEMPLATE'])), 500

@cordon.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.', 'warning')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!', 'warning')
        return redirect(url_for('user', nickname = nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.', 'warning')
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!', 'success')
    return redirect(url_for('user', nickname = nickname))

@cordon.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.', 'warning')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!', 'warning')
        return redirect(url_for('user', nickname = nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.', 'warning')
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.', 'success')
    return redirect(url_for('user', nickname = nickname))

@cordon.route('/post/like/<int:post_id>')
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    # ----- Search if a like exists yet
    like = Like.query.filter_by(post=post, user=g.user).first()
    if post and not like:
        like = Like(post = post,
                    user = g.user,
                    timestamp = datetime.utcnow(),
                    )
        db.session.add(like)
        db.session.commit()
    else:
        flash('No post for id %s' % (post_id), 'danger')
    return redirect(request.referrer or url_for('post'))

@cordon.route('/post/unlike/<int:post_id>')
@login_required
def unlike(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(post=post, user=g.user).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    else:
        flash('No like found on post %s' % (post_id), 'danger')
    return redirect(request.referrer or url_for('post'))

@cordon.route('/post/remove/<int:post_id>')
@login_required
def remove(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post.user.id != g.user.id:
        flash('You can\'t delete other user posts', 'danger')
        return redirect(request.referrer or url_for('post'))
    # ----- Delete all like for this post
    for like in post.like_ids:
        db.session.delete(like)
    db.session.commit()
    # ----- Delete post
    db.session.delete(post)
    db.session.commit()
    return redirect(request.referrer or url_for('post'))
