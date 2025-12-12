"""
Main application entry point.

This file only loads the Flask application using create_app()
and runs the development server.

Keeping this file minimal is good practice because all real
configuration lives inside stroke_app/__init__.py.
"""

from stroke_app import create_app

# Create Flask application instance using factory pattern
app = create_app()

if __name__ == "__main__":
    # Debug mode gives auto-reload and detailed error pages
    app.run(debug=True)
