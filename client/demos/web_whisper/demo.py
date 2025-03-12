import sys

from flask import Flask, render_template

def run(host, port):
    app = Flask(
        "Debug Demo Server",
        static_folder="static",
        template_folder="templates",
        static_url_path=""
    )

    @app.route("/")
    def root():
        return render_template("index.html", host=host, port=port)

    app.run(debug=True)

if __name__=="__main__":
    if len(sys.argv) < 3:
        print("usage: python demo.py <host> <port>")
        sys.exit(0)

    host = sys.argv[1]
    port = sys.argv[2]

    run(host, port)
