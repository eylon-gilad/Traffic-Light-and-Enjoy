import dash
from dash import dcc, html, Input, Output
from server import server  # Our Flask instance
import os

# Create the Dash app on top of the Flask server
app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True
)

# Import your pages (AFTER creating app)
from pages import page1_car_time
from pages import page2_cars_per_road
from pages import page3_lane_speed
from pages import page4_traffic_light
from pages import page5_correlation

# Main layout with multi-page routing
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content"),

    # Refresh plots every 2 seconds
    dcc.Interval(id="interval-component", interval=2000, n_intervals=0),
])

# Simple router to swap pages
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/page-2":
        return page2_cars_per_road.layout
    elif pathname == "/page-3":
        return page3_lane_speed.layout
    elif pathname == "/page-4":
        return page4_traffic_light.layout
    elif pathname == "/page-5":
        return page5_correlation.layout
    else:
        # Default page-1 if blank or unknown
        return page1_car_time.layout

if __name__ == "__main__":
    # Run on port 8050 by default; no need for root privileges
    app.run(debug=True, host="127.0.0.1", port=8050)
