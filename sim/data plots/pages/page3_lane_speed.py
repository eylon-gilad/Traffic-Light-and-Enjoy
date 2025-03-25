from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from server import lane_avg_speeds_history

layout = html.Div([
    html.H1("Page 3: Average Lane Speed"),
    html.P("A line chart showing average speed (units/s) in each lane over time."),
    dcc.Graph(id="lane-speed-plot"),
    html.Br(),
    dcc.Link("Go to Page 1", href="/"), html.Br(),
    dcc.Link("Go to Page 2", href="/page-2"), html.Br(),
    dcc.Link("Go to Page 4", href="/page-4"), html.Br(),
    dcc.Link("Go to Page 5", href="/page-5"),
])

@callback(Output("lane-speed-plot", "figure"),
          Input("interval-component", "n_intervals"))
def update_lane_speed_plot(_):
    """
    Line chart of average lane speeds over time.
    """
    if not lane_avg_speeds_history:
        return px.line(
            pd.DataFrame({'iteration': [], 'lane_id': [], 'avg_speed': []}),
            x='iteration', y='avg_speed', color='lane_id',
            title="Average Lane Speeds Over Time (No Data)"
        )

    rows = []
    for lane_id, speeds in lane_avg_speeds_history.items():
        for i, speed in enumerate(speeds):
            rows.append((i, lane_id, speed))

    df = pd.DataFrame(rows, columns=["iteration", "lane_id", "avg_speed"])
    df["lane_id"] = df["lane_id"].astype(str)

    fig = px.line(
        df,
        x="iteration",
        y="avg_speed",
        color="lane_id",
        title="Average Lane Speeds Over Time"
    )
    fig.update_layout(
        xaxis_title="Iteration",
        yaxis_title="Speed (units/s)"
    )
    fig.update_traces(
        hovertemplate="Iteration: %{x}<br>Lane ID: %{fullData.name}<br>Speed: %{y}"
    )
    return fig
