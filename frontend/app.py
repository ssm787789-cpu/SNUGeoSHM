import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import os

# 절대 경로로 pages 폴더 지정
current_dir = os.path.dirname(os.path.abspath(__file__))
pages_folder = os.path.join(current_dir, 'pages')

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder=pages_folder,  # ← 절대 경로 사용
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# 서버 (배포용)
server = app.server

# 전체 레이아웃
app.layout = html.Div([
    # ========================================================================
    # 전역 데이터 저장소 (페이지 간 데이터 공유)
    # ========================================================================
    dcc.Store(id='turbine-data', storage_type='session', data={
        'locations': [],        # Map에서 설정: GeoJSON 데이터
        'frequencies': {},      # Analytics에서 설정: {turbine_id: {mode1, mode2, damping, timestamp}}
        'anomalies': {},        # Analytics에서 설정: {turbine_id: [anomaly_list]}
        'weather': {},          # Weather에서 설정: {timestamp, wind_speed, temperature}
        'last_updated': None    # 마지막 업데이트 시간
    }),
    
    # 헤더
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(html.H2("🌊 SNUGeoSHM", className="text-white"), width="auto"),
            ], align="center"),
        ]),
        color="primary",
        dark=True,
        className="mb-4"
    ),
    
    # 네비게이션 바
    dbc.Container([
        dbc.Nav([
            dbc.NavLink(" Home", href="/", active="exact"),
            dbc.NavLink(" Map", href="/map-overlay", active="exact"),
            dbc.NavLink(" Soil", href="/soil-profile", active="exact"),
            dbc.NavLink(" Foundation", href="/foundation-springs", active="exact"),
            dbc.NavLink(" FE Sim", href="/fe-simulation", active="exact"),
            dbc.NavLink(" Analytics", href="/analytics", active="exact"),
            dbc.NavLink(" Scenario", href="/scenario-builder", active="exact"),
            dbc.NavLink(" 3D View", href="/wtg-viewer", active="exact"),
        ], pills=True, className="mb-4"),
    ]),
    
    # 페이지 컨텐츠 (자동 렌더링)
    dbc.Container(dash.page_container, fluid=True),
    
    # 푸터
    html.Footer(
        dbc.Container([
            html.Hr(),
            html.P("© 2025 SNU GeoSHM | Offshore Wind Turbine Digital Twin Platform",
                   className="text-center text-muted")
        ]),
        className="mt-5"
    )
])

if __name__ == '__main__':
    print(f"Pages folder: {pages_folder}")
    print(f"Pages folder exists: {os.path.exists(pages_folder)}")
    
    # 로컬 개발용 실행
    app.run(debug=True, port=8050)