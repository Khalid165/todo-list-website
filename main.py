from flask import Flask,request,render_template,redirect,url_for,flash
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField,EmailField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user,LoginManager,login_required,logout_user,UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

login_manager=LoginManager()
app=Flask(__name__)
app.config["SECRET_KEY"]="jfhfhfiuewiurgqewiur"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///todo.db"
Bootstrap(app)
db=SQLAlchemy(app)
login_manager.init_app(app)


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(100),nullable=False)
    phone=db.Column(db.String(15),nullable=False,unique=True)
    user_name=db.Column(db.String(100),unique=True,nullable=False)


class na_form(FlaskForm):
    email=EmailField("Email Address",validators=[DataRequired()])
    user_name=StringField("User Name",validators=[DataRequired()])
    phone=StringField("Phone",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField(" Create Account")



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



class todo_db(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user=db.Column(db.String,nullable=False,unique=True)
    todo_1=db.Column(db.String,nullable=True)



class todo_form(FlaskForm):
    todo=StringField("Add new task")
    submit=SubmitField("Ok")


class login_form(FlaskForm):
    user_name=StringField("Email.",validators=[DataRequired()])
    user_password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("LOGIN")

db.create_all()

@app.route("/",methods=["POST","GET"])
def home():
    form=todo_form()
    return render_template("home.html",form=form)

@app.route("/login",methods=["POST","GET"])
def login():
    form=login_form()
    if form.validate_on_submit():
        try:
            user=User.query.filter_by(user=form.user_name.data).first()
            if user:
                if check_password_hash(user.password,form.user_password.data):
                    login_user(user)
                    return redirect(url_for("page",user=user.user.split("@")[0],id=user.id))
                else:
                    flash("Wrong Password")
            else:
                flash("Wrong Email")
        except:
            return None

    return render_template("login.html",form=form)

@app.route("/new_account",methods=["POST","GET"])
def new_account():
    form=na_form()
    if request.method=="POST":
        if form.validate_on_submit():
            hash_pass=generate_password_hash(password=form.password.data,method='pbkdf2:sha256',salt_length=8)
            try:
                new_user=User(user=form.email.data,password=hash_pass,phone=form.phone.data,user_name=form.user_name.data)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for("page",user=new_user.user_name,id=new_user.id))
            except:
                flash('You have account already')
                return redirect(url_for("login"))
    return render_template("new_account.html",form=form)


@app.route("/worker",methods=["POST","GET"])
@login_required
def page():
    form=todo_form()

    if form.validate_on_submit():
        if form.todo.data!="" and form.todo.data!=" ":
            try:
                user_todo=todo_db.query.filter_by(user=request.args.get("user")).first()
                if user_todo.todo_1==None:
                    user_todo.todo_1 = form.todo.data

                else:
                    user_todo.todo_1 += f",{form.todo.data}"

                db.session.commit()
            except:
                user_todo=todo_db(user=request.args.get("user"),todo_1=form.todo.data)
                db.session.add(user_todo)
                db.session.commit()
            return redirect(url_for("page",user=request.args.get('user'),id=request.args.get('id')))
        else:
            pass

    return render_template("index.html",form=form)

@app.route("/logut")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/your_list")
@login_required
def list():
    todo=todo_db.query.get(request.args.get("id"))
    try:
        todo_list=todo.todo_1.split(",")
        if todo_list:
            return render_template("tasks.html",list=todo_list)
    except AttributeError:
        error="You Don't Have any tasks."
        return render_template("tasks.html",error=error)

    return render_template("tasks.html")

@app.route("/delete",methods=["POST","GET"])
def delete_item():
    current_user=todo_db.query.filter_by(user=request.args.get("user")).first()
    current_user_list=current_user.todo_1.split(",")
    if len(current_user.todo_1)>0:

        if request.args.get("done") in current_user_list:
            print(request.args.get("done"))
            print(current_user_list)
            current_user_list.remove(request.args.get("done"))
            new_todo=",".join(current_user_list)
            current_user.todo_1=new_todo
            db.session.commit()
    else:
        current_user.todo_1=None
        db.session.commit()
        print("Hello world")


    return redirect(url_for("list",user=request.args.get('user'),id=request.args.get("id")))




if __name__=="__main__":
    app.run(debug=True)

