# Em desenvolvimento

# Fondesc

Fondesc is a web application built with Django, possibly related to education or course management.

## Project Overview

Fondesc appears to be a comprehensive web application with features related to courses, user authentication, and possibly faculty management. The project uses Django for the backend and includes static files for frontend styling and interactivity.

## Features

- User authentication
- Course management
- Faculty information
- Responsive design

## Technology Stack

- Backend: Django
- Frontend: HTML, CSS, JavaScript
- Database: SQLite (default Django database)

## Project Structure

The project follows a standard Django structure with some additional custom apps:

- \`fondesc/\`: Main project directory
  - \`fondesc/\`: Django project settings
  - \`fondescapp/\`: Main Django app
    - \`migrations/\`: Database migrations
    - \`static/\`: Static files (CSS, JS)
    - \`templates/\`: HTML templates
  - \`manage.py\`: Django's command-line utility for administrative tasks

## Setup and Installation

1. Clone the repository:
   ```
   git clone git@github.com:clerdomy/fondesc.git
   cd fondesc
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate
   # On Windows use \venv\\Scripts\\activate\
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
  ```
  python manage.py runserver
  ```

7. Access the application at:
   ```
   http://localhost:8000\
   ```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

