from flask import Flask, render_template, request, redirect, url_for, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import (
    Form, PasswordField, TextField,
    ValidationError, SelectMultipleField, SubmitField,
    Required
)
from sqlalchemy import or_
import re
from flask.ext.login import (
    LoginManager, login_required,
    login_user, logout_user, AnonymousUser
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/flaskr.db'
db = SQLAlchemy(app)

SECRET_KEY = "blablabla"
DEBUG = True

app.config.from_object(__name__)

login_manager = LoginManager()


class Anonymous(AnonymousUser):
    name = u"Anonymous"


login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.setup_app(app)


authors_books = db.Table('authors_books', db.Column('book_id', db.Integer, db.ForeignKey('book.id')), \
    db.Column('author_id', db.Integer, db.ForeignKey('author.id')))


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    books = db.relationship('Book', secondary=authors_books, backref=db.backref('authors'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Author %r>' % (self.name)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return '<Book %r>' % (self.title)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    is_active = db.Column(db.Boolean, unique=False, default=True)

    def __init__(self, email, password, is_active=True):
        self.email = email
        self.password = password
        self.is_active = True

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def get_user(email, password):
        return (
            User.query
            .filter(User.email == email)
            .filter(User.password == password)
            .first()
        )

    def __repr__(self):
        return '<User %r>' % (self.email)


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = AuthorizationForm(request.form)
    if form.validate():
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.get_user(email, password)
        if user:
            login_user(user, remember="yes")
            return redirect(url_for("show_books"))
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/authors')
def show_authors():
    authors = Author.query.all()
    return render_template('show_authors.html', authors=authors)


@app.route('/books')
def show_books():
    books = Book.query.all()
    return render_template('show_books.html', books=books)


@app.route('/add_author', methods=['POST'])
@login_required
def add_author():
    form = AuthorForm(request.form)
    if form.validate():
        name = request.form.get('name')
        author = Author(name)
        db.session.add(author)
        db.session.commit()
    return redirect(url_for('show_authors'))


@app.route('/search', methods=['GET'])
def search_authors_books():
    text = request.args.get('text', 0, type=str)
    form = SearchForm()
    if text:
        books = Book.query.filter(or_(Book.title.like("%" + text + "%"), \
            Book.authors.any(Author.name.like("%" + text + "%")))).all()
    else:
        books = None
    return render_template('show_search.html', books=books,  form=form)


@app.route('/edit/book/', methods=['GET', 'POST'])
@app.route('/edit/book/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id=None):
    book = Book.query.get(id) if id else None
    if request.method == 'POST':
        form = BookForm(request.form)
        if not book:
            book = Book(None)
        form.populate_obj(book)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('show_books'))
    form = BookForm(obj=book)
    return render_template('edit_book.html', book=book,  form=form)


@app.route('/edit/author/', methods=['GET', 'POST'])
@app.route('/edit/author/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_author(id=None):
    author = Author.query.get(id) if id else None
    if request.method == 'POST':
        form = AuthorForm(request.form)
        form.populate_obj(author)
        db.session.add(author)
        db.session.commit()
        return redirect(url_for('show_authors'))
    form = AuthorForm(obj=author)
    return render_template('edit_author.html', author=author,  form=form)


@app.route('/delete_author/<author_id>')
@login_required
def delete_author(author_id):
    author = Author.query.get(author_id)
    if author:
        db.session.delete(author)
        db.session.commit()
    return redirect(url_for('show_authors'))


@app.route('/delete_book/<book_id>')
@login_required
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for('show_books'))


class AuthorizationForm(Form):
    email = TextField(u'Email', [Required()])
    password = PasswordField(u'Password', [Required()])
    go = SubmitField(u'Go')

    def validate_email(form, field):
        if not bool(re.match("^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", field.data)):
            raise ValidationError('Name must be not empty')

    def validate_password(form, field):
        if not bool(re.match("(?!^[0-9]*$)(?!^[a-zA-Z]*$)^([a-zA-Z0-9]{8,16})$", field.data)):
            raise ValidationError('Name must be not empty')


class AuthorForm(Form):
    name = TextField(u'Author name', [Required()])
    save = SubmitField(u'Save')


class BookForm(Form):
    title = TextField(u'title', [Required()])
    authors = SelectMultipleField(u'Authors', coerce=int)
    save = SubmitField(u'Save')

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        obj = kwargs.get('obj')
        self.authors.choices = \
            [(author.id, author.name) for author in Author.query.all()]
        if obj:
            selected_authors_ids = [author.id for author in obj.authors]
            self.title.data = obj.title
            self.authors.data = selected_authors_ids

    def populate_obj(self, obj):
        obj.title = self.title.data
        author_ids = self.authors.data
        obj.authors = Author.query.filter(Author.id.in_(author_ids)).all()


class SearchForm(Form):
    text = TextField(u'Text', [Required()])
    search = SubmitField(u'Search')


if __name__ == '__main__':
    app.run(debug=True)
