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

# 습득물 모델
class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_location = db.Column(db.String(100), nullable=False)
    storage_location = db.Column(db.String(100), nullable=False)
    found_by_name = db.Column(db.String(100), nullable=False)
    found_by_contact = db.Column(db.String(100), nullable=False)
    acquisition_time = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)  # 설명 추가
    photo_filename = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    comments = db.relationship('Comment', backref='found_item', lazy=True, cascade="all, delete-orphan")

# 분실물 모델
class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    lost_location = db.Column(db.String(100), nullable=False)
    lost_by_name = db.Column(db.String(100), nullable=False)
    lost_by_contact = db.Column(db.String(100), nullable=False)
    lost_time = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)  # 설명 추가
    photo_filename = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    comments = db.relationship('Comment', backref='lost_item', lazy=True, cascade="all, delete-orphan")

# 댓글 모델
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String(10), nullable=False)  # 'found' 또는 'lost'
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# 홈 페이지
@app.route('/')
def index():
    view_type = request.args.get('type', 'found')
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()

    if view_type == 'lost':
        items = LostItem.query
        if query:
            items = items.filter(LostItem.item_name.contains(query))
        if category:
            items = items.filter(LostItem.category == category)
        items = items.all()
    else:
        items = FoundItem.query
        if query:
            items = items.filter(FoundItem.item_name.contains(query))
        if category:
            items = items.filter(FoundItem.category == category)
        items = items.all()

    return render_template('index.html', items=items, view_type=view_type, query=query, category=category)

# 댓글 추가
@app.route('/add_comment/<item_type>/<int:item_id>', methods=['POST'])
def add_comment(item_type, item_id):
    author = request.form['author']
    content = request.form['content']
    comment = Comment(item_id=item_id, item_type=item_type, author=author, content=content)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index', type=item_type))

# 습득물 등록
@app.route('/add_found', methods=['GET', 'POST'])
def add_found():
    if request.method == 'POST':
        item_name = request.form['item_name']
        acquisition_time = request.form['acquisition_time']
        item_location = request.form['item_location']
        storage_location = request.form['storage_location']
        found_by_name = request.form['found_by_name']
        found_by_contact = request.form['found_by_contact']
        category = request.form['category']
        description = request.form['description']
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
            category=category,
            description=description,
            photo_filename=photo_filename
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('index', type='found'))
    return render_template('add_found.html')

# 분실물 등록
@app.route('/add_lost', methods=['GET', 'POST'])
def add_lost():
    if request.method == 'POST':
        item_name = request.form['item_name']
        lost_time = request.form['lost_time']
        lost_location = request.form['lost_location']
        lost_by_name = request.form['lost_by_name']
        lost_by_contact = request.form['lost_by_contact']
        category = request.form['category']
        description = request.form['description']
        file = request.files.get('item_photo')

        photo_filename = None
        if file and allowed_file(file.filename):
            photo_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        new_item = LostItem(
            item_name=item_name,
            lost_time=lost_time,
            lost_location=lost_location,
            lost_by_name=lost_by_name,
            lost_by_contact=lost_by_contact,
            category=category,
            description=description,
            photo_filename=photo_filename
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('index', type='lost'))
    return render_template('add_lost.html')

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

# 관리자 대시보드
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    found_items = FoundItem.query.all()
    lost_items = LostItem.query.all()
    return render_template('admin_dashboard.html', found_items=found_items, lost_items=lost_items)

# 관리자 삭제
@app.route('/admin/delete/<item_type>/<int:item_id>')
def delete_item(item_type, item_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if item_type == 'found':
        item = FoundItem.query.get_or_404(item_id)
    else:
        item = LostItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5003)
