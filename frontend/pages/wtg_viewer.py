import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/wtg-viewer', name='3D Viewer')

layout = dbc.Container([
    html.H1(" 3D Wind Turbine Viewer", className="text-center my-4"),
    
    # 파일 업로드
    dbc.Card([
        dbc.CardHeader("Load 3D Model"),
        dbc.CardBody([
            dcc.Upload(
                id='upload-vtk',
                children=dbc.Button('Upload VTK File', color='primary'),
                multiple=False
            ),
            html.Div(id='vtk-upload-status', className='mt-2')
        ])
    ], className="mb-4"),
    
    # 3D 뷰어
    dbc.Card([
        dbc.CardHeader("3D View"),
        dbc.CardBody([
            html.Div([
                html.P("🌐 3D viewer will render here with dash-vtk", 
                       className="text-center text-muted",
                       style={'padding': '150px'})
            ], id='vtk-container', style={'height': '600px', 'border': '1px dashed #ccc'})
        ])
    ])
], fluid=True)

@callback(
    Output('vtk-upload-status', 'children'),
    Input('upload-vtk', 'filename')
)
def update_vtk_status(filename):
    if filename:
        return dbc.Alert(f"✅ Loaded: {filename}", color="success")
    return ""