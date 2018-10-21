from flask import Flask, flash, render_template, request, redirect, url_for
app = Flask(__name__)
import os
import subprocess
import requests
from werkzeug.utils import secure_filename
from audio_to_txt import process_vid

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
            output_file = 'resources/genesis0.txt'

            process_vid('videos/' + filename, output_file)

            summary = get_summary(output_file, "summary.txt")
            summary = summary.replace("<b>", "")
            summary = summary.replace("</b>", "")
            summary = summary.replace(":", ".")
            summary = summary.replace('"', "")
            summary = summary.replace("'", "")
            print(summary)
            
            subprocess.call('say \"' + summary + '"', shell=True)

            return redirect(url_for('hello_world'))
    return render_template("index.html")


def get_summary(file, output_file):
    API_KEY = "7492989d-6d23-4b32-9b6e-badcd5aef8c4"
    files = {'upload_file': open(file,'rb')}

    n_url = "http://api.intellexer.com/summarizeFileContent?apikey=" + API_KEY + "&fileName=" + file + "&fileSize=100000&summaryRestriction=10&returnedTopicsCount=3&loadConceptsTree=true&loadNamedEntityTree=true&conceptsRestriction=7&structure=general&fullTextTrees=true&textStreamLength=100000000"
    response = requests.post(n_url, files=files)

    r = response.json()
    print(r)
    print(r['items'])
    text = "This is a summary of "
    title = r['summarizerDoc']['title']
    if title:
        text += title
    else:
        text += "the video. "
    if r['topics']:
        text += "The topics that are covered by the video are: "
        for topic in r['topics']:
            text += topic.replace('.', ' and ') + ", "
        text += ". "
    text += "These are the " + str(len(r['items'])) + " key sentences in the video: "

    for item in r['items']:
        if not any(char.isdigit() for char in item['text']):
            text += item['text'] + " "


    text += "This is the end of the summary."
    with open(output_file, 'w+') as outf:
        outf.write(text)
    return text
