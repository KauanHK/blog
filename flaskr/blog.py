from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import abort
from .auth import login_required
from .db import get_db


bp = Blueprint('blog', __name__)