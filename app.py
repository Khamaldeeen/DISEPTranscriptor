from flask import Flask, render_template, request, flash, redirect
from flask.helpers import url_for 
from ibm_watson import SpeechToTextV1 
import json
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from werkzeug.utils import secure_filename
import os 

UPLOAD_FOLDER = ""
ALLOWED_EXTENSIONS = {'mp3'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


url_s2t = "https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/6378e690-e198-4d68-a82a-209ac3410509"
iam_apikey_s2t = "2q8XjGHDihTDP2egxfI-33vH4JsI1L67xzYCv7sG2nh6"       
authenticator = IAMAuthenticator(iam_apikey_s2t)
s2t = SpeechToTextV1(authenticator=authenticator)
s2t.set_service_url(url_s2t)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=['POST'])

def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 

            
            with open(filename, mode="rb") as wav:
                response = s2t.recognize(audio=wav, content_type="audio/mp3")
                fulltext = []
                for i in range(len(response.result['results'])):
                    fulltext.append(response.result['results'][i]["alternatives"][0]["transcript"].strip())
                wav.close()
                os.remove(filename)
                out = ". ".join(fulltext)
            
                return render_template("index.html", translation=out)

@app.route("/about")
def about():
    return render_template("about.html")


if  __name__ == "__main__":
    app.run(debug=True)