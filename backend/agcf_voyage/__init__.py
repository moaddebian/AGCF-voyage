# Support pour PyMySQL
import pymysql
pymysql.install_as_MySQLdb()

# Patch pour Python 3.14.0 compatibility
try:
    from .fix_python314 import *
except ImportError:
    pass

