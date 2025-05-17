import os
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Flask 애플리케이션 초기화
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 설정
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///found_items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 데이터베이스 초기화
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 허용 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 모델 정의
class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_location = db.Column(db.String(100), nullable=False)
    storage_location = db.Column(db.String(100), nullable=False)
    found_by_name = db.Column(db.String(100), nullable=False)
    found_by_contact = db.Column(db.String(100), nullable=False)
    acquisition_time = db.Column(db.String(100), nullable=False)
    photo_filename = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<FoundItem {self.id} - {self.item_name}>'

# 메인 페이지 (검색 포함)
@app.route('/')
def index():
    query = request.args.get('q', '').strip()

    if query:
        items = FoundItem.query.filter(
            (FoundItem.item_name.contains(query)) |
            (FoundItem.item_location.contains(query)) |
            (FoundItem.storage_location.contains(query))  # 검색 대상에 포함
        ).all()
    else:
        items = FoundItem.query.all()
        
    return render_template('index.html', items=items)

# 습득물 등록 페이지
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        acquisition_time = request.form['acquisition_time']
        item_location = request.form['item_location']
        storage_location = request.form['storage_location']
        found_by_name = request.form['found_by_name']
        found_by_contact = request.form['found_by_contact']
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
            photo_filename=photo_filename
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

# 관리자 대시보드
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    items = FoundItem.query.all()
    return render_template('admin_dashboard.html', items=items)

# 관리자 삭제
@app.route('/admin/delete/<int:item_id>')
def delete_item(item_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    item = FoundItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# 초기화
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5003)
