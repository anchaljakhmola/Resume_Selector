import os
import PyPDF2
import textract
import re
import string
import pandas as pd
from enum import unique
from flask import Flask,render_template,request,flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user, logout_user, login_required, UserMixin

app = Flask(__name__)
p='12345'
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/resume_build'%p
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    return render_template("login.html") #,dbData = dbData

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
        user_type = request.form.get('user_type')
        check_user = User.query.filter_by(username=username).first()
        if(check_user is not None):
            if(check_user.password == password and check_user.user_type == user_type):
                login_user(check_user)
                if(str(user_type) == 'recruiter'):
                    return render_template("index.html")
                return render_template("user_seeker.html")
            else:
                return "Incorrect Password"
        else:
            return "No such User exists"
        
def parse_pdf(filepath):
    # Open pdf file
    pdfFileObj = open(filepath,'rb')

    # Read file
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    num_pages = pdfReader.numPages

    # Initialize a count for the number of pages
    count = 0

    # Initialize a text empty etring variable
    text = ""

    # Extract text from every page on the file
    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        count +=1
        text += pageObj.extractText()


    # Convert all strings to lowercase
    text = text.lower()

    # Remove numbers
    text = re.sub(r'\d+','',text)

    # Remove punctuation
    text = text.translate(str.maketrans('','',string.punctuation))


    # Create dictionary with industrial and system engineering key terms by area
    terms = {'SDE':['software','developer','c','c++','java','python',
                                'shell', 'database','scripting','php','node','javascript','systems','algorithm',
                                'data','performance','quality',
                                'sql','mongodb','mysql','networks','iit','iiit','nit',
                                'programming','production','git','bitbucket'],
            'Research Analyst':['research','analytical','conceptual','problem solving','high quality','reliable solutions',
                                'acquisition', 'cross platform','analysis','interpretation','documentation','report','ieee',
                                'publish','conference','paper'],
            'Operations management':['automation','bottleneck','constraints','cycle time','efficiency','fmea',
                                    'machinery','maintenance','manufacture','line balancing','oee','operations',
                                    'operations research','optimization','overall equipment effectiveness',
                                    'pfmea','process','process mapping','production','resources','safety',
                                    'stoppage','value stream mapping','utilization'],
            'Supply chain':['abc analysis','apics','customer','customs','delivery','distribution','eoq','epq',
                            'fleet','forecast','inventory','logistic','materials','outsourcing','procurement',
                            'reorder point','rout','safety stock','scheduling','shipping','stock','suppliers',
                            'third party logistics','transport','transportation','traffic','supply chain',
                            'vendor','warehouse','wip','work in progress'],
            'Project management':['administration','agile','budget','cost','direction','feasibility analysis',
                                'finance','kanban','leader','leadership','management','milestones','planning',
                                'pmi','pmp','problem','project','risk','schedule','scrum','stakeholders'],
            'Data analytics':['analytics','api','aws','big data','busines intelligence','clustering','code',
                            'coding','data','database','data mining','data science','deep learning','hadoop',
                            'hypothesis test','iot','internet','machine learning','modeling','nosql','nlp',
                            'predictive','programming','python','r','sql','tableau','text mining',
                            'visualuzation'],
            'Healthcare':['adverse events','care','clinic','cphq','ergonomics','healthcare',
                        'health care','health','hospital','human factors','medical','near misses',
                        'patient','reporting system']}


    # Initializie score counters for each area
    sde=0
    research=0
    operations = 0
    supplychain = 0
    project = 0
    data = 0
    healthcare = 0

    # Create an empty list where the scores will be stored
    scores = []

    # Obtain the scores for each area
    for area in terms.keys():
        if area == 'SDE':
            for word in terms[area]:
                if word in text:
                    sde +=1
            scores.append(sde)
                
        elif area == 'Research Analyst':
            for word in terms[area]:
                if word in text:
                    research +=1
            scores.append(research)
                    
        elif area == 'Operations management':
            for word in terms[area]:
                if word in text:
                    operations +=1
            scores.append(operations)
            
        elif area == 'Supply chain':
            for word in terms[area]:
                if word in text:
                    supplychain +=1
            scores.append(supplychain)
            
        elif area == 'Project management':
            for word in terms[area]:
                if word in text:
                    project +=1
            scores.append(project)
            
        elif area == 'Data analytics':
            for word in terms[area]:
                if word in text:
                    data +=1
            scores.append(data)
            
        else:
            for word in terms[area]:
                if word in text:
                    healthcare +=1
            scores.append(healthcare)


    # Create a data frame with the scores summary
    summary = pd.DataFrame(scores,index=terms.keys(),columns=['score']).sort_values(by='score',ascending=False)
    summary

    print(summary)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/user_seeker', methods=['GET', 'POST'])
def upload_file():
    if(request.method == 'POST'):
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            summry = parse_pdf(filepath)
            return "Successfully Uploaded"                  #redirect(url_for('download_file', name=filename))
    return "Wrong"

if __name__ == "__main__":
    app.run(debug=True,port=5600)