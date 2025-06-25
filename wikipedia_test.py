import wikipedia
from tools.wikipedia.utils import extract_context
page = wikipedia.page("mercedes sosa")
with open("clean_file.html", "w") as fp:
    fp.write(extract_context(page))