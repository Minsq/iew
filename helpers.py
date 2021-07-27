import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
import datetime

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def sgd(value):
    """Format value as SGD."""
    return f"${value:,.2f}"

def percent(value):
    """Format value as percentage."""
    return f"{value:,.2f}%"

def f_datetime(value):
    """Format value as percentage."""
    return f"{value.date()}"


def getStatus(row):
    # get status for bill payments
    today = datetime.date.today()
    reminder = row['reminder'].date()
    deadline = row['deadline'].date()

    if (reminder - today).days <= 0:
        return "REMINDER"
    elif (deadline - today).days < 0:
        return "OVERDUE"
    else:
        return "NOT YET"