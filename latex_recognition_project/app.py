from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
from config import API_TOKEN, API_URL

app = Flask(__name__)

# 配置 SQLite 数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义数据库模型
class ImageRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # 禁用自动递增
    file_path = db.Column(db.String(255), nullable=False)
    formula = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 初始化数据库
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 保存文件到本地
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)  # 创建上传目录（如果不存在）
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # 构造请求数据
    files = {'file': (file.filename, open(file_path, 'rb'), file.content_type)}
    headers = {"token": API_TOKEN}
    data = {}  # 如果需要额外参数，可以在此添加

    try:
        # 调用外部 API
        response = requests.post(API_URL, files=files, data=data, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        # 提取公式部分
        latex_formula = response_data.get('res', {}).get('latex', None)

        # 获取当前最大 ID，确保 ID 重新排序时能正确处理
        max_id = db.session.query(db.func.max(ImageRecord.id)).scalar() or 0

        # 将记录存储到数据库
        new_record = ImageRecord(id=max_id + 1, file_path=file_path, formula=latex_formula)
        db.session.add(new_record)
        db.session.commit()

        return jsonify({'latex': latex_formula})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
    finally:
        files['file'][1].close()  # 关闭文件流

@app.route('/history', methods=['GET'])
def history():
    records = ImageRecord.query.order_by(ImageRecord.timestamp.desc()).all()
    history_data = [
        {'id': record.id, 'file_path': record.file_path, 'formula': record.formula, 'timestamp': record.timestamp}
        for record in records
    ]
    return jsonify(history_data)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        num_deleted = db.session.query(ImageRecord).delete()
        db.session.commit()
        return jsonify({'status': 'success', 'deleted_records': num_deleted})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete_record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    try:
        # 删除指定记录
        record = ImageRecord.query.get(record_id)
        if not record:
            return jsonify({'status': 'error', 'message': 'Record not found'}), 404

        db.session.delete(record)
        db.session.commit()

        # 重新排序ID
        records = ImageRecord.query.order_by(ImageRecord.timestamp).all()
        for index, record in enumerate(records, start=1):
            record.id = index
        db.session.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True,port=5001)