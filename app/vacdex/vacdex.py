from flask import Blueprint, request, jsonify
from vacdb import *


vacdex = Blueprint("vacdex", __name__, subdomain="vac")
