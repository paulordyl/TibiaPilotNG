import secrets
import string

def genRanStr():
  return ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(30))