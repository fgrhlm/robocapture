from flask import Flask, render_template


if __name__=="__main__":
    app = Flask(
        "Debug Demo Server",
        static_folder="static",
        template_folder="templates",
        static_url_path=""
    )
    
    @app.route("/")
    def root():
        return render_template("index.html")
    
    app.run(debug=True)
