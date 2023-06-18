import os
import urllib.parse

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'

    BLOB_ACCOUNT = os.environ.get('BLOB_ACCOUNT') or 'udacity4599'
    BLOB_CONTAINER = os.environ.get('BLOB_CONTAINER') or 'images'
    BLOB_STORAGE_ACCOUNT_URL = os.environ.get('BLOB_STORAGE_URL') or 'DefaultEndpointsProtocol=https;AccountName=udacity4599;AccountKey=Ddl3dVxfefTLoJp+CDYWXoAtz/KH03v8VC16h7rzBXlYoXTGMYXeBhY6hJzP34s5SAmVW78fEbj5+AStdg8RRQ==;EndpointSuffix=core.windows.net'

    SQL_SERVER = os.environ.get('SQL_SERVER') or 'nhan4599-udacity.database.windows.net'
    SQL_DATABASE = os.environ.get('SQL_DATABASE') or 'udacity-ass1'
    SQL_USER_NAME = os.environ.get('SQL_USER_NAME') or 'nhan4599'
    SQL_PASSWORD = os.environ.get('SQL_PASSWORD') or 'p@nCake061000'
    # Below URI may need some adjustments for driver version, based on your OS, if running locally
    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{SQL_USER_NAME}:{urllib.parse.quote(SQL_PASSWORD)}@{SQL_SERVER}/{SQL_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ### Info for MS Authentication ###
    ### As adapted from: https://github.com/Azure-Samples/ms-identity-python-webapp ###
    MS_CLIENT_ID = os.environ.get('CLIENT_ID')
    MS_CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    # In your production app, Microsoft recommends you to use other ways to store your secret,
    # such as KeyVault, or environment variable as described in Flask's documentation here:
    # https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
    # CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    # if not CLIENT_SECRET:
    #     raise ValueError("Need to define CLIENT_SECRET environment variable")

    MS_AUTHORITY = "https://login.microsoftonline.com/consumers"  # For multi-tenant app, else put tenant name
    # AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"


    MS_LOGIN_REDIRECT_PATH = "/ms-login-callback"  # Used to form an absolute URL; must match to app's redirect_uri set in AAD

    # You can find the proper permission names from this document
    # https://docs.microsoft.com/en-us/graph/permissions-reference
    SCOPES = ["User.Read"]
    AUTHORIZATION_SCOPES = ["openid", *SCOPES]

    SESSION_TYPE = "filesystem"  # Token cache will be stored in server-side session