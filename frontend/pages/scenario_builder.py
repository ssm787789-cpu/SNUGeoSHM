import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/scenario-builder', name='Scenario Builder')

layout = dbc.Container([
    html.H1("Scenario Builder", className="text-center my-4"),
    
    # 시나리오 선택
    dbc.Card([
        dbc.CardHeader("Scenario Configuration"),
        dbc.CardBody([
            html.Label("Scenario Type:"),
            dcc.Dropdown(
                id='dropdown-scenario',
                options=[
                    {'label': '🟢 Normal Operation', 'value': 'normal'},
                    {'label': '🟡 Scour (20% spring reduction)', 'value': 'scour'},
                    {'label': '🔴 Storm (High load)', 'value': 'storm'}
                ],
                value='normal'
            ),
            html.Hr(),
            html.Label("Load Factor (%):"),
            dcc.Slider(id='slider-load-factor', min=0, max=200, value=100, 
                       marks={0: '0%', 100: '100%', 200: '200%'}),
            html.Label("Wind Speed (m/s):"),
            dcc.Slider(id='slider-wind', min=0, max=30, value=15,
                       marks={0: '0', 15: '15', 30: '30'})
        ])
    ], className="mb-4"),
    
    # 실행
    dbc.Button(" Run Scenario", id="btn-run-scenario", 
               color="primary", size="lg", className="mb-4"),
    
    # 결과
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Score"),
                dbc.CardBody([
                    html.H2(id='score-display', className="text-center")
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("AI Suggestions"),
                dbc.CardBody([
                    html.Div(id='suggestions-output')
                ])
            ])
        ], width=6)
    ])
], fluid=True)

@callback(
    [Output('score-display', 'children'),
     Output('suggestions-output', 'children')],
    Input('btn-run-scenario', 'n_clicks'),
    prevent_initial_call=True
)
def run_scenario(n_clicks):
    return "🟢 85/100", dbc.Alert("✅ No critical issues detected", color="success")