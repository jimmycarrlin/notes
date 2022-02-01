# Run this app with `dashboard-тестовое_задание-valiotti.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import os
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_digit(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# DATA

app = dash.Dash(external_stylesheets=["assets/html-components.css", dbc.themes.BOOTSTRAP])

df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'games.csv'))
df.Year_of_Release = df.Year_of_Release.apply(lambda x: int(x) if is_digit(x) else None)
df.User_Score = df.User_Score.apply(lambda x: float(x) if is_number(x) else None)
df = df.dropna(axis=0).query('Year_of_Release >= 2000')
df.Year_of_Release = df.Year_of_Release.astype('int64')

# CORE ELEMENTS

genre_filter = dbc.Card([
    dbc.CardBody([
        html.Label("Выбрать жанр"),
        dcc.Dropdown(
            id='genres-input',
            options=[{'label': genre, 'value': genre} for genre in df.Genre.unique()],
            value=list(df.Genre.unique()),
            multi=True,
        )
    ], style={'height': '10rem'})
], style={'height': '8rem'})

rating_filter = dbc.Card([
    dbc.CardBody([
        html.Label("Выбрать возрастной рейтинг"),
        dcc.Dropdown(
            id='rating-input',
            options=[{'label': rating, 'value': rating} for rating in df.Rating.unique()],
            value=list(df.Rating.unique()),
            multi=True,
        )
    ])
], style={'height': '8rem', 'width': '32rem'})

num_games_graph = dbc.Card([
    dbc.CardBody([
        html.Label("Выпуск игр по годам и платформам",
                   style={'font-size': 24, 'text-align': 'left'}
                   ),
        dcc.Graph(id='num-games-vs-year', style={'height': '27rem'}),
        dcc.RangeSlider(
            id='year-range-input',
            min=df.Year_of_Release.min(),
            max=df.Year_of_Release.max(),
            value=[df.Year_of_Release.min(), df.Year_of_Release.max()],
            step=1,
            marks={year: str(year) for year in range(df.Year_of_Release.min(), df.Year_of_Release.max() + 1)}
        )
    ], style={'height': '34rem'})
])

score_graph = dbc.Card([
    dbc.CardBody([
        html.Label("Оценки игроков vs. оценки критиков",
                   style={'font-size': 24, 'text-align': 'left'}
                   ),
        dcc.Graph(id='critic-score-vs-user-score', style={'height': '30rem'})
    ], style={'height': '34rem'})
])

# LAYOUT

app.layout = html.Div([

    dbc.Row([
        html.H1("История состояния игровой индустрии"),
        html.Label("""Дашборд показывает историю выпуска игр по платформам (график слева) 
                    и корреляцию оценок игроков с оценками критиков (график справа).""",
                   style={'font-size': 14, 'text-align': 'left', 'color': '#808080'}
                   ),
        html.Label("""Счетчик количества выбранных игр и оба графика 
                    реагируют на изменения значений всех трех фильтров 
                    (выбор жанра, выбор возрастного рейтинга, временной промежуток) одновременно.""",
                   style={'font-size': 14, 'text-align': 'left', 'color': '#808080'}
                   )
    ], style={'margin-top': '8px', 'margin-bottom': '0px'}),

    dbc.Row([
        dbc.Col([
            html.Label("Выбрать жанр"),
            dcc.Dropdown(
                id='genres-input',
                options=[{'label': genre, 'value': genre} for genre in df.Genre.unique()],
                value=list(df.Genre.unique()),
                multi=True,
                style={'height': '4rem'}
            )
        ]),
        dbc.Col([
            html.Label("Выбрать возрастной рейтинг"),
            dcc.Dropdown(
                id='rating-input',
                options=[{'label': rating, 'value': rating} for rating in df.Rating.unique()],
                value=list(df.Rating.unique()),
                multi=True,
                style={'height': '4rem', 'width': '24rem'}
            )
        ])
    ], style={'margin-top': '8px', 'margin-bottom': '0px'}),

    dbc.Row([
        html.Div(id='num-games-output')
    ], style={'margin-top': '8px', 'margin-bottom': '0px'}),

    dbc.Row([
        dbc.Col([
            num_games_graph
        ], width=6),
        dbc.Col([
            score_graph
        ], width=6),
    ], style={'margin-top': '8px', 'margin-bottom': '0px'})

], style={'margin-left': '64px', 'margin-right': '64px', 'margin-top': '16px'})


# CALLBACKS

@app.callback(
    Output('num-games-output', 'children'),
    Output('num-games-vs-year', 'figure'),
    Output('critic-score-vs-user-score', 'figure'),
    Input('genres-input', 'value'),
    Input('rating-input', 'value'),
    Input('year-range-input', 'value')
)
def update(genres_input, rating_input, year_range_input):
    df2 = df.query(f"""Genre in {genres_input} \
                     & Rating in {rating_input} \
                     & Year_of_Release >= {year_range_input[0]} \
                     & Year_of_Release <= {year_range_input[1]}""")

    df1 = df2.groupby(['Platform', 'Year_of_Release']).count() \
             .reset_index() \
             .drop(columns=['Genre', 'Critic_Score', 'User_Score', 'Rating']) \
             .rename(columns={'Name': 'Num_Games'})

    num_games = len(df2)

    fig1 = px.area(df1, x='Year_of_Release', y='Num_Games',
                   color='Platform', line_group='Platform',
                   labels={'Year_of_Release': "Год выпуска", 'Num_Games': "Количество игр"},
                   color_discrete_sequence=px.colors.qualitative.Dark24
                   )
    fig1.update_traces(line=dict(width=0.5))

    fig2 = px.scatter(df2, x='User_Score', y='Critic_Score',
                      hover_name='Name', color='Genre',
                      labels={'User_Score': "Оценка игрока", 'Critic_Score': "Оценка критика"},
                      size='Critic_Score', size_max=7, opacity=0.3,
                      color_discrete_sequence=px.colors.qualitative.Dark24
                      )

    for fig in (fig1, fig2):
        fig.update_layout(
            yaxis={'gridcolor': '#e5e5e5'},
            plot_bgcolor='white',
            xaxis={'gridcolor': '#e5e5e5'}
        )

    return f"Выбрано игр: {num_games}", fig1, fig2


if __name__ == '__main__':
    app.run_server(debug=True)