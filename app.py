from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user, login_user, logout_user, LoginManager, UserMixin
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# PostgreSQL Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_Vhip9wNgSL2Z@ep-tiny-sun-a1x0gh8y-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
login_manager = LoginManager(app)


# Allowed categories
CATEGORIES = [
    "Artificial Intelligence", "Machine Learning", "Data Science", "Cybersecurity", "Computer Vision",
    "Blockchain", "Internet of Things", "Cloud Computing", "Robotics", "Quantum Computing"
]

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Paper model
class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)  # Renamed field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('papers', lazy=True))


# Chat message model
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

# Create the database tables
with app.app_context():
    db.create_all()  # Create all tables

# Global list for notifications
notifications = []

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route: Landing Page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        # Add notification for successful registration
        notifications.append(f"User '{username}' registered successfully!")
        
        return redirect(url_for('login'))
    return render_template('register.html')

# Route: Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)  # Use Flask-Login's login_user method
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "error")
    return render_template('login.html')

# Route: Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    papers = Paper.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', papers=papers, user=current_user)

# Route: Profile
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


#Route: Edit_Profile
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username or email already exists for another user
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username or email is already taken.', 'error')
            return redirect(url_for('edit_profile'))

        # Update user details
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.username = username
        current_user.email = email

        if password:  # Only update password if entered
            current_user.password = bcrypt.generate_password_hash(password).decode('utf-8')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=current_user)

# Route: Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route: Upload a paper
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        file = request.files.get('file')

        if not title or not description or not category or not file:
            flash("Please fill in all fields and upload a file.", "error")
            return redirect(url_for('upload'))

        if category not in CATEGORIES:
            flash("Invalid category selected!", "error")
            return redirect(url_for('upload'))

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        paper = Paper(title=title, description=description, category=category, file_path=file_path, user_id=current_user.id)
        db.session.add(paper)
        db.session.commit()

        flash(f"Paper '{title}' uploaded successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('upload.html', categories=CATEGORIES)



# Route: Explore (List of papers with category filter)
@app.route('/explore', methods=['GET'])
def explore():
    search_query = request.args.get('search', '').strip()
    selected_category = request.args.get('category', '')

    papers_query = Paper.query  # Start with base query

    if search_query:
        papers_query = papers_query.filter(Paper.title.ilike(f"%{search_query}%"))

    if selected_category:
        papers_query = papers_query.filter_by(category=selected_category)

    papers = papers_query.all()

    return render_template('explore.html', papers=papers)



# Route to delete paper
@app.route('/delete_paper/<int:paper_id>', methods=['POST'])
@login_required
def delete_paper(paper_id):
    paper = Paper.query.get(paper_id)
    if not paper:
        flash("Paper not found.", "error")
        return redirect(url_for('dashboard'))

    try:
        db.session.delete(paper)
        db.session.commit()
        flash("Paper deleted successfully.", "success")

        # Add notification for deletion
        notifications.append(f"Paper '{paper.title}' deleted successfully.")
    except Exception as e:
        flash(f"Error occurred while deleting the paper: {str(e)}", "error")

    return redirect(url_for('dashboard'))

# Route to handle collaboration request (now opens chat inbox)
@app.route('/collaborate/<int:paper_id>', methods=['POST'])
@login_required
def collaborate(paper_id):
    paper = Paper.query.get_or_404(paper_id)
    recipient = paper.user

    if recipient:
        notifications.append(f"Collaboration request sent to {recipient.username} for paper '{paper.title}'.")
        return redirect(url_for('chat_inbox', recipient_id=recipient.id))

    flash("Failed to open chat inbox.", "error")
    return redirect(url_for('explore'))

# Route to display chat partners
@app.route('/chats', methods=['GET'])
@login_required
def chats():
    user_id = current_user.id
    
    partners = db.session.query(User).join(
        ChatMessage, 
        (ChatMessage.sender_id == User.id) | (ChatMessage.recipient_id == User.id)
    ).filter(
        ((ChatMessage.sender_id == user_id) | (ChatMessage.recipient_id == user_id)) &
        (User.id != user_id)
    ).distinct().all()

    return render_template('chats.html', partners=partners)

# Route for individual chat inbox
@app.route('/chat/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def chat_inbox(recipient_id):
    sender_id = current_user.id

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            chat_message = ChatMessage(sender_id=sender_id, recipient_id=recipient_id, message=message)
            db.session.add(chat_message)
            db.session.commit()
            return redirect(url_for('chat_inbox', recipient_id=recipient_id))

    messages = ChatMessage.query.filter(
        (ChatMessage.sender_id == sender_id) & (ChatMessage.recipient_id == recipient_id) |
        (ChatMessage.sender_id == recipient_id) & (ChatMessage.recipient_id == sender_id)
    ).all()

    recipient_user = User.query.get(recipient_id)

    return render_template('chat.html', messages=messages, recipient_user=recipient_user)

# Route: Notifications
@app.route('/notifications_page')
@login_required
def notifications_page():
    user_notifications = notifications  # Here we are directly using the list
    return render_template('notifications.html', notifications=user_notifications)

# Route: Modify submission
@app.route('/modify_submission/<int:paper_id>', methods=['GET', 'POST'])
@login_required
def modify_submission(paper_id):
    paper = Paper.query.get_or_404(paper_id)

    if paper.user_id != current_user.id:
        flash("You are not authorized to edit this submission.", "error")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')

        if category not in CATEGORIES:
            flash("Invalid category selected!", "error")
            return redirect(url_for('modify_submission', paper_id=paper_id))

        if title:
            paper.title = title
        if description:
            paper.description = description
        paper.category = category

        db.session.commit()
        flash("Submission updated successfully.", "success")

        return redirect(url_for('dashboard'))

    return render_template('modify_submission.html', paper=paper, categories=CATEGORIES)

# Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
