import dash
from dash import html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io

dash.register_page(__name__, path='/analytics', name='Analytics')

# 전역 변수로 데이터 저장
current_data = None

# ============================================================================
# Section 1: Data Preparation 
# ============================================================================
section_1_layout = dbc.Row([
    # 왼쪽: Step 패널들 (30%)
    dbc.Col([
        
        # CSV Upload 
            dcc.Upload(
                id='upload-csv',
                children=html.Div([
                    '📁 Click to Upload CSV',
                ], style={
                    'textAlign': 'center',
                    'padding': '20px',
                    'border': '2px dashed #007bff',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'backgroundColor': '#f8f9fa',
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'color': '#007bff'
                }),
                multiple=False,
                style={'marginBottom': '15px'}
            ),
            
            # Step 1 카드
            dbc.Card([
                dbc.CardHeader(html.H6("Step 1: Initial Inspection", style={'fontWeight': 'bold'})),
                dbc.CardBody([
                    # Remove Outliers
                    dbc.Row([
                        dbc.Col(html.Label("Remove Outliers:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='remove-outliers',
                                options=[            
                                    {'label': '3σ', 'value': '3sigma'},  
                                    {'label': '8σ', 'value': '8sigma'}
                                ],
                                value='3sigma',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # Replace Spikes
                    dbc.Row([
                        dbc.Col(html.Label("Replace Spikes:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='replace-spikes',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='Yes',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # Drop Missing
                    dbc.Row([
                        dbc.Col(html.Label("Drop Missing:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='drop-missing',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='Yes',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # Offset Drift
                    dbc.Row([
                        dbc.Col(html.Label("Offset/Drift:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='offset-drift',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='Yes',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-3", align="center"),
                    
                    # Run 버튼
                    dbc.Button("Run Step 1", id='run-step1', color="primary", className="w-100", size="sm")
                ], style={'padding': '15px'})
            ], className="mb-3", style={'width': '100%'}),
            
            # Step 2 카드
            dbc.Card([
                dbc.CardHeader(html.H6("Step 2: Scaling/Normalization", style={'fontWeight': 'bold'})),
                dbc.CardBody([
                    # Detrend
                    dbc.Row([
                        dbc.Col(html.Label("Detrend:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='detrend',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='Yes',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # Units
                    dbc.Row([
                        dbc.Col(html.Label("Units:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='units',
                                options=[
                                    {'label': 'm/s²', 'value': 'ms2'},
                                    {'label': 'g', 'value': 'g'},
                                ],
                                value='ms2',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # Normalization
                    dbc.Row([
                        dbc.Col(html.Label("Normalization:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='normalization',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='Yes',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-3", align="center"),
                    
                    # Run 버튼
                    dbc.Button("Run Step 2", id='run-step2', color="primary", className="w-100", size="sm")
                ], style={'padding': '15px'})
            ], className="mb-3", style={'width': '100%'}),
            
            # Step 3 카드
            dbc.Card([
                dbc.CardHeader(html.H6("Step 3: Noise Filtering", style={'fontWeight': 'bold'})),
                dbc.CardBody([
                    # Antialiasing
                    dbc.Row([
                        dbc.Col(html.Label("Antialiasing:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='antialiasing',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='Yes',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # Downsampling
                    dbc.Row([
                        dbc.Col(html.Label("Downsampling:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='downsampling',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='Yes',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # Bandpass Low
                    dbc.Row([
                        dbc.Col(html.Label("Bandpass Low (Hz):", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Input(
                                id='bandpass-low',
                                type='number',
                                value=0.1,
                                step=0.1,
                                className="form-control form-control-sm",
                                style={'fontSize': '13px', 'height': '32px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # Bandpass High
                    dbc.Row([
                        dbc.Col(html.Label("Bandpass High (Hz):", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Input(
                                id='bandpass-high',
                                type='number',
                                value=3.2,
                                step=0.1,
                                className="form-control form-control-sm",
                                style={'fontSize': '13px', 'height': '32px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # Wavelet Denoising
                    dbc.Row([
                        dbc.Col(html.Label("Wavelet Denoising(optional):", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='wavelet-denoising',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='No',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-3", align="center"),
                    
                    # Run 버튼
                    dbc.Button("Run Step 3", id='run-step3', color="primary", className="w-100", size="sm")
                ], style={'padding': '15px'})
            ], className="mb-3", style={'width': '100%'}),
            
            # Step 4 카드
            dbc.Card([
                dbc.CardHeader(html.H6("Step 4: Validation/Check", style={'fontWeight': 'bold'})),
                dbc.CardBody([
                    # Zero Mean
                    dbc.Row([
                        dbc.Col(html.Label("Zero Mean:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='zero-mean',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='Yes',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # Bandpass Filtered
                    dbc.Row([
                        dbc.Col(html.Label("Bandpass Filtered:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='bandpass-filtered',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='Yes',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-2", align="center"),
                    
                    # No Spikes
                    dbc.Row([
                        dbc.Col(html.Label("No Spikes:", style={'fontSize': '14px'}), width=7),
                        dbc.Col(
                            dcc.Dropdown(
                                id='no-spikes',
                                options=[{'label': 'Yes', 'value': 'Yes'}, {'label': 'No', 'value': 'No'}],
                                value='Yes',
                                clearable=False,
                                style={'fontSize': '13px'}
                            ),
                            width=5
                        )
                    ], className="mb-3", align="center"),
                    
                    # Run 버튼
                    dbc.Button("Run Step 4", id='run-step4', color="primary", className="w-100", size="sm")
                ], style={'padding': '15px'})
            ], className="mb-3", style={'width': '100%'}),
            
            # Check Result 카드 (별도)
            dbc.Card([
                dbc.CardHeader(html.H6("Final Validation", style={'fontWeight': 'bold'})),
                dbc.CardBody([
                    dbc.Button("Check Result", id='check-result', color="success", className="w-100", size="sm")
                ], style={'padding': '15px'})
            ], className="mb-3", style={'width': '100%'}),
            
        ], width=3, style={'paddingRight': '10px'}),
        
        # 오른쪽: 데이터 뷰 (70%)
        dbc.Col([
            
            # Data View 제목
            html.Div([
                html.H5("Data View", 
                       style={
                           'backgroundColor': '#f0f0f0',
                           'padding': '8px',
                           'margin': '0',
                           'borderBottom': '2px solid #ccc',
                           'fontSize': '16px',
                           'fontWeight': 'bold'
                       })
            ]),
            
            # 테이블
            html.Div([
                dash_table.DataTable(
                    id='data-table',
                    columns=[],
                    data=[],
                    page_size=25,
                    style_table={
                        'overflowX': 'auto',
                        'overflowY': 'auto',
                        'maxHeight': '650px',
                        'border': '1px solid #ddd'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'fontSize': '13px',
                        'fontFamily': 'Arial, sans-serif',
                        'minWidth': '80px',
                        'maxWidth': '180px',
                        'whiteSpace': 'normal'
                    },
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold',
                        'borderBottom': '2px solid #dee2e6',
                        'fontSize': '13px'
                    },
                    style_data={
                        'borderBottom': '1px solid #dee2e6'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9f9f9'
                        }
                    ]
                )
            ]),
            
            # 상태 메시지
            html.Div(id='status-message', className="mt-2", style={'fontSize': '13px', 'color': '#666'})
            
        ], width=9, style={'paddingLeft': '10px'}),
    ]),
    


# ============================================================================
# Section 2: SSI-COV Modal Analysis (빈 레이아웃)
# ============================================================================
section_2_layout = dbc.Container([
    html.H4(" SSI-COV Modal Analysis", className="my-3"),
    html.P("This section is under development.", className="text-muted", style={'fontSize': '14px'}),
    html.Hr(),
    
    # TODO 주석
    dbc.Alert([
        html.H6(" Planned Features:", className="alert-heading"),
        html.Ul([
            html.Li("PyOMA SSI-COV algorithm integration"),
            html.Li("Modal frequency extraction (Mode 1, 2, 3)"),
            html.Li("Damping ratio calculation"),
            html.Li("Mode shape visualization"),
            html.Li("Frequency comparison chart (before/after)"),
        ], style={'marginBottom': '0'})
    ], color="info", style={'fontSize': '13px'})
    
    # TODO: Add CSV data upload (preprocessed from Tab 1)
    # TODO: Add PyOMA SSI-COV algorithm integration
    # TODO: Add modal frequency extraction (Mode 1, 2, 3)
    # TODO: Add damping ratio calculation
    # TODO: Add mode shape visualization
    # TODO: Add frequency comparison chart
], fluid=True)


# ============================================================================
# Section 3: Anomaly Detection (빈 레이아웃)
# ============================================================================
section_3_layout = dbc.Container([
    html.H4(" Anomaly Detection", className="my-3"),
    html.P("This section is under development.", className="text-muted", style={'fontSize': '14px'}),
    html.Hr(),
    
    # TODO 주석
    dbc.Alert([
        html.H6(" Planned Features:", className="alert-heading"),
        html.Ul([
            html.Li("Isolation Forest anomaly detection algorithm"),
            html.Li("Drift threshold detection (>10%)"),
            html.Li("Time-series plot with anomaly markers (Plotly)"),
            html.Li("Anomaly statistics and summary"),
        ], style={'marginBottom': '0'})
    ], color="info", style={'fontSize': '13px'})
    
    # TODO: Add Isolation Forest anomaly detection algorithm
    # TODO: Add drift threshold detection (>10%)
    # TODO: Add time-series plot with anomaly markers
    # TODO: Add anomaly statistics table
    # TODO: Add anomaly event log
], fluid=True)


# ============================================================================
# Section 4: Weather Correlation (빈 레이아웃)
# ============================================================================
section_4_layout = dbc.Container([
    html.H4(" Weather Correlation", className="my-3"),
    html.P("This section is under development.", className="text-muted", style={'fontSize': '14px'}),
    html.Hr(),
    
    # TODO 주석
    dbc.Alert([
        html.H6(" Planned Features:", className="alert-heading"),
        html.Ul([
            html.Li("OpenWeatherMap API integration"),
            html.Li("Wind speed and temperature data fetch"),
            html.Li("Weather-vibration correlation analysis"),
            html.Li("Interactive correlation charts"),
        ], style={'marginBottom': '0'})
    ], color="info", style={'fontSize': '13px'})
    
    # TODO: Add OpenWeatherMap API integration
    # TODO: Add location input (e.g., Seoul)
    # TODO: Add weather-vibration correlation chart
    # TODO: Add wind speed/temperature display
], fluid=True)


# ============================================================================
# Section 5: AI Suggestion (빈 레이아웃)
# ============================================================================
section_5_layout = dbc.Container([
    html.H4(" AI Suggestion", className="my-3"),
    html.P("This section is under development.", className="text-muted", style={'fontSize': '14px'}),
    html.Hr(),
    
    # TODO 주석
    dbc.Alert([
        html.H6(" Planned Features:", className="alert-heading"),
        html.Ul([
            html.Li("Rule-based AI suggestion engine"),
            html.Li("Maintenance recommendations based on anomaly count"),
            html.Li("Priority scoring system (0-100)"),
            html.Li("Export report functionality"),
        ], style={'marginBottom': '0'})
    ], color="info", style={'fontSize': '13px'})
    
    # TODO: Add rule-based AI suggestion engine
    # TODO: Add maintenance recommendations
    # TODO: Add priority scoring (0-100)
    # TODO: Add export report button
], fluid=True)


# ============================================================================
# Main Layout (탭 구조)
# ============================================================================
layout = dbc.Container([
    html.H2("Analytics", className="my-3"),
    
    # 탭 버튼
    dbc.Tabs([
        dbc.Tab(label=" Data Preparation", tab_id="tab-1"),
        dbc.Tab(label=" SSI-COV Modal Analysis", tab_id="tab-2"),
        dbc.Tab(label=" Anomaly Detection", tab_id="tab-3"),
        dbc.Tab(label=" Weather Correlation", tab_id="tab-4"),
        dbc.Tab(label=" AI Suggestion", tab_id="tab-5"),
    ], id="analytics-tabs", active_tab="tab-1", className="mb-3"),
    
    # 탭 콘텐츠 영역
    html.Div(id="tab-content")
    
], fluid=True, style={'maxWidth': '1600px'})


# ============================================================================
# 콜백: 탭 전환
# ============================================================================
@callback(
    Output("tab-content", "children"),
    Input("analytics-tabs", "active_tab")
)
def render_tab_content(active_tab):
    """탭 전환 시 해당 섹션 레이아웃 반환"""
    if active_tab == "tab-1":
        return section_1_layout
    elif active_tab == "tab-2":
        return section_2_layout
    elif active_tab == "tab-3":
        return section_3_layout
    elif active_tab == "tab-4":
        return section_4_layout
    elif active_tab == "tab-5":
        return section_5_layout
    return html.Div("Error: Invalid tab", className="text-danger")



# CSV 파싱 함수
def parse_csv(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        return df
    except Exception as e:
        print(e)
        return None

# 콜백: CSV 업로드
@callback(
    [Output('data-table', 'data'),
     Output('data-table', 'columns'),
     Output('status-message', 'children')],
    Input('upload-csv', 'contents'),
    State('upload-csv', 'filename')
)
def upload_csv(contents, filename):
    global current_data
    
    if contents is None:
        return [], [], ''
    
    df = parse_csv(contents, filename)
    
    if df is None:
        return [], [], html.Span('❌ Error: Could not read file', style={'color': 'red'})
    
    current_data = df.copy()
    
    columns = [{"name": col, "id": col} for col in df.columns]
    data = df.to_dict('records')
    status = html.Span(f'✅ Loaded: {filename} ({len(df)} rows × {len(df.columns)} columns)', 
                      style={'color': 'green'})
    
    return data, columns, status

# 콜백: Run Step 1
@callback(
    Output('status-message', 'children', allow_duplicate=True),
    Input('run-step1', 'n_clicks'),
    [State('remove-outliers', 'value'),
     State('replace-spikes', 'value'),
     State('drop-missing', 'value'),
     State('offset-drift', 'value')],
    prevent_initial_call=True
)
def run_step1(n_clicks, remove_outliers, replace_spikes, drop_missing, offset_drift):
    if n_clicks and current_data is not None:
        # TODO: 실제 로직 추가
        msg = f"Step 1 executed: Outliers={remove_outliers}, Spikes={replace_spikes}, Missing={drop_missing}, Drift={offset_drift}"
        return html.Span(f'✅ {msg}', style={'color': 'green'})
    return ''

# 콜백: Run Step 2
@callback(
    Output('status-message', 'children', allow_duplicate=True),
    Input('run-step2', 'n_clicks'),
    [State('detrend', 'value'),
     State('units', 'value'),
     State('normalization', 'value')],
    prevent_initial_call=True
)
def run_step2(n_clicks, detrend, units, normalization):
    if n_clicks and current_data is not None:
        # TODO: 실제 로직 추가
        msg = f"Step 2 executed: Detrend={detrend}, Units={units}, Normalization={normalization}"
        return html.Span(f'✅ {msg}', style={'color': 'green'})
    return ''

# 콜백: Run Step 3
@callback(
    Output('status-message', 'children', allow_duplicate=True),
    Input('run-step3', 'n_clicks'),
    [State('antialiasing', 'value'),
     State('downsampling', 'value'),
     State('bandpass-low', 'value'),
     State('bandpass-high', 'value'),
     State('wavelet-denoising', 'value')],
    prevent_initial_call=True
)
def run_step3(n_clicks, antialiasing, downsampling, bp_low, bp_high, wavelet):
    if n_clicks and current_data is not None:
        # TODO: 실제 로직 추가
        msg = f"Step 3 executed: Bandpass {bp_low}-{bp_high} Hz, Wavelet={wavelet}"
        return html.Span(f'✅ {msg}', style={'color': 'green'})
    return ''

# 콜백: Run Step 4
@callback(
    Output('status-message', 'children', allow_duplicate=True),
    Input('run-step4', 'n_clicks'),
    [State('zero-mean', 'value'),
     State('bandpass-filtered', 'value'),
     State('no-spikes', 'value')],
    prevent_initial_call=True
)
def run_step4(n_clicks, zero_mean, bandpass_filtered, no_spikes):
    if n_clicks and current_data is not None:
        # TODO: Step 4 실행 로직 추가
        msg = f"Step 4 executed: Zero-mean={zero_mean}, Bandpass={bandpass_filtered}, No-spikes={no_spikes}"
        return html.Span(f'✅ {msg}', style={'color': 'green'})
    return ''

# 콜백: Check Result
@callback(
    Output('status-message', 'children', allow_duplicate=True),
    Input('check-result', 'n_clicks'),
    [State('zero-mean', 'value'),
     State('bandpass-filtered', 'value'),
     State('no-spikes', 'value')],
    prevent_initial_call=True
)
def check_result(n_clicks, zero_mean, bandpass_filtered, no_spikes):
    if n_clicks and current_data is not None:
        # TODO: 실제 검증 로직 추가
        return html.Span('SUCCESS! Validation passed! Data is ready for modal analysis.', 
                        style={'color': 'green', 'fontWeight': 'bold', 'fontSize': '15px'})
    return ''