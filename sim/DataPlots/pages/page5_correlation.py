from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from server import total_cars_history, avg_velocity_history

layout = html.Div(
    [
        html.H1("Page 5: Total Cars vs. Average Velocity"),
        html.P(
            "A heatmap showing the distribution between total cars in sim and average velocity."
        ),
        dcc.Graph(id="correlation-heatmap"),
        html.Br(),
        dcc.Link("Go to Page 1", href="/"),
        html.Br(),
        dcc.Link("Go to Page 2", href="/page-2"),
        html.Br(),
        dcc.Link("Go to Page 3", href="/page-3"),
        html.Br(),
        dcc.Link("Go to Page 4", href="/page-4"),
        html.Br(),
        dcc.Link("Go to Page 5", href="/page-5"),
        html.Br(),
    ]
)


@callback(
    Output("correlation-heatmap", "figure"), Input("interval-component", "n_intervals")
)
def update_correlation_heatmap(n_intervals):
    """
    Generate a 2D density heatmap of total_cars_history vs avg_velocity_history.
    Each bin is colored by the count of data points in that region.
    """
    # Validate data: ensure both histories are present and of equal length.
    if (
        not total_cars_history
        or not avg_velocity_history
        or len(total_cars_history) != len(avg_velocity_history)
    ):
        empty_df = pd.DataFrame({"cars": [], "avg_vel": []})
        return px.scatter(
            empty_df, x="cars", y="avg_vel", title="Cars vs. Average Velocity (No Data)"
        )

    # Build the dataframe
    df = pd.DataFrame({"cars": total_cars_history, "avg_vel": avg_velocity_history})

    # Create a 2D density heatmap
    fig = px.density_heatmap(
        df,
        x="cars",
        y="avg_vel",
        nbinsx=20,
        nbinsy=20,
        histfunc="count",
        color_continuous_scale=[
            (0.0, "black"),  # 0% of max count -> black (no data)
            (0.33, "red"),  # low fraction -> red
            (0.66, "yellow"),  # mid-range -> yellow
            (1.0, "green"),  # max count -> green
        ],
        title="Total Cars vs. Average Velocity Heatmap",
    )

    fig.update_layout(
        xaxis_title="Total Cars in Sim",
        yaxis_title="Average Velocity (units/s)",
    )

    # Configure hovertemplate to show bin counts
    fig.update_traces(
        hovertemplate=("Total Cars: %{x}<br>" "Avg Velocity: %{y}<br>" "Count: %{z}")
    )

    return fig
