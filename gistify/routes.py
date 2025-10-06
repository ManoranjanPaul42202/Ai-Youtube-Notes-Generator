import secrets
import os
from PIL import Image
from flask import render_template, url_for, redirect, flash, request, jsonify, session
from gistify import app, db, bcrypt
from gistify.form import RegistrationForm, loginForm, UpdateAccountForm, LinkForm, GenerateNotesForm
from gistify.model import User, Note
from flask_login import login_user, logout_user, current_user, login_required
from gistify.audio_transcription import generate_transcript

data = '''
    Hi everyone, Kevin here. Today we're going to look at how you can take speech and turn it into text using AI. And the really crazy thing is that it does a better job than most humans. You can use it with English and 96 other languages. It works even if you have a lot of background noise. And it also works if you have a very sick accent. The best part is that it's completely free and also open source. Let's check out how to do this. We're going to use an AI tool called Whisper. Whisper is made by a company called OpenAI and you might've heard of them before. That's the same company behind the immensely popular chat GPT, which allows you to converse with a computer. There are also the company behind Dolly2 where you can type in some text and then it'll generate an image based on that text. You can install Whisper directly on your computer. You can click on the link right up above, but you do need a somewhat capable computer. So instead we're going to use something called Google Collaboratory. This allows you to run code directly in your web browser. So it doesn't really matter what type of PC you have. To use Google Collaboratory, head to Google Drive. You can click on the link right up above. You'll need a Google account and if you don't have one yet, it's entirely free to set up. On Google Drive, in the top left hand corner, let's click on the new button. And at the very bottom, let's click on more and then go down to connect more apps. At the top of this dialogue, let's click into the search field and here type in Google Collaboratory and then search. Here we see this result for Collaboratory. Let's click on that. And here let's click on install. Next, let's click on continue. Next, you should see a message saying that Google Collaboratory was connected to Google Drive. Let's click on okay. And look at that, it has successfully been installed. Let's click on done. Now you can close out this window. Let's now go back to the top left hand corner, click on the new button again, then go down to more. And here you should now see an option for Google Collaboratory. Let's click on this one. This drops us into the Google Collaboratory space. And at first glance, it might look a little bit intimidating, but trust me, this is going to be so easy and the results are going to be so good. In the top left hand corner, first off, let's give our file a name. This way you could find your way back to this in the future. I'll click on untitled. Let's double click on that. And here I'll type in transcribe audio. Here I'll click away and that's now the name of the file. Next, let's click on the menu titled runtime. And right here, there's the option for change runtime type. Let's click on that. And that opens up this dialogue where we can choose the hardware accelerator. Be sure to select GPU or a graphics card. It turns out that graphics cards run these models extremely well. Next, let's click on save. Next, we need to install Whisper AI. So let's go up to this field right up above where we can enter in code. And here I'll enter this in. You'll find this in the description so you could simply copy and paste it from there. First, we're going to install Whisper and we're getting this from GitHub. This is where all of the code is kept and also maintained. Once we get that, we're going to install something called FFmpeg. And this allows us to work with audio and video files. And although I say we're going to install it, don't worry, we're not installing anything on your computer. This is installing it all to the Google Collaboratory. Once you're all set, over on the left-hand side, let's click on this run icon. This will now go through and install Whisper and also FFmpeg. And it looks like the installation finished in about 23 seconds. Not too bad. Over on the left-hand side, let's click on this folder icon. And you can now drag in an audio file or a video file that you would like to transcribe. Here, I have an MP3 file and I'll simply drop this in. Here it says that the uploaded files will get deleted when this runtime is recycled. That's okay, so let's click on okay. And now we can see that the file has been successfully uploaded. I'm now ready to extract text from this audio file. Let's go back up to the top and here I'll insert some code. This inserts another field down below and here I'll type in Whisper. Here, this is calling the Whisper AI. Then you need to type in the name of the file that you want to extract text from. Mine is called cookies.mp3. So here I'll make sure it says cookies.mp3. And last, you can also specify the model that you would like to use. I want to use the medium model. You have five different models that you can choose from. On the low end, you have the tiny model. This takes up the least space. It also works the quickest, but you get the worst accuracy. On the other end, you have the large model. It takes up about a gig and a half. It also takes the longest time to process, but you also get the highest quality level. I found that a good sweet spot is going with the medium model. Once you finish entering this in, let's click on the run icon. And check that out, it has now finished running. And right down here, I can see a transcript of everything that was said in this audio file. Also, over on the left-hand side, if you don't see these three new files, right up on top, click on the refresh icon and you should see an SRT file, a TXT file, and a VTT file. A text file is just all of the text from the audio. SRT and VTT, these are caption formats that also include timestamps, so you know what was said when. To download any one of these files, over on the right-hand side, click on the ellipsis or the three dot, and here you can click on download. I'll download the SRT file and also the TXT file. Here, I'll click on download. Here, we can see the TXT file. And the thing I love about using Whisper is, first off, reading through this, it looks like it did a perfect job transcribing. Also, look at all of this, it applied capitalization. You also get punctuation, so this is a very high-quality transcript. When I open up the SRT file, here you'll see the exact same transcript, but it also includes timestamps for when everything is said. To transcribe another file, you could simply drag another audio or video file in and then simply update the name right here and you can run again, and then you'll get another transcript for your next file. To transcribe this file, we just use a very basic command. You also have some additional parameters that you can use. Right up on top, let's add some more code. And right down here, type in Whisper-H. You'll also find this in the description. And then let's click on run. This opens up all of the available parameters. Here, for instance, you can specify where you want to save the output. Here, you could also specify whether you want to transcribe a file or whether you also want to translate a file. Here, you could also specify the language and you have many other parameters. If you're not sure what a parameter does, if you scroll down a little bit, here you'll see a detailed explanation of what every single parameter does. Once you leave Google Collaboratory, your runtime will end and it'll automatically remove all of your files. So if you've transcribed some audio, I'd recommend downloading it first before you leave. This is such amazing technology. I personally use it for all of my YouTube video captions. It does a better job than Google's auto-generated captions because it gets all the words right. It applies capitalization. It takes care of the punctuation. I just have to go in and make a few very minor tweaks and refinements to get it perfect. To watch more videos like this one, please consider subscribing and I will see you in the next video.
'''

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
        data=data,
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

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('hello'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
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
