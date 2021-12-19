from flask import Flask, render_template, request
from flask.helpers import url_for 
from ibm_watson import SpeechToTextV1 
import json
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pandas import json_normalize
import os
from dotenv import load_dotenv 

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=['POST'])

def upload():
    if request.method == 'POST':
        
        url_s2t = os.environ['urls2t']
        iam_apikey_s2t = os.environ['apikey']
        authenticator = IAMAuthenticator(iam_apikey_s2t)
        s2t = SpeechToTextV1(authenticator=authenticator)
        s2t.set_service_url(url_s2t)

        output = request.form["audio"]
        with open(output, mode="rb") as audio:
            response = s2t.recognize(audio = audio, content_type="audio/mp3")
            fulltext = []
            for i in range(len(response.result['results'])):
                fulltext.append(response.result['results'][i]["alternatives"][0]["transcript"].strip())
            
            out = "\n".join(fulltext)

            return render_template("index.html", translation=out)
    

@app.route("/about")
def about():
    return render_template("about.html")


if  __name__ == "__main__":
    app.run(debug=True)