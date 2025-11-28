import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/fe-simulation', name='FE Simulation')

layout = dbc.Container([
    html.H1(" Finite Element Analysis", className="text-center my-4"),
    
    # 입력
    dbc.Card([
        dbc.CardHeader("Load Configuration"),
        dbc.CardBody([
            dcc.Upload(
                id='upload-springs',
                children=dbc.Button('Load Springs JSON', color='secondary'),
                multiple=False
            ),
            html.Hr(),
            html.Label("Load Magnitude:"),
            dcc.Slider(
                id='slider-load',
                min=0, max=2e6, value=1e6, step=1e5,
                marks={0: '0', 1e6: '1e6', 2e6: '2e6'},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ])
    ], className="mb-4"),
    
    # 실행
    dbc.Button("▶️ Run Simulation", id="btn-run-fe", 
               color="success", size="lg", className="mb-4"),
    
    # 결과
    dbc.Card([
        dbc.CardHeader("Modal Analysis Results"),
        dbc.CardBody([
            html.Div(id='fe-output')
        ])
    ])
], fluid=True)

@callback(
    Output('fe-output', 'children'),
    Input('btn-run-fe', 'n_clicks'),
    prevent_initial_call=True
)
def run_simulation(n_clicks):
    return dbc.Alert([
        html.H5("✅ Simulation Complete (Demo)"),
        html.P("Mode 1: 0.28 Hz (1st Fore-Aft)"),
        html.P("Mode 2: 0.32 Hz (1st Side-Side)"),
        html.P("Mode 3: 1.05 Hz (2nd Fore-Aft)")
    ], color="success")