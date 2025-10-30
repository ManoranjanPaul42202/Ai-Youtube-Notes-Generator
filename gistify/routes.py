import secrets
import os
from PIL import Image
from flask import render_template, url_for, redirect, flash, request, jsonify, session
from gistify import app, db, bcrypt
from gistify.form import RegistrationForm, loginForm, UpdateAccountForm, LinkForm, GenerateNotesForm
from gistify.model import User, Note
from flask_login import login_user, logout_user, current_user, login_required
from gistify.audio_transcription import generate_transcript
from gistify.notes_generator import NotesGenerator

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static','images','profile_images', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

def get_or_create_note(url, user_id, title="YouTube Note", cookies_path=None):
    note = Note.query.filter_by(yt_link=url).first()
    if note:
        return {
            "transcription": note.content,
            "segments": eval(note.time_stamps),
            "language": note.language,
            "cached": True
        }

    # Generate new transcription
    result = generate_transcript(url, cookies_path=cookies_path)
    if "error" in result:
        return result

    transcription_text = result.get("transcription", "")
    segments = result.get("segments", [])
    language = result.get("language", "unknown")

    new_note = Note(
        title=title,
        yt_link=url,
        language=language,
        time_stamps=str(segments),
        content=transcription_text,
        user_id=user_id
    )
    db.session.add(new_note)
    db.session.commit()

    return {
        "transcription": transcription_text,
        "segments": segments,
        "language": language,
        "cached": False
    }

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def hello():
    form = LinkForm()
    if form.validate_on_submit():
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        link = form.link.data
        save_path = None

        cookie_file = form.cookies_file.data
        if cookie_file:
            save_path = os.path.join(BASE_DIR, 'cookies.txt')
            cookie_file.save(save_path)
            print("Saved cookies to", save_path)

        # Save to session instead of URL
        session['cookies_path'] = save_path

        return redirect(url_for('dashboard', link=link))

    return render_template(
        'home.html',
        title="Gistify - AI YouTube Notes Generator",
        css='home.css',
        form=form
    )


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password, preference=form.preference.data, 
                    tone=form.tone.data)
        db.session.add(user)
        db.session.commit()
        flash(f"You're all set! Log in to continue.", "success")
        return redirect(url_for("login"))
    return render_template('register.html', title='Register', form=form, css='register.css')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = loginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash("Bad credentials, Check email or password !!", "danger")
    return render_template('login.html', title='Login', form=form, css="register.css")

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    form = LinkForm()
    notes_form = GenerateNotesForm()
    if form.validate_on_submit():
        link = form.link.data
        return redirect(url_for('dashboard', link=link))
    link = request.args.get('link')
    cookies_file_path = request.args.get('save_path')

    # Extract video ID for embedding
    video_id = None
    if link and link.lower() != "none":
        if "watch?v=" in link:
            video_id = link.split("watch?v=")[-1]
        elif "youtu.be/" in link:
            video_id = link.split("youtu.be/")[-1]
    
    return render_template(
        'dashboard.html',
        title='Dashboard',
        form=form,
        notes_form = notes_form,
        video_id=video_id,
        link=link,
        cookies_file_path=cookies_file_path,
        css='dashboard.css'
    )

@app.route("/get_transcription", methods=['GET'])
@login_required
def get_transcription():
    link = request.args.get("link")
    session['link'] = link
    cookies_file_path = session.get('cookies_path')

    if link == "None":
        return jsonify({"transcription": "", "segments": [], "error": "Provide a link to get started"})
    if not link:
        return jsonify({"transcription": "", "segments": [], "error": "No link provided."})
    
    result = get_or_create_note(link, 
                                current_user.id, 
                                title="Youtube Note", 
                                cookies_path=cookies_file_path)    

    # result = generate_transcript(link, cookies_path=cookies_file_path, return_segments=True)

    if "error" in result:
        return jsonify(result)
    
    # Extract clean segments
    clean_segments = []
    for seg in result.get("segments", []):
        clean_segments.append({
            "start": seg.get("start", 0),
            "end": seg.get("end", 0),
            "text": seg.get("text", "")
        })

    return jsonify({
        "transcription": result.get("transcription", ""),
        "segments": clean_segments
    })

@app.route("/generate_notes", methods=['POST'])
@login_required
def generate_notes():
    url = session.get('link')
    print(f"[DEBUG] Generating notes for: {url}")
    note = Note.query.filter_by(yt_link=url).first()

    if note is None or not note.content:
        return jsonify({"error": "No transcription found. Please generate transcription first."}), 400

    transcript_text = note.content

    # Get style and topic from the form data
    style = current_user.preference
    topic = request.form.get("topic", "").strip()

    try:
        # Generate notes using your NotesGenerator class
        notes_generator = NotesGenerator()
        notes_text = notes_generator.generate_notes(
            transcript_text=transcript_text,
            style=style
            # topic=topic
        )

        # Store the generated notes in session for future download/export
        session["generated_notes"] = notes_text

        return jsonify({
            "success": True,
            "notes": notes_text,
            "style": style
        })

    except Exception as e:
        print(f"[ERROR] Note generation failed: {e}")
        return jsonify({"error": str(e)}), 500



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('hello'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    print("Route hit. Method:", request.method)
    print("Form submitted:", form.is_submitted())
    print("Form validate_on_submit:", form.validate_on_submit())
    print("Form errors:", form.errors)
    if form.validate_on_submit():
        print("FORM")
        if form.picture.data:
            picture_name = save_picture(form.picture.data)
            print(picture_name)
            if picture_name:
                current_user.image_file = picture_name
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.preference = form.preference.data
        current_user.tone = form.tone.data
        db.session.commit()
        flash(f"Your account has been successfully updated", 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.preference.data = current_user.preference
        form.tone.data = current_user.tone
    user_image = url_for("static", 
                         filename="images/profile_images/" + current_user.image_file)
    return render_template('account.html', title='Account', 
                           user_image = user_image, form=form, css='register.css')
