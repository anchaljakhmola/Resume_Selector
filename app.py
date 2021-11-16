from enum import unique
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user, logout_user, login_required, UserMixin

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/resume_build'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secrethaibhai'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin,db.Model):
    user_type = db.Column(db.String(80))
    username = db.Column(db.String(80),primary_key = True)
    password = db.Column(db.String(120))
    
    def get_id(self):
           return (self.username)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
        
# _user = User('admin', 'admin123', 'admin@example.com')
# db.session.add(_user)
# db.session.commit()
#dbData = user.query.all()
# db.session.add(_user)
# db.session.commit()

@app.route("/")
def index():
    # _user = User('admin', 'admin123', 'admin@example.com')
    # db.create_all()
    # db.session.add(_user)
    # db.session.commit()
    # dbData = User.query.all()
    return render_template("index.html") #,dbData = dbData

@app.route('/signup',methods = ['GET', 'POST'])
def signup():
     return render_template("signup.html")
 
@app.route('/do_signup',methods = ['GET', 'POST'])
def do_signup():
    if(request.method=='POST'):
        username = request.form.get('username')
        user_type = request.form.get('user_type')
        password = request.form.get('password')
        check_user = User.query.filter_by(username=username).first()
        if(check_user is not None):
            return "User already registered, please sign in"
        else:
            user = User(user_type=user_type, username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return render_template("login.html")

@app.route('/login',methods = ['GET', 'POST'])
def login():
     return render_template("login.html")
 
 
@app.route('/do_login',methods = ['GET', 'POST'])
def do_login():
     if(request.method=='POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        check_user = User.query.filter_by(username=username).first()
        if(check_user is not None):
            if(check_user.password == password):
                login_user(check_user)
                return render_template("index.html")
            else:
                return "Incorrect Password"
        else:
            return "No such User exists"

if __name__ == "__main__":
    app.run(debug=True,port=5600)