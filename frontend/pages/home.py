import dash
from dash import html, Input, Output, State, callback
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', name='Home')

layout = dbc.Container([
    html.H1("Welcome to SNUGeoSHM", className="text-center my-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🌊 Overview", className="card-title"),
                    html.P("Digital Twin Platform for Offshore Wind Turbine Structural Health Monitoring"),
                    html.Ul([
                        html.Li("Geotechnical Integration (GemPy)"),
                        html.Li("Foundation Analysis (Optum GX)"),
                        html.Li("Finite Element Simulation (OpenSeesPy)"),
                        html.Li("Data Preprocessing Pipeline (4-Step)"),
                        html.Li("System Identification (SSI-COV Modal Analysis)"),
                        html.Li("Anomaly Detection (Isolation Forest)"),
                        html.Li("Weather Correlation Analysis (OpenWeatherMap)"),
                        html.Li("AI-based Maintenance Suggestions"),
                    ])
                ])
            ], className="mb-4")
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🚀 Quick Start", className="card-title"),
                    html.Ol([
                        html.Li([html.Strong("Map: "), "View turbine locations"]),
                        html.Li([html.Strong("Soil: "), "Generate 3D geological model"]),
                        html.Li([html.Strong("Foundation: "), "Calculate stiffness springs"]),
                        html.Li([html.Strong("FE Sim: "), "Run structural analysis"]),
                        html.Li([
                            html.Strong("Analytics: "),
                            "Process & analyze field data ",
                            html.A(
                                "[▼]",
                                id="analytics-toggle",
                                href="#",
                                style={
                                    'textDecoration': 'none',
                                    'color': '#007bff',
                                    'cursor': 'pointer',
                                    'fontSize': '14px',
                                    'marginLeft': '5px'
                                }
                            ),
                            dbc.Collapse([
                                html.Ul([
                                    html.Li("Data Preparation: Preprocess field data (4-Step)"),
                                    html.Li("SSI-COV: Extract modal frequencies"),
                                    html.Li("Anomaly Detection: Detect structural anomalies"),
                                    html.Li("Weather Correlation: Analyze environmental impact"),
                                    html.Li("AI Suggestion: Get maintenance recommendations"),
                                ], style={
                                    'marginTop': '8px',
                                    'marginLeft': '0px',
                                    'fontSize': '14px',
                                    'color': '#555',
                                    'listStyleType': 'disc'
                                })
                            ], id="analytics-collapse", is_open=True)
                        ]),
                        html.Li([html.Strong("Scenario: "), "Test scenarios with AI scoring"]),
                        html.Li([html.Strong("3D View: "), "Visualize turbine & geological model (3D)"]),
                    ])
                ])
            ], className="mb-4")
        ], width=6),
    ]),
    
    dbc.Alert([
        html.H4("📚 Documentation", className="alert-heading"),
        html.P("For detailed information, visit:"),
        html.Ul([
            html.Li(html.A("User Guide", href="#")),
            html.Li(html.A("API Reference", href="#")),
            html.Li(html.A("GitHub Repository", href="#")),
        ])
    ], color="info")
])


# ============================================================================
# 콜백: Analytics 세부 항목 토글
# ============================================================================
@callback(
    Output("analytics-collapse", "is_open"),
    Input("analytics-toggle", "n_clicks"),
    State("analytics-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_analytics(n_clicks, is_open):
    """Analytics 세부 항목 펼치기/접기"""
    if n_clicks:
        return not is_open
    return is_open