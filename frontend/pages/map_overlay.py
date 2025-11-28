import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/map-overlay', name='Map Overlay')

layout = dbc.Container([
    html.H1(" Wind Farm Map", className="text-center my-4"),
    
    # 업로드 섹션
    dbc.Card([
        dbc.CardHeader("Upload Turbine Locations"),
        dbc.CardBody([
            dcc.Upload(
                id='upload-geojson',
                children=dbc.Button('Upload GeoJSON', color='primary'),
                multiple=False
            ),
            html.Div(id='upload-status', className='mt-2')
        ])
    ], className="mb-4"),
    
    # 지도 섹션
    dbc.Card([
        dbc.CardHeader("Map View"),
        dbc.CardBody([
            html.Div([
                html.P("🗺️ Map will render here with dash-leaflet", 
                       className="text-center text-muted",
                       style={'padding': '100px'})
            ], id='map-container', style={'height': '500px', 'border': '1px dashed #ccc'})
        ])
    ])
], fluid=True)

# 더미 콜백
@callback(
    Output('upload-status', 'children'),
    Input('upload-geojson', 'filename')
)
def update_status(filename):
    if filename:
        return dbc.Alert(f"✅ Loaded: {filename}", color="success")
    return ""