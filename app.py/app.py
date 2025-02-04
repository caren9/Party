from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max file size

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Check allowed file extensions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user input from the form
        host = request.form["host"]
        event = request.form["event"]
        date = request.form["date"]
        time = request.form["time"]
        venue = request.form["venue"]
        guest = request.form["guest"]
        rsvp_link = request.form["rsvp_link"]

        # Handle background image upload
        background_image = request.files.get("background")
        bg_path = None
        if background_image and background_image.filename != "":
            if allowed_file(background_image.filename):
                filename = secure_filename(background_image.filename)
                bg_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                background_image.save(bg_path)
            else:
                return "File type not allowed. Only PNG, JPG, JPEG, and GIF are allowed."

        # Generate QR code
        qr_code_path = generate_qr_code(rsvp_link)

        # Generate invitation card
        invitation_path = create_invitation_card(host, event, date, time, venue, guest, qr_code_path, bg_path)

        return send_file(invitation_path, as_attachment=True)

    return render_template("index.html")

def generate_qr_code(link):
    """Generates a QR code and saves it."""
    qr = qrcode.make(link)
    qr_path = "static/qr_code.png"
    qr.save(qr_path)
    return qr_path

def create_invitation_card(host, event, date, time, venue, guest, qr_code_path, bg_path):
    """Creates an invitation card with provided data and saves it."""
    width, height = 800, 600

    # Load background image or use default color
    if bg_path:
        bg_image = Image.open(bg_path).resize((width, height))
    else:
        bg_image = Image.new("RGB", (width, height), (255, 223, 186))  # Light orange background

    draw = ImageDraw.Draw(bg_image)

    # Load fonts (use default if custom font is unavailable)
    try:
        font_title = ImageFont.truetype("arial.ttf", 50)
        font_text = ImageFont.truetype("arial.ttf", 30)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # Draw text on the image
    draw.text((200, 50), "🎊 You're Invited! 🎊", font=font_title, fill="black")
    draw.text((50, 150), f"Dear {guest},", font=font_text, fill="black")
    draw.text((50, 200), f"Join us for {event}!", font=font_text, fill="black")
    draw.text((50, 250), f"📅 Date: {date}", font=font_text, fill="black")
    draw.text((50, 300), f"⏰ Time: {time}", font=font_text, fill="black")
    draw.text((50, 350), f"📍 Venue: {venue}", font=font_text, fill="black")
    draw.text((50, 450), f"Hosted by: {host}", font=font_text, fill="black")
    draw.text((50, 500), "Scan QR Code below to RSVP 👇", font=font_text, fill="black")

    # Paste QR code onto the invitation
    qr_code = Image.open(qr_code_path).resize((150, 150))
    bg_image.paste(qr_code, (600, 420))

    # Save and return invitation file path
    invitation_path = "static/party_invitation.png"
    bg_image.save(invitation_path)
    return invitation_path

if __name__ == "__main__":
    app.run(debug=True)
