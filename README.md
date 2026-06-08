# Django Final Project 🎓

A comprehensive Django project that includes multiple applications with a complete management system.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [Important Files](#important-files)
- [Available Commands](#available-commands)
- [Configuration](#configuration)

---

## 🎯 Overview

This is an advanced Django project designed to create a comprehensive web application featuring:

- ✅ User Management System
- ✅ Advanced Database Models
- ✅ Professional User Interfaces (HTML/CSS)
- ✅ Media Files Handling
- ✅ Content Management System
- ✅ Admin Dashboard
- ✅ RAG Course Recommender
- ✅ Multi-Agent Teaching Assistant

---

## 📂 Project Structure

```
Django_final_project/
│
├── config/                          # Main configuration folder
│   ├── __init__.py
│   ├── settings.py                  # Project settings
│   ├── urls.py                      # Main URL routes
│   ├── wsgi.py                      # WSGI configuration
│   └── asgi.py                      # ASGI configuration
│
├── core/                            # Main application
│   ├── migrations/                  # Database migration files
│   ├── templates/                   # HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   └── [other templates].html
│   ├── static/                      # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── __init__.py
│   ├── admin.py                     # Django admin configuration
│   ├── apps.py                      # App configuration
│   ├── models.py                    # Database models
│   ├── views.py                     # View functions and classes
│   ├── urls.py                      # App-specific URL routes
│   ├── forms.py                     # Django forms
│   ├── tests.py                     # Unit tests
│   └── views/                       # Separated view modules (optional)
│
├── media/                           # User uploaded files directory
│   └── course_docs/                 # Course documents
│
├── templates/                       # Global HTML templates (optional)
│   └── base.html
│
├── static/                          # Global static files (optional)
│
├── manage.py                        # Django management tool
├── requirements.txt                 # Project dependencies
├── .gitignore                       # Git ignore rules
├── db.sqlite3                       # SQLite database (development)
└── README.md                        # Project documentation
```

---

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **Django**: 3.2 or higher
- **Database**: SQLite (default), PostgreSQL, or MySQL
- **pip**: Python package manager

---

## 📥 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Arezk22/Django_final_project.git
cd Django_final_project
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations

```bash
python manage.py migrate
```

### Step 5: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### Step 6: Run Development Server

```bash
python manage.py runserver
```

The project will be accessible at: `http://127.0.0.1:8000/`

---

## 🚀 Usage Guide

### Access Admin Panel

```
http://localhost:8000/admin
```

Log in with the superuser credentials you created.

### Run Tests

```bash
python manage.py test
```

### Collect Static Files (Production)

```bash
python manage.py collectstatic
```

### Reset Database

```bash
python manage.py flush
```

### Create a New App

```bash
python manage.py startapp app_name
```

---

## 📄 Important Files

### `manage.py`

- Django's command-line utility for administrative tasks
- Used to run development server, create migrations, and manage the project

### `requirements.txt`

- Contains all project dependencies with specific versions
- Install all dependencies using: `pip install -r requirements.txt`

### `config/settings.py`

- Main configuration file containing:
  - Database configuration
  - Installed applications
  - Middleware settings
  - Static and media files paths
  - Security settings
  - Authentication settings

### `config/urls.py`

- Main URL routing configuration
- Includes URLs from all applications

### `core/models.py`

- Database models definition
- Contains all data structures used in the application

### `core/views.py`

- Contains view functions and classes
- Handles request processing and response generation

### `core/urls.py`

- Application-specific URL patterns
- Maps URLs to views

### `core/forms.py`

- Django forms for data validation
- User input forms for various features

### `core/admin.py`

- Django admin interface configuration
- Registers models for admin panel access

### `core/templates/`

- HTML templates for rendering pages
- Uses Django template language for dynamic content

---

## 🛠️ Available Commands

| Command                            | Description                   |
| ---------------------------------- | ----------------------------- |
| `python manage.py runserver`       | Start development server      |
| `python manage.py migrate`         | Apply database migrations     |
| `python manage.py makemigrations`  | Create new migrations         |
| `python manage.py createsuperuser` | Create admin user             |
| `python manage.py test`            | Run unit tests                |
| `python manage.py shell`           | Open interactive Python shell |
| `python manage.py collectstatic`   | Collect static files          |
| `python manage.py flush`           | Clear database                |
| `python manage.py startapp [name]` | Create new application        |

---

## 🔐 Configuration

### Development Settings

In `config/settings.py`, ensure:

```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### Production Settings

Before deploying to production:

- ⚠️ Set `DEBUG = False`
- ⚠️ Generate a new `SECRET_KEY`
- ⚠️ Use environment variables for sensitive data
- ⚠️ Configure `ALLOWED_HOSTS` properly
- ⚠️ Use a production database (PostgreSQL recommended)

### Environment Variables

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

---

## 📊 Key Components

| Component       | Purpose                                    |
| --------------- | ------------------------------------------ |
| **config/**     | Project configuration and main URL routing |
| **core/**       | Main application logic, models, and views  |
| **templates/**  | HTML templates for frontend                |
| **static/**     | CSS, JavaScript, and image files           |
| **media/**      | User-uploaded files storage                |
| **migrations/** | Database schema changes                    |

---

## 🔄 Development Workflow

### 1. Create Models

- Define data structures in `core/models.py`
- Create migration: `python manage.py makemigrations`
- Apply migration: `python manage.py migrate`

### 2. Create Views

- Add view logic in `core/views.py`
- Define URL patterns in `core/urls.py`

### 3. Create Templates

- Add HTML templates in `core/templates/`
- Use Django template language for dynamic content

### 4. Register Models in Admin

- Register models in `core/admin.py`
- Access through admin panel

### 5. Test Your Code

- Write tests in `core/tests.py`
- Run tests with `python manage.py test`

---

## 📚 Django Best Practices

- Keep views simple - use class-based views when appropriate
- Create reusable template tags and filters
- Use Django ORM for database operations
- Implement proper error handling
- Write meaningful commit messages
- Keep models DRY (Don't Repeat Yourself)
- Use environment variables for sensitive data

---

## 🚀 Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError`

**Solution**: Ensure virtual environment is activated and dependencies are installed

```bash
pip install -r requirements.txt
```

### Issue: Database Migration Errors

**Solution**: Check migration files and reset if necessary

```bash
python manage.py migrate core --fake-initial
```

### Issue: Static Files Not Loading

**Solution**: Collect static files

```bash
python manage.py collectstatic --noinput
```

---

## 📝 Files to Exclude from Git

```
*.pyc
__pycache__/
*.sqlite3
venv/
.env
.env.local
*.log
/media/
/static/collected/
.DS_Store
.vscode/
.idea/
```

---

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📞 Support & Issues

If you encounter any issues or have suggestions:

- Open an **Issue** on GitHub
- Create a **Pull Request** with improvements
- Contact the project maintainer

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

## 📖 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Python Documentation](https://docs.python.org/3/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## ✍️ Additional Notes

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Write docstrings for complex functions
- Keep lines under 79 characters

### Testing

- Write tests for critical functionality
- Aim for high code coverage
- Use Django's TestCase class for database tests

### Security

- Always validate user input
- Use Django's built-in security features
- Keep dependencies updated
- Use HTTPS in production
- Implement CSRF protection (enabled by default)

---

## 🎉 Getting Started Tips

1. **Read the Django Documentation**: Familiarize yourself with Django concepts
2. **Start Small**: Create simple models and views first
3. **Use Admin Panel**: Django's admin panel is powerful for initial development
4. **Write Tests**: Test your code frequently
5. **Use Git**: Maintain version control throughout development

---

**Last Updated**: 2026
**Status**: Under Development 🔄
**Maintainer**: Arezk22

---

Made with ❤️ By Ahmed Rezk
