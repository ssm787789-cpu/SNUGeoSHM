import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import json
import base64

dash.register_page(__name__, path='/map-overlay', name='Map Overlay')

# ============================================================================
# GeoJSON 파싱 함수
# ============================================================================
def parse_geojson(contents, filename):
    """
    업로드된 GeoJSON 파일 파싱
    
    Args:
        contents: Base64 인코딩된 파일 내용
        filename: 파일명
        
    Returns:
        tuple: (geojson_dict, error_message)
    """
    try:
        # Base64 디코딩
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # JSON 파싱
        geojson = json.loads(decoded.decode('utf-8'))
        
        # 유효성 검증
        if geojson.get('type') != 'FeatureCollection':
            return None, "❌ Invalid GeoJSON: Must be a FeatureCollection"
        
        if not geojson.get('features'):
            return None, "❌ Invalid GeoJSON: No features found"
        
        # 각 feature 검증
        for idx, feature in enumerate(geojson['features']):
            # geometry 확인
            if 'geometry' not in feature:
                return None, f"❌ Feature {idx+1}: Missing geometry"
            
            if feature['geometry'].get('type') != 'Point':
                return None, f"❌ Feature {idx+1}: Only Point geometry supported"
            
            # coordinates 확인
            coords = feature['geometry'].get('coordinates')
            if not coords or len(coords) != 2:
                return None, f"❌ Feature {idx+1}: Invalid coordinates"
            
            lon, lat = coords
            
            # 좌표 범위 확인
            if not (-180 <= lon <= 180):
                return None, f"❌ Feature {idx+1}: Invalid longitude ({lon})"
            
            if not (-90 <= lat <= 90):
                return None, f"❌ Feature {idx+1}: Invalid latitude ({lat})"
        
        return geojson, None
        
    except json.JSONDecodeError:
        return None, "❌ Invalid JSON format"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# ============================================================================
# Convex Hull 알고리즘 (순수 Python, scipy 불필요)
# ============================================================================
def convex_hull(points):
    """
    Graham Scan 알고리즘으로 Convex Hull 계산 (외곽 점들만 추출)
    
    Args:
        points: [[lat, lon], ...] 좌표 리스트
        
    Returns:
        list: 외곽 점들의 좌표 [[lat, lon], ...]
    """
    if len(points) < 3:
        return points
    
    # 1. 가장 아래(남쪽) 점 찾기 (y가 작은 점)
    start = min(points, key=lambda p: (p[0], p[1]))
    
    # 2. 시작점 기준 각도로 정렬
    import math
    
    def polar_angle(p):
        dx = p[1] - start[1]
        dy = p[0] - start[0]
        return math.atan2(dy, dx)
    
    sorted_points = sorted(points, key=polar_angle)
    
    # 3. Graham Scan
    hull = []
    
    for point in sorted_points:
        # 반시계방향이 아닌 점들 제거
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def cross_product(o, a, b):
    """
    외적 계산 (회전 방향 판단)
    > 0: 반시계방향
    < 0: 시계방향
    = 0: 일직선
    """
    return (a[1] - o[1]) * (b[0] - o[0]) - (a[0] - o[0]) * (b[1] - o[1])


# ============================================================================
# 경계 Polygon 자동 생성 함수
# ============================================================================
def create_boundary_polygon(geojson):
    """
    터빈 좌표들의 외곽선을 자동으로 연결하여 Polygon 생성
    
    Args:
        geojson: GeoJSON FeatureCollection
        
    Returns:
        list: Polygon 좌표 [[lat, lon], ...]
    """
    if not geojson or not geojson.get('features'):
        return None
    
    # Point 좌표만 추출
    points = []
    for feature in geojson['features']:
        if feature['geometry']['type'] == 'Point':
            lon, lat = feature['geometry']['coordinates']
            points.append([lat, lon])
    
    if len(points) < 3:
        return None
    
    # Convex Hull 계산 (외곽 터빈들만 연결)
    boundary = convex_hull(points)
    
    return boundary


