from flask import Flask, render_template, redirect, request, session
import funcs

app = Flask(__name__)
app.secret_key = "wieofuhwelifugwguhöwreogih"

@app.route("/")
def start():
    li = False

    if session.get("logged_in"):
        li = True

    posts = funcs.get_posts()
    return str(posts)

    return render_template("index.html", li=li, posts=posts)

@app.route("/login")
def login():
    if session.get("logged_in"):
        return redirect("/")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/login/process", methods=["POST"])
def lprocess():
    un = request.form["username"]
    pw = request.form["password"]

    lg = funcs.login_user(un, pw)

    if lg[0] == True:
        session["logged_in"] = True
        session["user"] = un

        return redirect("/")

    return render_template("login.html")

@app.route("/post")
def post():
    return render_template("post.html")

@app.route("/post/process", methods=["POST"])
def pprocess():
    title = request.form["title"]
    description = request.form["description"]
    files = request.files.getlist("bilder")

    if not files or len(files) == 0:
        return "Keine Dateien hochgeladen", 400

    image_urls = []

    for file in files:
        image_url = funcs.upload_image(file)
        if not image_url:
            return "Bild-Upload fehlgeschlagen", 500
        image_urls.append(image_url)

    db_result = funcs.save_post_with_images(title, description, image_urls)
    if not db_result:
        return "Fehler beim Speichern in der Datenbank", 500

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=5600)