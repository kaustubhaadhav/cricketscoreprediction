from flask import Flask, render_template, request,session,logging,flash,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail, Message
import os
import secrets
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import pickle
import numpy as np

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__,template_folder='template')
app.secret_key = 'super-secret-key'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = params['admin_user']
app.config['MAIL_PASSWORD'] = params['admin_password']
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']     #linking of sql Database
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)



# this is contact model
class Contact(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)

# this is registeration  model 

    
class Register(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    rno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(12), nullable=False)
    password2 = db.Column(db.String(120), nullable=False)

class Forgetpassword(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String, nullable=False)
    token=db.Column(db.String(50), nullable=False)



@app.route("/")
def home():
    if('email' in session and session['email']):
        return render_template('index.html',params=params)
    else:
        return redirect(url_for('dashboard'))


# this is login code
@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    if('email' in session and session['email']):
        return render_template('dashboard.html',params=params)

    if (request.method== "POST"):
        email = request.form["email"]
        password = request.form["password"]
        
        login = Register.query.filter_by(email=email, password=password).first()
        if login is not None:
            session['email']=email
            return render_template('dashboard.html',params=params)
        else:
            flash("plz enter right password")
    return render_template('login.html',params=params)

# this is register page
@app.route("/register", methods=['GET','POST'])
def register():
    if(request.method=='POST'):
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if (password==password2):
            entry = Register(name=name,email=email,password=password, password2=password2)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:

            flash("plz enter right password")
           
    return render_template('register.html',params=params)


        

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contact(name=name, phone_num = phone, message = message, email = email,date= datetime.now() )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['admin_user']],
                          body = message + "\n" + phone
                          )
    return render_template('contact.html',params=params)
    
# chatbot here code
@app.route("/predict", methods=['GET','POST'])
def predict():
    
    model = pickle.load(open('model.pkl', 'rb'))
    '''for rendering html gui'''
    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)

    output = round(prediction[0], 3)

    return render_template('index.html', prediction_text='cricket score predict should be $ {}'.format(output),params=params)
    '''
    return render_template('index.html',params=params)
    '''
  
@app.route("/logistic", methods=['GET','POST'])
def logistic():
    if(request.method=='POST'):
        import pdb;pdb.set_trace();
        forest_model=pickle.load(open('random_forestmodel.pkl','rb'))
        print(forest_model)
        int_features=[int(x) for x in request.form.values()]
        print(int_features)
        final_features=[np.array(int_features)]
        print(final_features)
        prediction=forest_model.predict(final_features)
        print(prediction)

        output1=round(prediction[0],3)
        print(output1)
        return render_template('logistic.html',prediction_text1='cricket score predict should be $ {}'.format(output1),params=params)
    return render_template('logistic.html',params=params)

@app.route("/logout", methods = ['GET','POST'])
def logout():
    session.pop('email')
    return redirect(url_for('dashboard'))


@app.route("/Cricketwinprediction")
def Cricketwinprediction():
    import PredictTheOutComeUI
    import getStats
    import predict_match
    return render_template("Cricketwinprediction.html",params=params)


@app.route("/forgetpassword", methods = ['GET','POST'])
def forgetpassword():
    if(request.method=='POST'):
        email=request.form.get('email')
        token=secrets.token_urlsafe(5)
        send_reset_email(email,token)
        entry=Forgetpassword(email=email,token=token)
        db.session.add(entry)
        db.session.commit()
        return render_template('mailsuccess.html', params=params)
    else:
        return render_template('forgetpassword.html',params=params)

def send_reset_email(email,token):
    message_body="http://127.0.0.1:5000/reset_password/"+token
    mail.send_message('New message from your email' ,
                          sender="params['admin_user']",
                          recipients = [email],
                          body = message_body 
                          )

@app.errorhandler(404)
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if(request.method=='POST'):
        password=request.form.get('password')
        email=request.form.get('email')
        record=Register.query.filter_by(email=email).first()
        if record:
            record.password=password
            record.password2=password
            db.session.add(record)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            pass
    else:
        record = Forgetpassword.query.filter_by(token=token).first()
        if record:
                 return render_template('resetpassword.html', email=record.email)


if __name__ == "__main__":
    
    app.run(debug=True)
