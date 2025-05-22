def register_routes(app):
    @app.route("/api/hello")
    def hello():
        return {"message": "Hello from wx PWA backend!"}
