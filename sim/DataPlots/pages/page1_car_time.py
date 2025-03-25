from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from server import car_time_in_sim

layout = html.Div([
    html.H1("Page 1: Car Time Distribution"),
    html.P("A histogram showing how long each car has spent in the simulation."),
    dcc.Graph(id="car-time-histogram"),
    html.Br(),
    dcc.Link("Go to Page 2", href="/page-2"), html.Br(),
    dcc.Link("Go to Page 3", href="/page-3"), html.Br(),
    dcc.Link("Go to Page 4", href="/page-4"), html.Br(),
    dcc.Link("Go to Page 5", href="/page-5"),
])

@callback(
    Output("car-time-histogram", "figure"),
    Input("interval-component", "n_intervals")
)
def update_car_time_histogram(_):
    """
    Displays a histogram of how long each car has been in the sim.
    """
    if not car_time_in_sim:
        fig = px.histogram(
            pd.DataFrame({'time_in_sim': []}),
            x='time_in_sim',
            nbins=20,
            title="Distribution of Car Times (No Data)"
        )
        fig.update_layout(
            xaxis_title="Time in Simulation (s)",
            yaxis_title="Number of Cars"
        )
        return fig

    times = list(car_time_in_sim.values())
    df = pd.DataFrame({'time_in_sim': times})

    fig = px.histogram(
        df,
        x='time_in_sim',
        nbins=20,
        title="Distribution of Car Times in Simulation"
    )
    fig.update_layout(
        xaxis_title="Time in Simulation (s)",
        yaxis_title="Number of Cars"
    )
    fig.update_traces(
        hovertemplate="Time in Sim: %{x} s<br>Count: %{y}"
    )
    return fig