# ============================================================================
# 터빈 레이어 생성 함수 (Polygon + CircleMarker)
# ============================================================================
def create_turbine_layers(geojson, frequencies=None):
    """
    GeoJSON에서 dash-leaflet 레이어 생성 (경계 Polygon + 터빈 CircleMarker)
    
    Args:
        geojson: GeoJSON FeatureCollection
        frequencies: 터빈별 주파수 딕셔너리 (optional)
        
    Returns:
        list: [Polygon, CircleMarker, CircleMarker, ...]
    """
    if not geojson or not geojson.get('features'):
        return []
    
    layers = []
    frequencies = frequencies or {}
    
    # 1. 경계 Polygon 생성
    boundary = create_boundary_polygon(geojson)
    if boundary:
        polygon = dl.Polygon(
            positions=boundary,
            color='purple',           # 보라색 테두리 (실선)
            fillColor='lavender',     # 옅은 보라색 채우기
            fillOpacity=0.4,          # 투명도
            weight=3                  # 선 두께
        )
        layers.append(polygon)
    
    # 2. 터빈 CircleMarker 생성
    for feature in geojson['features']:
        if feature['geometry']['type'] != 'Point':
            continue
        
        # 좌표 추출
        coords = feature['geometry']['coordinates']
        lon, lat = coords
        
        # 속성 추출
        props = feature.get('properties', {})
        turbine_id = props.get('id', 'Unknown')
        name = props.get('name', 'Unknown')
        capacity = props.get('capacity', 'N/A')
        install_year = props.get('install_year', 'N/A')
        status = props.get('status', 'unknown')
        
        # 주파수 데이터 확인
        freq = frequencies.get(turbine_id)
        
        # 팝업 내용 생성
        if freq:
            # Analytics 완료 후
            popup_content = html.Div([
                html.H6(f"{name} ({turbine_id})", style={'marginBottom': '10px', 'fontWeight': 'bold'}),
                html.Hr(style={'margin': '5px 0'}),
                html.P([
                    html.Strong("Capacity: "), f"{capacity}", html.Br(),
                    html.Strong("Install Year: "), f"{install_year}", html.Br(),
                    html.Strong("Status: "), f"{status.capitalize()} ✅"
                ], style={'fontSize': '13px', 'marginBottom': '10px'}),
                html.Hr(style={'margin': '5px 0'}),
                html.P([
                    html.Strong("Modal Analysis:"), html.Br(),
                    f"  Frequency: {freq['mode1']:.2f} Hz", html.Br(),
                    f"  Damping: {freq['damping']:.1f}%", html.Br(),
                    f"  Mode 1: {freq['mode1']:.2f} Hz", html.Br(),
                    f"  Mode 2: {freq['mode2']:.2f} Hz"
                ], style={'fontSize': '12px', 'backgroundColor': '#f0f0f0', 'padding': '8px', 'borderRadius': '4px'}),
                html.Small(f"Last Updated: {freq['timestamp']}", style={'color': '#666', 'fontSize': '11px'})
            ])
        else:
            # Analytics 전
            popup_content = html.Div([
                html.H6(f"{name} ({turbine_id})", style={'marginBottom': '10px', 'fontWeight': 'bold'}),
                html.Hr(style={'margin': '5px 0'}),
                html.P([
                    html.Strong("Capacity: "), f"{capacity}", html.Br(),
                    html.Strong("Install Year: "), f"{install_year}", html.Br(),
                    html.Strong("Status: "), f"{status.capitalize()}"
                ], style={'fontSize': '13px', 'marginBottom': '10px'}),
                html.Hr(style={'margin': '5px 0'}),
                html.P([
                    html.Strong("Modal Analysis:"), html.Br(),
                    "  Frequency: Not analyzed yet", html.Br(),
                    "  Damping: -"
                ], style={'fontSize': '12px', 'backgroundColor': '#fff3cd', 'padding': '8px', 'borderRadius': '4px'}),
                html.Small([
                    dbc.Button("Go to Analytics →", href="/analytics", size="sm", color="primary", 
                              style={'marginTop': '5px', 'fontSize': '11px'})
                ])
            ])
        
        # CircleMarker 생성 (점으로 표시)
        circle = dl.CircleMarker(
            center=[lat, lon],
            radius=8,                 # 점 크기 (픽셀)
            color='blue',             # 테두리 색
            fillColor='blue',         # 채우기 색
            fillOpacity=0.8,          # 투명도
            weight=2,                 # 테두리 두께
            children=[
                dl.Tooltip(name),     # 마우스 오버 시 이름 표시
                dl.Popup(popup_content, maxWidth=300)  # 클릭 시 상세 정보
            ]
        )
        
        layers.append(circle)
    
    return layers


# ============================================================================
# 지도 중심 계산 함수
# ============================================================================
def calculate_center(geojson):
    """
    GeoJSON 터빈들의 중심 좌표 계산
    
    Args:
        geojson: GeoJSON FeatureCollection
        
    Returns:
        list: [lat, lon]
    """
    if not geojson or not geojson.get('features'):
        return [34.87, 126.17]  # 기본값: 한국 서해안
    
    lats = []
    lons = []
    
    for feature in geojson['features']:
        coords = feature['geometry']['coordinates']
        lons.append(coords[0])
        lats.append(coords[1])
    
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    return [center_lat, center_lon]


