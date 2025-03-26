from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from sim.DataPlots.server import collision_history

layout = html.Div([
    html.H1("Page 1: Collision Distribution"),
    html.P("A histogram showing the number of collisions in the simulation."),
    dcc.Graph(id="collision-histogram"),
    html.Br(),
    dcc.Link("Go to Page 1", href="/page-1"),html.Br(),
    dcc.Link("Go to Page 2", href="/page-2"), html.Br(),
    dcc.Link("Go to Page 3", href="/page-3"), html.Br(),
    dcc.Link("Go to Page 4", href="/page-4"), html.Br(),
    dcc.Link("Go to Page 5", href="/page-5"),
])

@callback(
    Output("collision-histogram", "figure"),
    Input("interval-component", "n_intervals")
)
def update_collision_histogram(_):
    """
    Displays a histogram of the number of collisions in the simulation.
    """
    if not collision_history:
        fig = px.histogram(
            pd.DataFrame({'collisions': []}),
            x='collisions',
            nbins=20,
            title="No Collisions in Simulation"
        )
        fig.update_layout(
            xaxis_title="Number of Collisions",
            yaxis_title="Frequency"
        )
        return fig

    # Flatten the collision history (assuming each entry in collision_history is a list of collision pairs)
    collision_counts = [len(collisions) for collisions in collision_history]

    # Create a DataFrame for plotting
    df = pd.DataFrame({'collisions': collision_counts})

    fig = px.histogram(
        df,
        x='collisions',
        nbins=20,
        title="Distribution of Collisions in Simulation"
    )
    fig.update_layout(
        xaxis_title="Number of Collisions",
        yaxis_title="Frequency"
    )
    fig.update_traces(
        hovertemplate="Collisions: %{x}<br>Frequency: %{y}"
    )
    return fig
