This is a Django-based Docker Web UI application (dwui) for managing Docker containers via a web interface.
The application allows users to create, start, stop, restart, remove, and update Docker containers.
The application uses django-allauth for authentication.
The application uses Bootstrap 5 for styling.
The application uses HTMX for dynamic content updates.
The main Django app is in the dwui/ directory.
The application uses SQLite for its database.
Application settings are in dwui/settings.py.
URL routing is defined in dwui/urls.py.
Views are defined in dwui/views.py.
Docker client interactions are handled in dwui/docker_helper.py.
Container image configuration is defined in dwui/container_config.py.
Container image definitions are loaded from dwui/container_configs/ directory.
Environment variables should be defined in a .env file (see .env.example).
The Dockerfile for the application should be created in the root directory.
The application follows Django best practices.
All code should be properly typed with Python type annotations.
Debug logging is enabled by default in development mode.
Login is required for all views unless decorated with @login_not_required.
API endpoints should return proper status codes and error messages.
Container configurations are modular and loaded dynamically.
Custom template filters are defined in dwui/templatetags/app_filters.py.
When logging exceptions via logging.exception, the exception object is logged automatically. Including the exception object in the log message is redundant and can lead to excessive logging.
