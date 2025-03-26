from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from server import lane_avg_speeds_history

layout = html.Div([
    html.H1("Page 3: Average Lane Speed"),
    html.P("A separate line chart for each lane’s speed over time."),
    html.Div(id="lane-speed-charts-container"),
    dcc.Interval(id="interval-component", interval=1000, n_intervals=0),
    html.Br(),
    dcc.Link("Go to Page 1", href="/"), html.Br(),
    dcc.Link("Go to Page 2", href="/page-2"), html.Br(),
    dcc.Link("Go to Page 4", href="/page-4"), html.Br(),
    dcc.Link("Go to Page 5", href="/page-5"), html.Br(),

])

@callback(
    Output("lane-speed-charts-container", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_lane_speed_charts(_):
    if not lane_avg_speeds_history:
        return [html.P("No data available yet.")]

    children = []
    for lane_id, speeds in lane_avg_speeds_history.items():
        if speeds is None or (isinstance(speeds, list) and len(speeds) == 0):
            continue

        if isinstance(speeds, (int, float)):
            speeds = [speeds]

        df = pd.DataFrame({
            "iteration": range(len(speeds)),
            "avg_speed": speeds
        })

        fig = px.line(
            df,
            x="iteration",
            y="avg_speed",
            title=f"Average Lane Speeds Over Time – Lane {lane_id}",
        )
        fig.update_layout(
            xaxis_title="Iteration",
            yaxis_title="Speed (units/s)"
        )
        fig.update_traces(
            hovertemplate="Iteration: %{x}<br>Speed: %{y}"
        )

        children.append(
            dcc.Graph(
                figure=fig,
                id=f"lane-speed-plot-lane-{lane_id}"
            )
        )

    if not children:
        return [html.P("No lane data available.")]

    return children
