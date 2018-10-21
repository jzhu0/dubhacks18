from flask import Flask, flash, render_template, request, redirect, url_for
app = Flask(__name__)
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'videos'
ALLOWED_EXTENSIONS = set(['mp4', 'mov', 'wav'])
fileUploaded = False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    global fileUploaded
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            fileUploaded = True
            return redirect(url_for('hello_world'))
    return render_template("index.html", fileUploaded=fileUploaded)
