from app.user.models import Post
from flask import current_app


def sort_posts(posts, sort_by):
    # print('sort_posts')
    if sort_by == 'best':
        # print('best')
        return posts.order_by(
            (Post.total_likes - Post.total_dislikes).desc(),
            Post.total_likes.desc(),
            Post.created_at.desc()
        )
    elif sort_by == 'oldest':
        # print('oldest')
        return posts.order_by(Post.created_at.asc())
    else:
        # print('newest')
        return posts.order_by(Post.created_at.desc())


def handle_posts_view(posts, request_args):
    page = request_args.get('page', 1, type=int)
    sort_by = request_args.get('sort_by', 'newest', type=str)

    posts = sort_posts(posts, sort_by)
    posts = posts.paginate(page=page,
                           per_page=current_app.config['NUM_PER_PAGE'])

    return posts, sort_by
