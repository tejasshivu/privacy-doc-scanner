import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    jsonify
)
from werkzeug.utils import secure_filename
from cleaner import clean_pdf_metadata

app = Flask(__name__)
app.secret_key = "change-this-in-production-to-a-random-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER  = os.path.join(BASE_DIR, "uploads")
CLEANED_FOLDER = os.path.join(BASE_DIR, "cleaned")

os.makedirs(UPLOAD_FOLDER,  exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"]  = UPLOAD_FOLDER
app.config["CLEANED_FOLDER"] = CLEANED_FOLDER

ALLOWED_EXTENSIONS = {"pdf"}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file was included in your request.", "error")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("Please select a file before uploading.", "error")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Only PDF files are supported right now.", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(upload_path)

    cleaned_filename = "cleaned_" + filename
    cleaned_path = os.path.join(app.config["CLEANED_FOLDER"], cleaned_filename)

    result = clean_pdf_metadata(upload_path, cleaned_path)
    os.remove(upload_path)

    if not result["success"]:
        flash(f"Something went wrong: {result.get('error', 'Unknown error')}", "error")
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        filename=cleaned_filename,
        original_meta=result["original"],
        cleaned_meta=result["cleaned"],
        removed_fields=result["removed"]
    )


@app.route("/download/<filename>")
def download_file(filename):
    filename = secure_filename(filename)
    file_path = os.path.join(app.config["CLEANED_FOLDER"], filename)

    if not os.path.exists(file_path):
        flash("File not found. It may have expired.", "error")
        return redirect(url_for("index"))

    return send_file(file_path, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)