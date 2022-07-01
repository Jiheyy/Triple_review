# -*- coding: utf-8 -*
from . import sqlite
from gevent import monkey # IO 함수들 비동기화
monkey.patch_all()
from flask import Flask

app = Flask(__name__)

sqlite.create_db()
