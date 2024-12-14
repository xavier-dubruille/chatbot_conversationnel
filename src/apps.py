from dotenv import load_dotenv
from fasthtml.common import *
from openai import AsyncOpenAI, OpenAI, AsyncAzureOpenAI, AzureOpenAI

# Load environment variables from the .env file
load_dotenv()

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com"),
font_awsome = Script(src="https://kit.fontawesome.com/f735776107.js", crossorigin="anonymous")
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
css = Style('.x {border:black solid 1px}  .down {position:absolute; bottom:10px; right:10px} ')

fast_app = FastHTML(hdrs=(font_awsome, tlink, dlink, css), exts='ws')