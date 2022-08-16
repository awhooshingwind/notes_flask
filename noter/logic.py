import markdown
import numpy as np
import pandas as pd

# Helper functions

# Render markdown
extensions = ['mdx_math', 'extra', 'codehilite']
def make_md(some_text):
    return markdown.markdown(some_text, extensions=extensions)
