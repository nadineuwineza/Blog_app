from flask import render_template,request,redirect,url_for,abort, flash, abort
from . import main
from flask_fontawesome import FontAwesome
from .. import db, photos
from flask_login import login_required, current_user
from ..models import User, Blog, Comment, Upvotes,Downvote, PhotoProfile
from .forms import AddBlog, UpdateProfile, CommentsForm, UpvoteForm,DownvoteForm
from flask.views import View, MethodView
import markdown2
from ..request import get_quotes


@main.route('/', methods=['GET', 'post'])
def index():
   quote = get_quotes()
   blogs_id = Blog.query.filter_by().first()
   sport = Blog.query.filter_by(category='sport')
   comedy = Blog.query.filter_by(category='comedy')
   technology = Blog.query.filter_by(category='technology')
   political =Blog.query.filter_by(category='political')
   title = 'blogs'
   
   upvotes = Upvotes.get_all_upvotes(blogs_id=Blog.id)

   return render_template('index.html', title=title,upvotes=upvotes,sport=sport, comedy= comedy, technology=technology, political=political,quote=quote)

@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()

    if user is None:
        abort(404)

    return render_template("profile/profile.html", user = user)

@main.route('/user/<uname>/update', methods=['GET','POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username= uname).first()
    if user is None:
        abort(404)
    form = UpdateProfile()
    if form.validate_on_submit():
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile', uname=user.username))
    return render_template('profile/update.html', form=form)

@main.route('/user/<uname>/update/pic', methods=['POST'])
@login_required
def update_pic(uname):
    user= User.query.filter_by(username=uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        user_photo = PhotoProfile(pic_path = path,user = user)
        db.session.commit()
    return redirect(url_for('main.profile', uname=uname))

@main.route('/blogs/new/', methods= ['GET','POST'])
@login_required
def new_blog():
    form = AddBlog()
    upvotes = Upvotes.query.filter_by(blogs_id=Blog.id)
    if form.validate_on_submit():
        details= form.details.data
        blog_id =current_user
        category = form.category.data
        print(current_user._get_current_object().id)
        new_blogs = Blog(blog_id=current_user._get_current_object().id, details=details, category=category)
        new_blogs.save_blogs()

        return redirect(url_for('main.index'))

    return render_template('blog.html', form=form)

@main.route('/comment/new/<int:blogs_id>', methods=['GET','POST'])
@login_required
def add_comment(blogs_id):
    form = CommentsForm()
    blog = Blog.query.get(blogs_id)
    if form.validate_on_submit():
        details= form.details.data
        add_comment= Comment(details=details, user_id=current_user._get_current_object().id, blogs_id=blogs_id)
        db.session.add(add_comment)
        db.session.commit()

        return redirect(url_for('.add_comment', blogs_id=blogs_id))
    allComents= Comment.query.filter_by(blogs_id=blogs_id).all()
    return render_template('comment.html',form=form, allComents=allComents,blog=blog)

@main.route('/blog/upvote/<int:blogs_id>/upvote', methods=['GET', 'POST'])
@login_required
def upvote(blogs_id):
    blog = Blog.query.get(blogs_id)
    user = current_user
    p_upvotes =Upvotes.query.filter_by(blogs_id=blogs_id)

    if Upvotes.query.filter(Upvotes.user_id==user.id, Upvotes.blogs_id==blogs_id).first():
        return redirect(url_for('main.index'))

    newUpvote = Upvotes(blogs_id=blogs_id, user=current_user)
    newUpvote.save_upvotes()
    return redirect(url_for('main.index'))



@main.route('/blog/downvote/<int:blogs_id>/downvote', methods=['GET','POST'])
@login_required
def downvote(blogs_id):
    blog= Blog.query.get(blogs_id)
    user = current_user
    douwnVotes= Downvote.query.filter_by(blogs_id=blogs_id)

    if Downvote.query.filter(Downvote.user_id==user.id, Downvote.blogs_id==blogs_id).first():
        return redirect(url_for('main.index'))

    newDownvote = Downvote(blogs_id=blogs_id, user=current_user)
    newDownvote.save_downvotes()
    return redirect(url_for('main.index'))