from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Entry
from .forms import SignupForm, LoginForm, TwoFactorForm, EntryForm
from .utils import send_verification_code, get_stored_code, clear_stored_code
from . import db, login_manager

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def red():
    return redirect(url_for('main.login'))


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.')
            return redirect(url_for('main.signup'))

        user = User(
            username=form.username.data,
            phone_number=form.phone_number.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Signup successful. Please log in.')
        return redirect(url_for('main.login'))
    return render_template('signup.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            session['pre_2fa_user'] = user.username
            print("Login success:", user.username)
            send_verification_code(user.phone_number, user.username)
            return redirect(url_for('main.verify'))

        flash('Invalid credentials.')
    else:
        if request.method == 'POST':
            print("Form did not validate")
            print("Form errors:", form.errors)

    return render_template('login.html', form=form)

@main.route('/verify', methods=['GET', 'POST'])
def verify():
    form = TwoFactorForm()
    username = session.get('pre_2fa_user')
    if not username:
        return redirect(url_for('main.login'))

    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Verification failed.')
        return redirect(url_for('main.login'))

    if form.validate_on_submit():
        code = get_stored_code(username)
        if form.code.data == code:
            login_user(user)
            clear_stored_code(username)
            session.pop('pre_2fa_user', None)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Incorrect code.')
    return render_template('verify.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    query = request.args.get('q', '')
    entries = Entry.query.filter(
        Entry.user_id == current_user.id,
        Entry.title.contains(query)
    ).order_by(Entry.creation_time.desc()).all()
    return render_template('dashboard.html', entries=entries, query=query)


@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_entry():
    form = EntryForm()
    if form.validate_on_submit():
        entry = Entry(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        flash('Entry created.')
        return redirect(url_for('main.dashboard'))
    return render_template('create_entry.html', form=form)

@main.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id :
        flash("You don't have permission to delete this entry.")
        return redirect(url_for('main.dashboard'))

    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted.')
    return redirect(url_for('main.dashboard'))


