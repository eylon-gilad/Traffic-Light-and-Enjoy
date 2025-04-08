from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from server import collisions

layout = html.Div(
    [
        html.H1("Page 4: collisions over time"),
        html.P("A line chart showing the number of collisions over time."),
        dcc.Graph(id="collisions-plot"),
        html.Br(),
        dcc.Link("Go to Page 1", href="/"),
        html.Br(),
        dcc.Link("Go to Page 2", href="/page-2"),
        html.Br(),
        dcc.Link("Go to Page 3", href="/page-3"),
        html.Br(),
        dcc.Link("Go to Page 5", href="/page-5"),
    ]
)

# Store live data
collision_data = {"iterations": [], "collisions": []}


@callback(
    Output("collisions-plot", "figure"), Input("interval-component", "n_intervals")
)
def update_collisions_plot(n):
    """
    Updates the graph with live collision count per iteration.
    """
    # Simulate a live collision count (replace this with your actual source)

    if collisions is not []:
        # Append new data
        collision_data["iterations"].append(n)
        collision_data["collisions"].append(collisions[-1])

        # Convert to DataFrame
        df = pd.DataFrame(collision_data)

        # Create line plot
        fig = px.line(
            df,
            x="iterations",
            y="collisions",
            markers=True,
            title="Collisions Over Time",
        )

        # Update labels
        fig.update_layout(xaxis_title="Iteration", yaxis_title="Number of Collisions")

        return fig
    return [html.P("No lane data available.")]
