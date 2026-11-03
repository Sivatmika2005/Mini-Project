from dotenv import load_dotenv
load_dotenv()
from utils import auth

print(auth.send_password_reset_request('siivatmika0206@gmail.com'))
