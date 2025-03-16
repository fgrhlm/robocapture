import sys
import os
import shutil

from flask import Flask, render_template
from livereload import Server

def run():
    app = Flask(
        "Robocapture Client Demos",
        static_folder="static",
        template_folder="templates",
        static_url_path=""
    )

    app.debug = True

    @app.route("/debug")
    def root():
        return render_template("debug.html")

    @app.route("/hotword")
    def hotword_detection():
        return render_template("hotword_detection.html")

    @app.route("/human")
    def human_recognition():
        return render_template("human_detection.html")

    server = Server(app.wsgi_app)
    server.watch(".")
    server.serve()

if __name__=="__main__":
    print(f"Copying robocapture client..")
    client_src = os.path.join("../","robocapture.js")
    client_dst = os.path.join("static", "js", "robocapture.js")

    shutil.copyfile(client_src, client_dst)
    run()
