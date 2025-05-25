# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: hydrogen
#       format_version: '1.3'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: Python3
#     language: python
#     name: Python3
# ---

# %%
import json
import random
import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
from sklearn.datasets import load_iris

# pio.templates.default = "plotly_dark"
pio.templates.default

# %% [markdown]
# # Template Notebook

# %%
data = pd.DataFrame(load_iris()['data'])
scales = [
    'aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
    'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
    'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
    'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
    'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
    'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
    'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
    'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
    'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
    'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
    'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
    'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
    'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
    'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
    'ylorrd'
]

# %%
fig = px.scatter(data, x=0, y=1, color=2)
# fig = fig.update_layout({'height': 300, 'width': 500})

# %%
fig.data

# %%
for scale in random.sample(scales, 10):
    x, y, c = random.sample(list(data.columns), 3)
    fig = px.scatter(data, x=x, y=y, color=c, color_continuous_scale=scale)
    fig.update_layout(dict(title=scale))
    fig.show()

# %%
for x in data.columns:
    for y in data.columns:
        fig = px.scatter(data, x=x, y=y)
        fig.show()

# %%
fig = go.Figure(data=go.Table(
   header=dict(values=data.columns),
    cells=dict(values=[data[col] for col in data.columns]),
))
fig.show()

# %%
list(pio.templates)

# %%
fig.to_json()

# %%
# %%
# %%
# %%
# %%
# %%
# %%
# %%
# %%
# %%
# %%
# %%
# %%
