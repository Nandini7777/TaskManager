from flask import Flask, render_template, redirect, request, session
from cs50 import SQL
from functools import wraps


app = Flask(__name__)

app.secret_key = 'supersecretkey'
db = SQL("sqlite:///users.db")

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    user_id = session.get('user_id')   
    data = db.execute("SELECT * FROM tasks WHERE user_id = ?", user_id)   
    #  ORDER BY due_date
    return render_template('home.html', data=data, num=len(data))
# if __name__ == 'main':
#     app.run(debug = True)

@app.route('/register')
def reg():
    return render_template('register.html') 

@app.route('/login', methods=['POST', "GET"]) 
def login():
    if request.method == "GET":
        return render_template("login.html")
    email = request.form.get("email")
    password = request.form.get("password")
    if not email or not password:
        return render_template("error.html")
    res = db.execute("SELECT * FROM users WHERE email = ? AND password = ?", email, password)
    if not res:
        return render_template("error.html")   
    user_id = res[0]['user_id']
    session['user_id'] = user_id 
    return redirect("/")   

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    if not email or not password or not confirm_password:
        return render_template("error.html")
    if password != confirm_password:
        return render_template("error.html")
    res = db.execute("SELECT * FROM users WHERE email = ?", email)
    if res:
        return render_template("error.html")     
    db.execute("INSERT INTO users(email, password) VALUES (?, ?)", email, password)
    return redirect('/login') 

@app.route('/add', methods=['POST'])
def add():
    description = request.form.get('description')
    due_date = request.form.get('due_date')
    priority = request.form.get('priority')
    if not description or not due_date:
        return render_template("error.html")
    user_id = session.get('user_id')       
    db.execute("INSERT INTO tasks (due_date, priority, description, user_id) VALUES (?, ?, ?, ?)", due_date, priority, description, user_id)    
    # data = db.execute("SELECT * FROM tasks WHERE user_id = ?", user_id)
    # print(data)
    return redirect('/')

@app.route('/remove/<id>', methods=['GET'])
def remove(id):
    db.execute("DELETE FROM tasks WHERE task_id = ?", id)
    print(id)
    return "hi"

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')
