import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/soil-profile', name='Soil Profile')

layout = dbc.Container([
    html.H1(" Soil Profile Generator", className="text-center my-4"),
    
    # 파일 업로드
    dbc.Card([
        dbc.CardHeader("Upload Soil Data"),
        dbc.CardBody([
            html.P("Upload the following CSV files:"),
            dbc.Row([
                dbc.Col([
                    html.Label("Borehole Data:"),
                    dcc.Upload(
                        id='upload-borehole',
                        children=dbc.Button('Browse...', size='sm'),
                        multiple=False
                    )
                ], width=4),
                dbc.Col([
                    html.Label("Orientations:"),
                    dcc.Upload(
                        id='upload-orientations',
                        children=dbc.Button('Browse...', size='sm'),
                        multiple=False
                    )
                ], width=4),
                dbc.Col([
                    html.Label("Surface Points:"),
                    dcc.Upload(
                        id='upload-surface',
                        children=dbc.Button('Browse...', size='sm'),
                        multiple=False
                    )
                ], width=4),
            ]),
            html.Div(id='upload-soil-status', className='mt-3')
        ])
    ], className="mb-4"),
    
    # 생성 버튼
    dbc.Button("🔧 Generate Soil Model", id="btn-generate-soil", 
               color="success", size="lg", className="mb-4"),
    
    # 결과
    dbc.Card([
        dbc.CardHeader("Generated Model"),
        dbc.CardBody([
            html.Div(id='soil-output', children=[
                html.P("Upload files and click 'Generate' to create 3D soil model",
                       className="text-center text-muted")
            ])
        ])
    ])
], fluid=True)

@callback(
    Output('soil-output', 'children'),
    Input('btn-generate-soil', 'n_clicks'),
    prevent_initial_call=True
)
def generate_soil(n_clicks):
    return dbc.Alert([
        html.H5("✅ Model Generated (Demo)"),
        html.P("Layers: Clay (-5m), Sand (-15m)"),
        html.P("Properties: Su=30 kPa, φ=35°")
    ], color="success")