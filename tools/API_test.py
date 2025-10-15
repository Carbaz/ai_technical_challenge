"""FCM API endpoint interactive test."""

from environs import Env
from openai import OpenAI


env = Env()
env.read_env('.env', recurse=True)

api_url = env.str('FCM_API_URL')
api_key = env.str('FCM_API_KEY')

openai = OpenAI(api_key=api_key, base_url=api_url)

print(models := openai.models.list())
