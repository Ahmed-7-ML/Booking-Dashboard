# 1- Import Libraries & Prepare the DataFrame
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings(action='ignore')

# Load data , Fix Data Types & Extract Year From Date
df = pd.read_csv("booking.csv")
df['date of reservation'] = pd.to_datetime(
    df['date of reservation'], errors='coerce')
df['year'] = df['date of reservation'].dt.year
df['year'] = df['year'].fillna(method='ffill').astype('int64')

# App Creation
app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

# Layout Building
app.layout = dbc.Container(children=[
    dbc.NavbarSimple(
        brand=html.Span("Booking Dashboard", className="mx-auto fw-bold fs-4"),
        color="primary",
        dark=True,
        className='mb-3',
        children=[
            html.A(
                "By: Ahmed Akram | Triple AI",
                href="https://www.linkedin.com/in/ahmed-akram-kamel-amer",
                target="_blank",
                className="ms-2 text-light small",
                style={"fontSize": "14px", "textDecoration": "none"}
            )
        ]
    ),

    # --- Selectors Section ---
    dbc.Row(html.H2("Selectors", className='text-center my-3')),
    dbc.Row([
        dbc.Col([
            html.Label("Select a Category"),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': col, 'value': col} for col in [
                    "type of meal", "room type", "market segment type", "booking status"]],
                value='type of meal',
                clearable=False
            ),
            html.Label("Select a Value"),
            dcc.Dropdown(id='value-dropdown', clearable=True)
        ], width=6, className="mb-3")
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Select a Year"),
            dcc.RangeSlider(
                id="year-range-slider",
                min=df['year'].min(),
                max=df['year'].max(),
                step=1,
                value=[df['year'].min(), df['year'].max()],
                marks={str(year): str(year) for year in sorted(df['year'].unique())}
            )
        ], width=12, className='mb-4'),

        dbc.Col([
            html.Label("Booking Status"),
            dcc.Checklist(
                id="booking-status-checklist",
                options=[{'label': v, 'value': v} for v in df['booking status'].unique()],
                value=list(df['booking status'].unique()),
                inline=True,
                style={'padding': '5px'}
            ),

            html.Br(),

            html.Label("Repeated Guest ?"),
            dcc.Checklist(
                id="repeated-guest-checklist",
                options=[
                    {"label": "New", "value": 0},
                    {"label": "Repeated", "value": 1}
                ],
                value=[0, 1],
                inline=True,
                style={'padding': '5px'}
            )
        ], width=6, className='mb-3')
    ]),

    # --- Graphs Section ---
    dbc.Row([html.H2("Top-Row Graphs", className="text-center my-3")]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="bar-graph"), width=6),
        dbc.Col(dcc.Graph(id="pie-graph"), width=6)
    ]),

    dbc.Row(html.H2("Middle-Row Graphs", className='text-center my-3')),
    dbc.Row([
        dbc.Col(dcc.Graph(id='box-graph'), width=6),
        dbc.Col(dcc.Graph(id='scatter-graph'), width=6)
    ]),

    dbc.Row(html.H2("Bottom-Row Graphs", className='text-center my-3')),
    dbc.Row(dcc.Graph(id='booking-bar-graph'))
], fluid=True)


# ---- Callbacks ----

# Dynamic Dropdown (values of selected category)
@app.callback(
    Output('value-dropdown', 'options'),
    Input('category-dropdown', 'value')
)
def set_value_for_category(category):
    return [{'label': col, 'value': col} for col in df[category].dropna().unique()]


@app.callback(
    [Output('bar-graph', 'figure'),
     Output('pie-graph', 'figure'),
     Output('box-graph', 'figure'),
     Output('scatter-graph', 'figure'),
     Output('booking-bar-graph', 'figure')],
    [Input('category-dropdown', 'value'),
    Input('value-dropdown', 'value'),
    Input('year-range-slider', 'value'),
    Input('booking-status-checklist', 'value'),
    Input('repeated-guest-checklist', 'value')]
)
def update_graphs(category, value, year_range, booking_status, repeated_guests):
    dff = df.copy()

    # Apply Filters
    dff = dff[
        (dff["year"].between(year_range[0], year_range[1])) &
        (dff["booking status"].isin(booking_status)) &
        (dff["repeated"].isin(repeated_guests))
    ]

    if value:
        dff = dff[dff[category] == value]

    # Figures
    bar_fig = px.histogram(dff, x=category, title=f"Counts by {category}")
    pie_fig = px.pie(dff, names="booking status", title="Canceled vs Not Canceled")
    box_fig = px.box(dff, x=category, y="average price", title="Average Price vs Category", color="booking status")
    scatter_fig = px.scatter(dff, x="lead time", y="average price", color="booking status", title="Lead Time vs Average Price")
    year_fig = px.bar(dff, y="booking status", color="booking status", title=f"Booking Status in {year_range[0]} - {year_range[1]}")

    return bar_fig, pie_fig, box_fig, scatter_fig, year_fig


# To Run My App
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
