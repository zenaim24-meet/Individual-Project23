from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
from keys import youtube_api_key
import pyrebase
import requests


config = {
  "apiKey": "AIzaSyBKLyBHcJ7eQWwfpslP1jc4lx1xw8wrVZA",
  "authDomain": "individual-project-y2-b6746.firebaseapp.com",
  "projectId": "individual-project-y2-b6746",
  "storageBucket": "individual-project-y2-b6746.appspot.com",
  "messagingSenderId": "76357304606",
  "appId": "1:76357304606:web:cc5793bcc18bd36de6090f",
  "databaseURL": "https://individual-project-y2-b6746-default-rtdb.europe-west1.firebasedatabase.app/"
}



app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        print(request.form)
        if "signup-form" in request.form:
            username = request.form['username']
            user = {'email': email, 'username': username}
            try:
                login_session['user'] = auth.create_user_with_email_and_password(email, password)
                UID = login_session['user']['localId']
                db.child('Users').child(UID).set(user)
                return redirect(url_for('home'))
            except Exception as e:
                print("ERROR in index, signup-form")
                print(e)
        elif 'login-form' in request.form:
            try:
                login_session['user'] = auth.sign_in_with_email_and_password(email, password)
                return redirect(url_for('home'))
            except Exception as e:
                print("ERROR in index, login-form")
                print(e)

    return render_template("index.html")


@app.route('/choose', methods=['GET','POST'])
def choose():
    UID = login_session['user']['localId']
    if request.method== 'POST':
        space= request.form['space']
        links = get_video_links(youtube_api_key, space)
        print(links)
        return render_template("choose.html", links = links)
    else:
        return render_template("choose.html")

@app.route('/home', methods=['GET','POST'])
def home():
    link = request.args.get('link')
    return render_template("home.html", videoLink=link)

@app.route('/spaces', methods=['GET','POST'])
def spaces():

    return render_template("spaces.html")



@app.route('/spotify', methods=['GET','POST'])
def spotify():
    return render_template("spotifywidget.html")

@app.route('/todo', methods=['GET', 'POST'])
def todo_list():
    if request.method == 'POST':
        task = request.form['task']
        UID = login_session['user']['localId']
        tasks=[]
        tasks.append(task)
        db.child('Users').child(UID).set(tasks)

        if task:
            return render_template('to-do.html', taskslist= tasks)
        else:
            return "Please enter a task."

    return render_template('to-do.html')



@app.route('/logout')
def logout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('index'))

# def save_video_urls_to_firestore(videos):
#     db = firestore.client()
#     videos_ref = db.collection("videos")

#     # Save each video URL in the dictionary to Firestore
#     for category, video_urls in videos.items():
#         videos_ref.document(category).set({"urls": video_urls})
#     print('videos saved to firestore')


def get_video_links(api_key, query, max_results=5):
    base_url = "https://www.googleapis.com/youtube/v3"
    search_params = {
        "key": api_key,
        "q": query,
        "part": "snippet",
        "type": "video",
        "maxResults": max_results
    }
    response = requests.get(f"{base_url}/search", params=search_params)
    if response.status_code == 200:
        return [f"{item['id']['videoId']}" for item in response.json()['items']]
    else:
        print("Error:", response.status_code)
        return []



def countdown_timer(minutes, seconds):
    total_seconds = minutes * 60 + seconds
    while total_seconds >= 0:
        mins, secs = divmod(total_seconds, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        yield timeformat
        time.sleep(1)
        total_seconds -= 1

@app.route('/timer', methods=['GET', 'POST'])
def timer():
    if request.method == 'POST':
        if 'start' in request.form:
            # Set the initial time (25 minutes)
            minutes = 25
            seconds = 0
            timer = countdown_timer(minutes, seconds)
            return render_template('timer.html', timer=timer)

        elif 'reset' in request.form:
            # Reset the timer to 25 minutes
            minutes = 25
            seconds = 0
            timer = countdown_timer(minutes, seconds)
            return render_template('timer.html', timer=timer)

    return render_template('timer.html')

#save_video_urls_to_firestore(videos)

#Code goes above here

if __name__ == '__main__':
    app.run(debug=True)