from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from server import traffic_light_state_history

layout = html.Div([
    html.H1("Page 4: Traffic Light States"),
    html.P("A line chart showing the state of each traffic light (0=Red, 1=Green)."),
    dcc.Graph(id="traffic-lights-plot"),
    html.Br(),
    dcc.Link("Go to Page 1", href="/"), html.Br(),
    dcc.Link("Go to Page 2", href="/page-2"), html.Br(),
    dcc.Link("Go to Page 3", href="/page-3"), html.Br(),
    dcc.Link("Go to Page 5", href="/page-5"),
])

@callback(Output("traffic-lights-plot", "figure"),
          Input("interval-component", "n_intervals"))
def update_traffic_lights_plot(_):
    """
    Displays traffic light states over time (0=red, 1=green).
    """
    if not traffic_light_state_history:
        return px.line(
            pd.DataFrame({'iteration': [], 'light_id': [], 'state': []}),
            x='iteration', y='state', color='light_id',
            title="Traffic Light States Over Time (No Data)"
        )

    rows = []
    for light_id, states in traffic_light_state_history.items():
        for i, s_val in enumerate(states):
            rows.append((i, light_id, s_val))

    df = pd.DataFrame(rows, columns=["iteration", "light_id", "state"])
    df["light_id"] = df["light_id"].astype(str)

    fig = px.line(
        df,
        x="iteration", y="state", color="light_id",
        title="Traffic Light States (1=Green, 0=Red)"
    )
    fig.update_layout(
        xaxis_title="Iteration",
        yaxis_title="Light State"
    )
    fig.update_traces(
        hovertemplate="Iteration: %{x}<br>Light ID: %{fullData.name}<br>State: %{y}"
    )
    return fig
