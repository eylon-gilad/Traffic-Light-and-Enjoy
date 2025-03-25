from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from server import total_cars_history, avg_velocity_history

layout = html.Div([
    html.H1("Page 5: Total Cars vs. Average Velocity"),
    html.P("A scatter showing correlation between total cars in sim and average velocity."),
    dcc.Graph(id="correlation-scatter"),
    html.Br(),
    dcc.Link("Go to Page 1", href="/"), html.Br(),
    dcc.Link("Go to Page 2", href="/page-2"), html.Br(),
    dcc.Link("Go to Page 3", href="/page-3"), html.Br(),
    dcc.Link("Go to Page 4", href="/page-4"),
])

@callback(Output("correlation-scatter", "figure"),
          Input("interval-component", "n_intervals"))
def update_correlation_scatter(_):
    """
    Scatter of total_cars_history vs avg_velocity_history.
    """
    if not total_cars_history or not avg_velocity_history:
        return px.scatter(
            pd.DataFrame({'cars': [], 'avg_vel': []}),
            x='cars', y='avg_vel',
            title="Cars vs. Average Velocity (No Data)"
        )

    df = pd.DataFrame({
        "cars": total_cars_history,
        "avg_vel": avg_velocity_history
    })
    fig = px.scatter(
        df, x="cars", y="avg_vel",
        title="Total Cars vs. Average Velocity"
    )
    fig.update_layout(
        xaxis_title="Total Cars in Sim",
        yaxis_title="Average Velocity (units/s)"
    )
    fig.update_traces(
        hovertemplate="Cars: %{x}<br>Avg Velocity: %{y}"
    )
    return fig
