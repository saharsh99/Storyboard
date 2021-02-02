from flask import Flask, render_template, flash, redirect, url_for, session, request,logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from ocr import ocr_core

UPLOAD_FOLDER = '/static/uploads/'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'storyboard'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def allowed_file(filename):  
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
@is_logged_in
def articles():
    cur = mysql.connection.cursor()

    result = cur.execute("select * from articles where status='public'")
    
    articles = cur.fetchall()

    if result>0:
        return render_template('articles.html',articles=articles)

    else:
        msg = 'No articles found'
        return render_template('articles.html',msg=msg)

        
    cur.close()

@app.route('/article/<string:id>/')
@is_logged_in
def article(id):
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()

    return render_template('article.html', article=article)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        mysql.connection.commit()

        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * from users where username = %s",[username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)

            cur.close()
        
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')



@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are logged out','success')
    return redirect(url_for('login'))




@app.route('/dashboard')
@is_logged_in
def dashboard():

    cur = mysql.connection.cursor()
    
    result = cur.execute("select * from articles where author = %s",(session['username'],))
    
    articles = cur.fetchall()

    if result>0:
        return render_template('dashboard.html',articles=articles)

    else:
        msg = 'No articles found'
        return render_template('dashboard.html',msg=msg)


    cur.close()

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/add_article', methods = ['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO ARTICLES(title,body, author) values ( %s,%s,%s)",(title, body, session['username']))

        mysql.connection.commit()

        cur.close()

        flash('Article created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form = form)

@app.route('/edit_article/<string:id>', methods = ['GET','POST'])
@is_logged_in
def edit_article(id):
    cur = mysql.connection.cursor()

    result = cur.execute("Select * from articles where id = %s",[id])

    article = cur.fetchone()


    form = ArticleForm(request.form)

    form.title.data = article['title']
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        cur = mysql.connection.cursor()

        cur.execute("Update articles set title=%s, body=%s where id=%s",(title, body, id))

        mysql.connection.commit()

        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form = form)


@app.route('/delete_article/<string:id>',methods=['POST'])
@is_logged_in
def delete_article(id):
    cur = mysql.connection.cursor()
    cur.execute("Delete from articles where id=%s",[id])

    mysql.connection.commit()
    cur.close()
    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['GET', 'POST'])
@is_logged_in
def upload_page():  
    
    form = ArticleForm(request.form)
    if request.method == 'POST' and not form.validate():
        if 'file' not in request.files:
            return render_template('upload.html', msgforupload='No file selected')
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', msgforupload='No file selected')

        if file and allowed_file(file.filename):
            extracted_text = ocr_core(file)
            form.body.data = extracted_text
            return render_template('upload.html', form=form, text=extracted_text)

    # elif request.method == 'GET':
    #     return render_template('upload.html')

    if request.method == 'POST' and form.validate():
        title = form.title.data
        
        body = form.body.data
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO ARTICLES(title,body, author) values ( %s,%s,%s)",(title, body, session['username']))

        mysql.connection.commit()

        cur.close()

        flash('Article created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('upload.html', form = form)



# @app.route('/addwithOCR', methods = ['GET','POST'])
# @is_logged_in
# def addwithOCR():
#     form = ArticleForm(request.form)
#     if request.method == 'POST' and form.validate():
#         title = form.title.data
#         body = form.body.data
#         cur = mysql.connection.cursor()

#         cur.execute("INSERT INTO ARTICLES(title,body, author) values ( %s,%s,%s)",(title, body, session['username']))

#         mysql.connection.commit()

#         cur.close()

#         flash('Article created', 'success')

#         return redirect(url_for('dashboard'))
#     return render_template('addwithOCR.html', form = form)

if __name__ == '__main__':
    app.secret_key='secretkey'
    app.run(debug=True)