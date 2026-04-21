from flask import Flask, render_template, request
import cv2
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "static"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create static folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def cartoonize(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return None

    img = cv2.resize(img, (600, 600))

    # Smooth + stylize
    stylized = cv2.stylization(img, sigma_s=120, sigma_r=0.35)

    # Edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 100, 200)
    edges = cv2.bitwise_not(edges)

    cartoon = cv2.bitwise_and(stylized, stylized, mask=edges)

    # Save output
    output_filename = "output.jpg"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)
    cv2.imwrite(output_path, cartoon)

    return f"static/{output_filename}"


@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    original = None

    if request.method == "POST":
        file = request.files.get("image")

        if file and file.filename != "":
            ext = os.path.splitext(file.filename)[1].lower()

            if ext in [".jpg", ".jpeg", ".png"]:
                unique_name = str(uuid.uuid4()) + ext
                upload_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)

                file.save(upload_path)

                original = f"static/{unique_name}"
                output = cartoonize(upload_path)

    return render_template("index.html", output=output, original=original)


if __name__ == "__main__":
    app.run(debug=True)