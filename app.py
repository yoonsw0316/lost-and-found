import os
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 설정
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///found_items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB 설정
db = SQLAlchemy(app)
migrate = Migrate(app, db)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ FoundItem 모델
class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_location = db.Column(db.String(100), nullable=False)
    storage_location = db.Column(db.String(100), nullable=False)
    found_by_name = db.Column(db.String(100), nullable=False)
    found_by_contact = db.Column(db.String(100), nullable=False)
    acquisition_time = db.Column(db.String(100), nullable=False)
    photo_filename = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    comments = db.relationship('Comment', backref='item', lazy=True, cascade="all, delete-orphan")

# ✅ Comment 모델 추가
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('found_item.id'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# 메인 페이지
@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '')
    items_query = FoundItem.query

    if query:
        items_query = items_query.filter(
            (FoundItem.item_name.contains(query)) |
            (FoundItem.item_location.contains(query)) |
            (FoundItem.storage_location.contains(query))
        )
    
    if category_filter:
        items_query = items_query.filter(FoundItem.category == category_filter)

    items = items_query.all()
    return render_template('index.html', items=items, query=query, selected_category=category_filter)

# 댓글 추가 라우트
@app.route('/add_comment/<int:item_id>', methods=['POST'])
def add_comment(item_id):
    author = request.form['author']
    content = request.form['content']
    comment = Comment(item_id=item_id, author=author, content=content)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index'))

# 습득물 등록
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        acquisition_time = request.form['acquisition_time']
        item_location = request.form['item_location']
        storage_location = request.form['storage_location']
        found_by_name = request.form['found_by_name']
        found_by_contact = request.form['found_by_contact']
        category = request.form['category']
        file = request.files.get('item_photo')
        photo_filename = None

        if file and allowed_file(file.filename):
            photo_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        new_item = FoundItem(
            item_name=item_name,
            acquisition_time=acquisition_time,
            item_location=item_location,
            storage_location=storage_location,
            found_by_name=found_by_name,
            found_by_contact=found_by_contact,
            photo_filename=photo_filename,
            category=category
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html')

# 관리자 로그인
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'jhysw' and password == '30506':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return '로그인 실패'
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    items = FoundItem.query.all()
    return render_template('admin_dashboard.html', items=items)

@app.route('/admin/delete/<int:item_id>')
def delete_item(item_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    item = FoundItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# 앱 실행
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5003)