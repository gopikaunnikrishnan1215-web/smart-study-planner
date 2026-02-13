#!/usr/bin/env python
"""
Application entry point for the Study Planner application.
"""

if __name__ == "__main__":
    from backend import create_app
    
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5000)
