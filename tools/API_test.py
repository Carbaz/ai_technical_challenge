"""FCM API endpoint interactive test."""

from pprint import pprint

from environs import Env
from openai import OpenAI


env = Env()
env.read_env('.env', recurse=True)

api_url = env.str('FCM_APA_LLM_API_URL')
api_key = env.str('FCM_APA_LLM_API_KEY')

openai = OpenAI(api_key=api_key, base_url=api_url)

pprint(models := openai.models.list().data)
