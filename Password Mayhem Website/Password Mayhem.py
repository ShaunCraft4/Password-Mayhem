from flask import Flask, render_template, request, redirect, url_for, session, flash
import shelve
import random
from functools import wraps


app = Flask(__name__)
app.secret_key = 'MyNameIsNotShaunCraft440'  
passwords = shelve.open("PasswordStorageFile", writeback=True)


def check_password_strength(password):
    score=0
    advice="Try having: "
    if len(password)>12:
        score+=1
    else:
        advice+=" -more than 12 characters."
    d = {"UpperCase":0,"LowerCase":0,"Digits":0,"SpecialCharacters":0}
    for char in password:
        if char.isupper():
            d["UpperCase"]+=1
        elif char.islower():
            d["LowerCase"]+=1
        elif char.isdigit():
            d["Digits"]+=1
        elif not char.isalnum():
            d["SpecialCharacters"]+=1
    for key, value in d.items():
        if value>0:
            score+=1
        else:
            if key=="UpperCase":
                advice+=" -more uppercase letters."
            elif key=="LowerCase":
                advice+=" -more lowercase letters."
            elif key=="Digits":
                advice+=" -more numbers."
            elif key=="SpecialCharacters":
                advice+=" -more special characters."
    return score,advice


def create_random_password(length):
    cases=["ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz","1234567890","!@#$%^&*(){}[];':|<>?,./"]
    password=""
    while True:
        password=''.join(random.choice(random.choice(cases)) for _ in range(length))
        score=check_password_strength(password)[0]
        if score==5:
            return password


def login_required(f):
    @wraps(f)
    def decorated_function(*arguments,**kwargs):
        if 'username' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('login'))
        return f(*arguments,**kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        score,advice=check_password_strength(password)
        if username in passwords:
            flash('Username already exists!','error')
        elif score==5 or (score < 5 and request.form.get('proceed')=='Y'):
            passwords[username]=[password,{}]
            flash('Account registered successfully!','success')
            return redirect(url_for('login'))
        else:
            flash('Password is not strong enough! Advice: '+advice,'error')
    return render_template('signup.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if username in passwords and passwords[username][0]==password:
            session['username']=username
            flash('Login successful!','success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!','error')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html',passwords=passwords[session['username']][1])


@app.route('/check_password',methods=['GET','POST'])
def check_password():
    if request.method=='POST':
        password=request.form['password']
        score,advice=check_password_strength(password)
        flash(f'Password Score:{score*20}/100','info')
        if score<5:
            flash('Advice: '+advice,'error')
    return render_template('check_password.html')


@app.route('/generate_password',methods=['GET','POST'])
def generate_password():
    generated_password=None
    if request.method=='POST':
        length=int(request.form['length'])
        if length>12:
            generated_password=create_random_password(length)
            flash('Password generated successfully!','success')
        else:
            flash('Password length should be more than 12 characters','error')
    return render_template('generate_password.html',generated_password=generated_password)


@app.route('/add_password',methods=['GET','POST'])
def add_password():
    if request.method=='POST':
        site_name=request.form['site_name']
        password=request.form['password']
        score,advice=check_password_strength(password)
        if score==5 or (score<5 and request.form.get('proceed')=='Y'):
            passwords[session['username']][1][site_name]=password
            flash('Password added successfully!','success')
            return redirect(url_for('dashboard'))
        else:
            flash('Password is not strong enough! Advice: '+advice,'error')
    return render_template('add_password.html')


@app.route('/update_password',methods=['GET','POST'])
def update_password():
    if request.method=='POST':
        site_name=request.form['site_name']
        new_password=request.form['new_password']
        score, advice=check_password_strength(new_password)
        if site_name in passwords[session['username']][1]:
            if score==5 or (score<5 and request.form.get('proceed')=='Y'):
                passwords[session['username']][1][site_name]=new_password
                flash('Password updated successfully!','success')
                return redirect(url_for('dashboard'))
            else:
                flash('Password is not strong enough! Advice: '+ advice,'error')
        else:
            flash('Site not found!','error')
    return render_template('update_password.html')


@app.route('/delete_password',methods=['GET', 'POST'])
def delete_password():
    if request.method=='POST':
        site_name=request.form['site_name']
        if site_name in passwords[session['username']][1]:
            del passwords[session['username']][1][site_name]
            flash('Password deleted successfully!','success')
        else:
            flash('Site not found!','error')
    return render_template('delete_password.html')


@app.route('/delete_account',methods=['POST'])
def delete_account():
    del passwords[session['username']]
    session.pop('username')
    flash('Account deleted successfully!','success')
    return redirect(url_for('signup'))


@app.route('/logout')
def logout():
    session.pop('username',None)
    flash('Logged out successfully!','success')
    return redirect(url_for('login'))



if __name__=='__main__':
    app.run(debug=True)
