from dotenv import load_dotenv
from fasthtml.common import *
from openai import AsyncOpenAI, OpenAI, AsyncAzureOpenAI, AzureOpenAI

# Load environment variables from the .env file
load_dotenv()

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com"),
font_awsome = Script(src="https://kit.fontawesome.com/f735776107.js", crossorigin="anonymous")
keystrokes = Script(src="/static/keystrokes.js")
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
css = Style('.x {border:black solid 1px}  .down {position:absolute; bottom:10px; right:10px} ')

fast_app = FastHTML(hdrs=(font_awsome, keystrokes, tlink, dlink, css), exts='ws')
fast_app.static_route(prefix='/static', static_path='./src/static')


# openai.api_key = os.environ.get("OPENAI_API_KEY")
api_key = os.getenv("OPENAI_API_KEY")
if os.getenv("USE_AZURE", "no").lower() == "yes":
    client = AsyncAzureOpenAI(
        api_key=api_key,
        api_version=os.getenv("AZURE_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    openAiCli = AzureOpenAI(
        api_key=api_key,
        api_version=os.getenv("AZURE_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
else:
    client = AsyncOpenAI(
        api_key=api_key,  # This is the default and can be omitted
    )

    openAiCli = OpenAI(
        api_key=api_key,  # This is the default and can be omitted
    )
