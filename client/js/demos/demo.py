import sys

from flask import Flask, render_template

def run():
    app = Flask(
        "Robocapture Client Demos",
        static_folder="static",
        template_folder="templates",
        static_url_path=""
    )

    @app.route("/debug")
    def root():
        return render_template("debug.html")

    app.run(debug=True)

if __name__=="__main__":
    run()
