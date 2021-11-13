from enum import unique
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin, login_manager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///resumeData.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secrethaibhai'
db = SQLAlchemy(app)

# login_manager = LoginManager()
# login_manager.init_app(app)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(120), unique = True)
    email = db.Column(db.String(120),nullable = False)

    def __init__(self, username, password, email):
        self.username = username
        self.email = email
        self.password = password
        
db.create_all()
# _user = User('admin', 'admin123', 'admin@example.com')
# db.session.add(_user)
# db.session.commit()
dbData = User.query.all()
# db.session.add(_user)
# db.session.commit()

@app.route("/")
def hello_world():
    # _user = User('admin', 'admin123', 'admin@example.com')
    # db.create_all()
    # db.session.add(_user)
    # db.session.commit()
    # dbData = User.query.all()
    return render_template("index.html") #,dbData = dbData

@app.route("/About")
def aboutUs():
    return "<p>My name is this this,!</p>"

if __name__ == "__main__":
    app.run(debug=True,port=5600)