# ============================================================================
# 레이아웃
# ============================================================================
layout = dbc.Container([
    html.H1(" Wind Farm Map", className="text-center my-4"),
    
    # 업로드 섹션
    dbc.Card([
        dbc.CardHeader("Upload Turbine Locations"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Upload(
                        id='upload-geojson',
                        children=dbc.Button('📁 Upload GeoJSON', color='primary', className='w-100'),
                        multiple=False
                    ),
                ], width=6),
                dbc.Col([
                    html.A(
                        dbc.Button(' Download Sample', color='secondary', outline=True, className='w-100'),
                        href='/assets/sample_turbine_locations.geojson',
                        download='sample_turbine_locations.geojson'
                    )
                ], width=6)
            ]),
            html.Div(id='upload-status', className='mt-3')
        ])
    ], className="mb-4"),
    
    # 지도 섹션
    dbc.Card([
        dbc.CardHeader("Map View"),
        dbc.CardBody([
            html.Div([
                dl.Map(
                    id='wind-farm-map',
                    center=[34.87, 126.17],  # 초기 중심 (한국 서해안)
                    zoom=11,
                    children=[
                        dl.TileLayer(),  # OpenStreetMap 타일
                    ],
                    style={'height': '500px', 'width': '100%'}
                )
            ], id='map-container')
        ])
    ]),
       
], fluid=True)


# ============================================================================
# 콜백: GeoJSON 업로드 처리
# ============================================================================
@callback(
    [Output('upload-status', 'children'),
     Output('turbine-data', 'data')],
    Input('upload-geojson', 'contents'),
    [State('upload-geojson', 'filename'),
     State('turbine-data', 'data')]
)
def upload_geojson(contents, filename, turbine_data):
    """GeoJSON 파일 업로드 및 검증"""
    if not contents:
        return "", turbine_data
    
    # GeoJSON 파싱
    geojson, error = parse_geojson(contents, filename)
    
    if error:
        return dbc.Alert(error, color="danger"), turbine_data
    
    # 성공
    num_turbines = len(geojson['features'])
    status = dbc.Alert(
        [
            html.Strong(f"✅ Loaded: {filename}"), html.Br(),
            f"Found {num_turbines} turbine(s)"
        ],
        color="success"
    )
    
    # 전역 Store에 저장
    turbine_data['locations'] = geojson
    return status, turbine_data

# ============================================================================
# 콜백: 지도 업데이트
# ============================================================================
@callback(
    Output('wind-farm-map', 'children'),
    Output('wind-farm-map', 'center'),
    Output('wind-farm-map', 'zoom'),
    Input('turbine-data', 'data'),
    # TODO: Analytics에서 주파수 데이터 연동
    # Input('turbine-data', 'data')  # app.py의 전역 Store
)
def update_map(turbine_data):
    """지도에 경계 Polygon + 터빈 CircleMarker 표시"""
    # 전역 Store에서 GeoJSON 데이터 가져오기
    geojson = turbine_data.get('locations') if turbine_data else None
    
    if not geojson:
        # 초기 상태 (데이터 없음)
        return [dl.TileLayer()], [34.87, 126.17], 11
    
    # TODO: 전역 Store에서 주파수 데이터 가져오기
    # frequencies = turbine_data.get('frequencies', {}) if turbine_data else {}
    frequencies = None  # 현재는 None (Analytics 미구현)
    
    # Polygon + CircleMarker 생성
    turbine_layers = create_turbine_layers(geojson, frequencies)
    
    # 지도 중심 계산
    center = calculate_center(geojson)
    
    # 지도 레이어 구성
    map_children = [
        dl.TileLayer(),
        *turbine_layers  # Polygon + CircleMarker들 추가
    ]
    
    return map_children, center, 12  # zoom=12로 확대


# ============================================================================
# TODO: 전역 Store 연동 (app.py 수정 후)
# ============================================================================
# @callback(
#     Output('wind-farm-map', 'children'),
#     [Input('map-geojson-store', 'data'),
#      Input('turbine-data', 'data')]  # app.py의 전역 Store
# )
# def update_map_with_frequencies(geojson, turbine_data):
#     """Analytics 데이터 포함하여 지도 업데이트"""
#     if not geojson:
#         return [dl.TileLayer()]
#     
#     frequencies = turbine_data.get('frequencies', {}) if turbine_data else {}
#     turbine_layers = create_turbine_layers(geojson, frequencies)
#     
#     return [dl.TileLayer(), *turbine_layers]