"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

import ipywidgets as widgets

MAIN_BOX_LAYOUT = widgets.Layout(
    flex="1 1 auto", height="1200px", min_height="50px", width="auto"
)
MAIN_INTERFACE_LAYOUT = widgets.Layout(height="30%", width="90%")
MAIN_DISPLAY_LAYOUT = widgets.Layout(
    flex="0 1 auto",
    height="50%",
    overflow_y="auto",
    width="90%",
    border="1px solid black",
)
MAIN_FEEDBACK_LAYOUT = widgets.Layout(flex="0 1 auto", height="5%", width="90%")

INPUT_BOX_LAYOUT = widgets.Layout(
    flex="1 1 auto", height="100%", min_height="50px", width="auto"
)
INPUT_TEXT_LAYOUT = widgets.Layout(height="90%", width="90%")

SUB_DETECT_BOX_LAYOUT = widgets.Layout(
    flex="1 1 auto", height="40%", min_height="50px", width="auto"
)
DETECT_BOX_LAYOUT = widgets.Layout(
    flex="1 1 auto", height="auto", min_height="50px", width="auto"
)
INFO_BOX_LAYOUT = widgets.Layout(
    flex="1 1 auto", height="100%", min_height="50px", width="auto"
)
