# Support pour PyMySQL
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    # PyMySQL not available, will use mysqlclient if available
    pass

