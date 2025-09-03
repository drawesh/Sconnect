 # Sconnect

Sconnect is a web application built with Flask that facilitates collaboration on academic papers. It allows users to upload, explore, and discuss research papers across various categories, fostering academic collaboration through integrated chat features.

## Features

- **User Authentication**: Secure registration and login system with password hashing
- **Paper Upload**: Upload academic papers with title, description, and category classification
- **Paper Exploration**: Browse and search papers by title or filter by category
- **User Profiles**: View and edit personal profiles
- **Real-time Chat**: Communicate with other users about specific papers or general topics
- **Notifications**: Stay updated on collaboration requests and system notifications
- **Paper Management**: Edit and delete uploaded papers

## Prerequisites

Before running this application, make sure you have the following installed:

- Python 3.8 or higher
- PostgreSQL database
- Git (for cloning the repository)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sconnect.git
   cd sconnect
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install flask flask-sqlalchemy flask-login flask-bcrypt flask-session werkzeug psycopg2-binary
   ```

## Configuration

1. Set up your PostgreSQL database and update the database URI in `app.py`:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://your_username:your_password@your_host:5432/your_database'
   ```

2. Ensure the `flask_session` directory exists:
   ```bash
   mkdir flask_session
   ```

3. Update the secret key in `app.py` for production:
   ```python
   app.secret_key = 'your-secret-key-here'
   ```

## Running the Application

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Run the Flask application:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
sconnect/
├── app.py                 # Main Flask application
├── TODO.md               # Project tasks and progress
├── flask_session/        # Server-side session storage
├── mydatabase/           # Database files (if using SQLite)
├── static/               # Static files (CSS, JS, images)
│   ├── style.css
│   └── sconnect.db       # Database file (if applicable)
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── explore.html
│   ├── profile.html
│   ├── edit_profile.html
│   ├── chat.html
│   ├── chats.html
│   ├── notifications.html
│   ├── modify_submission.html
│   └── connection_requests.html
├── uploads/              # Uploaded paper files
└── README.md            # Project documentation
```

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login with Flask-Bcrypt for password hashing
- **Sessions**: Flask-Session for server-side session management
- **Frontend**: HTML, CSS (with Jinja2 templating)
- **File Handling**: Werkzeug for secure file uploads

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions about the project, please open an issue on GitHub or contact the maintainers.
