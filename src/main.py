from fasthtml.common import serve

from pages.index import *
from pages.admin import *
from pages.scenario import *

serve(host="127.0.0.1")
