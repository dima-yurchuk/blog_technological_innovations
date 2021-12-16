from . import blog_bp
from .forms import FormPostCreate, FormPostUpdate, FormComment
from app import db
from .models import Category, Post, Like, Comment
from app.user.models import User
from flask import redirect, url_for, flash, request, render_template, abort
from flask_login import current_user, login_required
from app.utils import handle_posts_view


@blog_bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def post_create():
    form = FormPostCreate.new()
    # if request.method == 'POST':
    #     print(request.values)
    if form.validate_on_submit():
        category_id = form.category.data
        title = form.title.data
        content = form.content.data
        # print(category_id, title, content)
        category = db.session.query(Category.id).filter(
            Category.id == category_id)
        post = Post(category_id=category, user_id=current_user.id, title=title,
                    content=content)
        try:
            db.session.add(post)
            db.session.commit()
            flash('Публікація успішно створена', 'success')
            return redirect(url_for('blog_bp_in.post_view', post_id=post.id))
        except:
            db.session.rollback()
            flash('Помилка при додаванні публікації до бази даних', 'danger')
            return redirect(url_for('blog_bp_in.post_create'))
    # elif request.method == 'POST':
    #     category_id = form.category.data
    #     title = form.title.data
    #     content = form.content.data
    #     print('UNsuccessful create post')
    #     print(category_id, title, content)
    return render_template('post_create.html', form=form,
                           title='Створення публікації')


@blog_bp.route('/post/<int:post_id>/update', methods=["GET", "POST"])
def post_update(post_id):
    form = FormPostUpdate.new()
    post = Post.query.get_or_404(post_id)
    if not current_user.is_authenticated or current_user.id != post.user_id:
        abort(403, description="Ви не маєте прав на редагування даної "
                               "публікації")

    if form.validate_on_submit():
        category_id = form.category.data
        post.category_id = db.session.query(Category.id).filter(
            Category.id == category_id)
        post.title = form.title.data
        post.content = form.content.data
        try:
            db.session.commit()
            flash('Публікація успішно оновлена', 'info')
            return redirect(
                url_for('blog_bp_in.post_view', post_id=post_id))
        except:
            db.session.rollback()
            flash('Помилка при оновленні публікації', 'danger')

    elif request.method == 'GET':  # якщо ми відкрили сторнку
        # для редагування, записуємо у поля форми значення з БД
        form.category.data = post.category_br.id
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post_update.html',
                           title='Оновити публікацію', form=form)


@blog_bp.route('/post/<int:post_id>/delete', methods=["GET", "POST"])
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_authenticated or current_user.id != post.user_id:
        abort(403, description="Ви не маєте прав на видалення даної "
                               "публікації")
    elif current_user.id == post.user_id:
        try:
            db.session.delete(post)
            db.session.commit()
            flash('Публікацію успішно видалено!', 'success')
        except:
            flash('Помилка при видаленні публікації', 'danger')
        return redirect(url_for('user_bp_in.account'))


@blog_bp.route('/comment/<int:comment_id>/delete', methods=["GET", "POST"])
def comment_delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    if not current_user.is_authenticated or current_user.id != comment.user_id:
        abort(403, description="Ви не маєте прав на видалення даного "
                               "коментаря")
    if current_user.id == comment.user_id:
        try:
            db.session.delete(comment)
            db.session.commit()
            # flash('Публікацію успішно видалено!', 'success')
        except:
            flash('Помилка при видаленні коментаря', 'danger')
        return redirect(url_for('blog_bp_in.post_view', post_id=post_id))


@blog_bp.route('/post/<int:post_id>', methods=["GET", "POST"])
def post_view(post_id):
    form = FormComment()

    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id) \
        .order_by(Comment.created_at.desc())
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(user_id=current_user.id, post_id=post.id,
                          text=form.comment.data)
        try:
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('blog_bp_in.post_view', post_id=post_id))
        except:
            db.session.rollback()
            flash('Помилка додавання коментаря', 'danger')
    return render_template('post_view.html', post=post, form=form,
                           comments=comments)


@blog_bp.route('/post/<int:post_id>/<action>')
@login_required
def rate_action(post_id, action):
    post = Post.query.get_or_404(post_id)

    if current_user.id == post.user_id:
        abort(403, description="Ви не можете оцінювати власні публікації")

    if action == 'like':
        # якщо пост не був оцінений до цього
        if current_user.is_rated_post(post) is False:
            current_user.like_post(post)
        else:
            # якщо вже стояв ДИЗлайк - то міняємо його на лайк
            if current_user.get_rate_status(post) is False:
                current_user.change_rate(post)
            # якщо стояв рейтинг лайк - то забираємо його (пост стає без оцінк)
            else:
                current_user.unrate_post(post)
        db.session.commit()

    if action == 'dislike':
        # якщо пост не був оцінений до цього
        if current_user.is_rated_post(post) is False:
            current_user.dislike_post(post)
        else:
            # якщо вже стояв лайк - то міняємо його на ДИЗлайк
            if current_user.get_rate_status(post) is True:
                current_user.change_rate(post)
            # якщо стояв рейтинг ДИЗлайк -то забираємо його(пост стає бз оцінк)
            else:
                current_user.unrate_post(post)
        db.session.commit()

    # print('NUM OF LIKES', Like.query.filter(
    #     Like.post_id == post_id,
    #     Like.status == True).count())
    # print('NUM OF DISLIKES', Like.query.filter(
    #     Like.post_id == post_id,
    #     Like.status == False).count())

    return redirect(url_for('blog_bp_in.post_view', post_id=post_id))


@blog_bp.route('/user_posts/<int:id>')
def user_posts(id):
    user = User.query.get_or_404(id)
    posts, sort_by = handle_posts_view(Post.query.filter_by(user_id=id),
                                       request.args)
    return render_template('user_posts.html', posts=posts, sort_by=sort_by,
                           user=user)


@blog_bp.route('/category/<int:id>')
def posts_by_category(id):
    # print("posts_by_category")
    # print(id)
    Category.query.get_or_404(id)
    posts, sort_by = handle_posts_view(
        Post.query.filter_by(category_id=id),
        request.args
    )
    # print("sort_by ==", sort_by)
    return render_template('posts_by_category.html', posts=posts,
                           sort_by=sort_by)


@blog_bp.route('/search')
def search():
    print('search')
    user_query = request.args.get('query')
    print('user_query', user_query)
    # здійснюємо пошук по ключовим словам з допомогою пакету flask_msearch
    result_by_keywords = Post.query.msearch(user_query, limit=20)
    print(result_by_keywords)
    print(type(result_by_keywords))
    result_by_substring = Post.query.filter(
        Post.title.ilike(f'%{user_query}%')
    )
    posts = result_by_keywords.union(result_by_substring)
    posts, sort_by = handle_posts_view(
        posts,
        request.args
    )
    return render_template('search_results.html', title='SearchResults',
                           posts=posts, sort_by=sort_by, query=user_query)
