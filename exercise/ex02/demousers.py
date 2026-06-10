# nur fuer uebungszwecke
# -- NIEMALS IN EINER ECHTEN APP PASSWOERTER SPEICHERN!

from werkzeug.security import generate_password_hash

USERS = {
    "alice": {"id": "alice", "password": generate_password_hash("password")},
    "admin": {"id": "admin", "password": generate_password_hash("adminpass")},
}
    
    