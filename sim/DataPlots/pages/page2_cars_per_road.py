from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from server import cars_per_road_history

layout = html.Div([
    html.H1("Page 2: Cars per Road Over Time"),
    html.P("A line chart showing how many cars each road has over time."),
    dcc.Graph(id="cars-per-road-plot"),
    html.Br(),
    dcc.Link("Go to Page 1", href="/"), html.Br(),
    dcc.Link("Go to Page 3", href="/page-3"), html.Br(),
    dcc.Link("Go to Page 4", href="/page-4"), html.Br(),
    dcc.Link("Go to Page 5", href="/page-5"), html.Br(),
    dcc.Link("Go to Page 6", href="/page-6"),
])

@callback(Output("cars-per-road-plot", "figure"),
          Input("interval-component", "n_intervals"))
def update_cars_per_road_plot(_):
    """
    Displays how the car count in each road evolves over time.
    """
    if not cars_per_road_history:
        return px.line(
            pd.DataFrame({'iteration': [], 'road_id': [], 'car_count': []}),
            x='iteration', y='car_count', color='road_id',
            title="Cars in Each Road Over Time (No Data)"
        )

    rows = []
    for road_id, counts in cars_per_road_history.items():
        for i, ccount in enumerate(counts):
            rows.append((i, road_id, ccount))

    df = pd.DataFrame(rows, columns=["iteration", "road_id", "car_count"])
    df["road_id"] = df["road_id"].astype(str)

    fig = px.line(
        df,
        x="iteration",
        y="car_count",
        color="road_id",
        title="Number of Cars in Each Road Over Time"
    )
    fig.update_layout(
        xaxis_title="Iteration",
        yaxis_title="Number of Cars"
    )
    fig.update_traces(
        hovertemplate="Iteration: %{x}<br>Road: %{fullData.name}<br>Car Count: %{y}"
    )
    return fig
