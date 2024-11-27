from dotenv import load_dotenv
from fasthtml.common import *
from openai import AsyncOpenAI, OpenAI, AsyncAzureOpenAI, AzureOpenAI

# Load environment variables from the .env file
load_dotenv()

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com"),
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
css = Style('.x {border:black solid 1px}  .down {position:absolute; bottom:10px; right:10px} ')

fast_app = FastHTML(hdrs=(tlink, dlink, picolink, css), exts='ws')

# openai.api_key = os.environ.get("OPENAI_API_KEY")
api_key = os.getenv("OPENAI_API_KEY")
if os.getenv("USE_AZURE", "no").lower() == "yes":
    client = AsyncAzureOpenAI(
        api_key=api_key,
        api_version = os.getenv("AZURE_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    openAiCli = AzureOpenAI(
        api_key=api_key,
        api_version = os.getenv("AZURE_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
else:
    client = AsyncOpenAI(
        api_key=api_key,  # This is the default and can be omitted
    )

    openAiCli = OpenAI(
        api_key=api_key,  # This is the default and can be omitted
    )
