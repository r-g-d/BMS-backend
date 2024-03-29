from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import  datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    sno = db.Column(db.Integer , primary_key=True)
    title = db.Column(db.String(200) , nullable=False)
    desc = db.Column(db.String(500) ,  nullable=False)
    date_created = db.Column(db.DateTime , default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"
    
@app.route("/")
def hello_world():
    return render_template('index.html')
    #return "Hello, World!"

@app.route("/products")
def products():
    return "This is products page"

    
def initialize_database():
    with app.app_context():
        try:
            db.create_all()
            print("Database initialized.")
        except Exception as e:
            print(f"An error occurred while initializing the database: {e}")

if __name__ == '__main__':
    initialize_database()
    app.run(host='0.0.0.0', debug=True, port=5000)