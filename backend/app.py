from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# 下面这一行就是修复的关键，加上了 jwt_required
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, jwt_required
from flask_bcrypt import Bcrypt
from datetime import datetime
from sqlalchemy import func
import bleach

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)
bcrypt = Bcrypt(app)


# --- 模型 ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(200), default="")
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SiteMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_visits = db.Column(db.Integer, default=0)


class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --- 工具 ---
def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr


# --- CLI ---
@app.cli.command("create-admin")
def create_admin():
    db.create_all()
    if not SiteMeta.query.first():
        db.session.add(SiteMeta(total_visits=0))
    if not User.query.filter_by(username='admin').first():
        hashed_pw = bcrypt.generate_password_hash('admin').decode('utf-8')
        admin = User(username='admin', password=hashed_pw)
        db.session.add(admin)
        print("Admin created.")
    else:
        print("Admin exists.")
    db.session.commit()

@app.cli.command("reset-password")
def reset_password():
    username = input("请输入用户名: ")
    user = User.query.filter_by(username=username).first()
    if not user:
        print("用户不存在")
        return
    new_pass = input("请输入新密码: ")
    user.password = bcrypt.generate_password_hash(new_pass).decode('utf-8')
    db.session.commit()
    print("密码已更新")


# --- 路由 ---

@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        token = create_access_token(identity=username)
        return jsonify(access_token=token)
    return jsonify({"msg": "Bad username or password"}), 401


@app.route('/api/site-info', methods=['GET'])
def site_info():
    meta = SiteMeta.query.first()
    if not meta:
        meta = SiteMeta(total_visits=0)
        db.session.add(meta)

    client_ip = get_client_ip()
    visitor = Visitor.query.filter_by(ip=client_ip).first()

    if not visitor:
        try:
            new_visitor = Visitor(ip=client_ip)
            db.session.add(new_visitor)
            meta.total_visits += 1
            db.session.commit()
        except:
            db.session.rollback()

    categories = db.session.query(Article.category, func.count(Article.category)).group_by(Article.category).all()
    all_articles = Article.query.with_entities(Article.tags).all()
    tag_set = set()
    for a in all_articles:
        if a.tags:
            for t in a.tags.split(','):
                tag_set.add(t.strip())

    return jsonify({
        'visits': meta.total_visits,
        'categories': [{'name': c[0], 'count': c[1]} for c in categories],
        'tags': list(tag_set)
    })

# --- 评论管理接口 ---

@app.route('/api/all-comments', methods=['GET'])
@jwt_required()
def get_all_comments():
    comments = db.session.query(Comment, Article.title).join(Article, Comment.article_id == Article.id).order_by(Comment.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': c.Comment.id,
        'nickname': c.Comment.nickname,
        'content': c.Comment.content,
        'date': c.Comment.created_at.strftime('%Y-%m-%d %H:%M'),
        'article_title': c.title
    } for c in comments])

@app.route('/api/comments/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'msg': 'Deleted'})

# --- 文章接口 ---

@app.route('/api/articles', methods=['GET', 'POST'])
def handle_articles():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        search = request.args.get('q', '')
        category = request.args.get('category', '')

        query = Article.query.order_by(Article.created_at.desc())
        if search:
            query = query.filter(Article.title.ilike(f'%{search}%') | Article.content.ilike(f'%{search}%'))
        if category:
            query = query.filter(Article.category == category)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'articles': [{
                'id': a.id, 'title': a.title, 'category': a.category,
                'tags': a.tags.split(',') if a.tags else [],
                'date': a.created_at.strftime('%Y-%m-%d'),
                'summary': a.content[:100] + '...',
                'views': a.views
            } for a in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next
        })

    verify_jwt_in_request()
    data = request.json
    new_article = Article(
        title=data['title'],
        content=data['content'],
        category=data['category'],
        tags=data.get('tags', '')
    )
    db.session.add(new_article)
    db.session.commit()
    return jsonify({'msg': 'Created'}), 201


@app.route('/api/articles/<int:id>', methods=['GET', 'DELETE', 'PUT'])
def article_detail(id):
    article = Article.query.get_or_404(id)
    if request.method == 'GET':
        article.views += 1
        db.session.commit()
        comments = Comment.query.filter_by(article_id=id).all()
        return jsonify({
            'id': article.id, 'title': article.title, 'content': article.content,
            'category': article.category,
            'tags': article.tags.split(',') if article.tags else [],
            'date': article.created_at.strftime('%Y-%m-%d'),
            'views': article.views,
            'comments': [{'nickname': c.nickname, 'content': c.content} for c in comments]
        })

    verify_jwt_in_request()
    if request.method == 'DELETE':
        db.session.delete(article)
        db.session.commit()
        return jsonify({'msg': 'Deleted'})

    if request.method == 'PUT':
        data = request.json
        article.title = data.get('title', article.title)
        article.content = data.get('content', article.content)
        article.category = data.get('category', article.category)
        article.tags = data.get('tags', article.tags)
        db.session.commit()
        return jsonify({'msg': 'Updated'})


@app.route('/api/articles/<int:id>/comments', methods=['POST'])
def add_comment(id):
    data = request.json
    clean_content = bleach.clean(data['content'])
    comment = Comment(article_id=id, nickname=data['nickname'], content=clean_content)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'msg': 'Comment added'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not SiteMeta.query.first():
            db.session.add(SiteMeta(total_visits=0))
            db.session.commit()
    app.run(debug=True, port=5000)