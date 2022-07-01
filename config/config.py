# -*- coding: utf-8 -
from socket import gethostname
from datetime import datetime
import sys

G_APP_INFO = {
        'HOSTNAME': gethostname(),
        'APP_NAME': "",
        'APP_VER': "",
        'APP_DATE': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

G_DB_INFO = {}

G_DB_INFO['DB_HOST'] = '127.0.0.1'
G_DB_INFO['DB_PORT'] = 3306
G_DB_INFO['DB_USER'] = "root"
G_DB_INFO['DB_PW'] = '20162467'
G_DB_INFO['DB_NAME'] = "TripleDB"
G_DB_INFO['DB_MINCACHED'] = 2
G_DB_INFO['DB_MAXCONNECTIONS'] = 2