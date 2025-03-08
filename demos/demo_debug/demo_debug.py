from flask import Flask

if __name__=="__main__":
    app = Flask("Debug Demo Server")
    
    @app.route("/")
    def root():
        return "Hello!"
    
    app.run(debug=True)
