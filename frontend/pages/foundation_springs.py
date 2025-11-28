import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/foundation-springs', name='Foundation Springs')

layout = dbc.Container([
    html.H1(" Foundation Stiffness Calculator", className="text-center my-4"),
    
    # 입력 파라미터
    dbc.Card([
        dbc.CardHeader("Monopile Parameters"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Diameter (m):"),
                    dbc.Input(id='input-diameter', type='number', value=8, min=1, max=20)
                ], width=4),
                dbc.Col([
                    html.Label("Depth (m):"),
                    dbc.Input(id='input-depth', type='number', value=30, min=10, max=50)
                ], width=4),
                dbc.Col([
                    html.Label("Lateral Load (N):"),
                    dbc.Input(id='input-load', type='number', value=1e6, min=1e5, max=1e7)
                ], width=4),
            ])
        ])
    ], className="mb-4"),
    
    # 계산 버튼
    dbc.Button("⚙️ Calculate Springs", id="btn-calc-springs", 
               color="primary", size="lg", className="mb-4"),
    
    # 결과
    dbc.Card([
        dbc.CardHeader("Stiffness Results"),
        dbc.CardBody([
            html.Div(id='springs-output')
        ])
    ])
], fluid=True)

@callback(
    Output('springs-output', 'children'),
    Input('btn-calc-springs', 'n_clicks'),
    State('input-diameter', 'value'),
    State('input-depth', 'value'),
    State('input-load', 'value'),
    prevent_initial_call=True
)
def calculate_springs(n_clicks, diameter, depth, load):
    return dbc.Alert([
        html.H5("✅ Calculation Complete (Demo)"),
        html.P(f"K_xx: 1.0e9 N/m"),
        html.P(f"K_yy: 1.2e9 N/m"),
        html.P(f"K_zz: 5.0e9 N/m"),
        html.Small(f"Input: D={diameter}m, L={depth}m, F={load:.1e}N")
    ], color="success")