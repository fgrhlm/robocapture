import sys
import os
import json

from time import sleep
from queue import SimpleQueue
from flask import Flask, Response, render_template, stream_with_context
from flask_cors import CORS

if __name__=="__main__":
    app = Flask(__name__, template_folder="templates")
    CORS(app)
    
    @app.route("/")
    def index():
        return render_template("demo.html")

    app.run(debug=True)
