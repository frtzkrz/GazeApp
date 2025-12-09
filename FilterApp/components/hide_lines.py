from dash import Patch, Input, Output, Dash

from . import ids

def hide_lines_patch(n_clicks) -> Patch:
    patch = Patch()
    lines_to_hide = list(range(4, 6))  # lines 5–10

    # Toggle visibility
    for i in lines_to_hide:
        patch["data"][i]["visible"] = False

    return patch

