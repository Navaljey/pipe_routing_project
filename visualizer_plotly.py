import json
import numpy as np
import plotly.graph_objects as go
import os

def load_json_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def calculate_path_metrics(path):
    if len(path) < 2: return 0, 0
    dist = sum(np.linalg.norm(np.array(path[i]) - np.array(path[i-1])) for i in range(1, len(path)))
    bends = 0
    for i in range(1, len(path)-1):
        v1 = (np.array(path[i]) - np.array(path[i-1]))
        v2 = (np.array(path[i+1]) - np.array(path[i]))
        if not np.allclose(v1/np.linalg.norm(v1), v2/np.linalg.norm(v2), atol=1e-3):
            bends += 1
    return round(dist, 2), bends

def get_smooth_bend_path(path, radius, segments=20):
    if len(path) < 3: return np.array(path)
    path = np.array(path); smooth_path = [path[0]]
    for i in range(1, len(path)-1):
        p1, p2, p3 = path[i-1], path[i], path[i+1]
        v1, v2 = p1-p2, p3-p2
        d1, d2 = np.linalg.norm(v1), np.linalg.norm(v2)
        actual_r = min(radius, d1*0.4, d2*0.4)
        if actual_r < 0.01:
            smooth_path.append(p2)
            continue
        s_pt, e_pt = p2+(v1/d1)*actual_r, p2+(v2/d2)*actual_r
        smooth_path.append(s_pt)
        for t in np.linspace(0, 1, segments):
            smooth_path.append((1-t)**2*s_pt + 2*(1-t)*t*p2 + t**2*e_pt)
        smooth_path.append(e_pt)
    smooth_path.append(path[-1])
    return np.array(smooth_path)

def visualizer_plotly():
    best_plan = load_json_data("routing_result.json")
    
    # 환경 데이터 (사용자 설정에 맞춰 수정)
    obstacles = [{'min_corner': [4,4,0], 'max_corner': [6,6,4]}, {'min_corner': [1,2,1], 'max_corner': [3,4,2]}]
    pipe_info = [
        {"id": 0, "diameter": 1.0, "start": [2.5, 2, 3], "goal": [6.5, 6, 3]},
        {"id": 1, "diameter": 1.0, "start": [7.5, 2, 3], "goal": [2.5, 7, 3]},
        {"id": 2, "diameter": 0.5, "start": [3, 3, 0], "goal": [7, 7, 0]},
        {"id": 3, "diameter": 0.5, "start": [3, 7, 0], "goal": [7, 3, 0]},
        {"id": 4, "diameter": 0.75, "start": [1, 1, 1], "goal": [9, 9, 1]},
        {"id": 5, "diameter": 0.75, "start": [1, 9, 1], "goal": [9, 1, 1]},
        {"id": 6, "diameter": 0.6, "start": [2, 5, 2], "goal": [8, 5, 2]},
        {"id": 7, "diameter": 0.6, "start": [5, 2, 2], "goal": [5, 8, 2]},
    ]

    fig = go.Figure()

    # 1. 장애물 표현 (박스 형태)
    for i, obs in enumerate(obstacles):
        min_c, max_c = np.array(obs['min_corner']), np.array(obs['max_corner'])
        # Plotly의 Mesh3d를 이용한 큐브 생성
        fig.add_trace(go.Mesh3d(
            x=[min_c[0], min_c[0], max_c[0], max_c[0], min_c[0], min_c[0], max_c[0], max_c[0]],
            y=[min_c[1], max_c[1], max_c[1], min_c[1], min_c[1], max_c[1], max_c[1], min_c[1]],
            z=[min_c[2], min_c[2], min_c[2], min_c[2], max_c[2], max_c[2], max_c[2], max_c[2]],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            opacity=0.15, color='gray', name=f'Obstacle {i}', hoverinfo='skip'
        ))

    # 2. 파이프 및 마커 표현
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    for i, p in enumerate(pipe_info):
        p_id = str(p["id"])
        path_data = best_plan.get(p_id) or best_plan.get(int(p_id))
        color = colors[i % len(colors)]
        s, g = p["start"], p["goal"]

        # 시작/종료 지점 마커
        fig.add_trace(go.Scatter3d(x=[s[0]], y=[s[1]], z=[s[2]], mode='markers+text', 
                                   marker=dict(size=6, color='green'), text=[f"S{p_id}"], name=f"Start P{p_id}"))
        fig.add_trace(go.Scatter3d(x=[g[0]], y=[g[1]], z=[g[2]], mode='markers+text', 
                                   marker=dict(size=6, color='red'), text=[f"G{p_id}"], name=f"Goal P{p_id}"))

        if path_data:
            path = np.array(path_data)
            length, bends = calculate_path_metrics(path)
            smooth_pts = get_smooth_bend_path(path, p["diameter"]*3.0)

            # 파이프 본체 (두께감 표현을 위해 line width 조절)
            fig.add_trace(go.Scatter3d(
                x=smooth_pts[:, 0], y=smooth_pts[:, 1], z=smooth_pts[:, 2],
                mode='lines',
                line=dict(color=color, width=p["diameter"]*15),
                name=f"Pipe {p_id}",
                hovertext=f"ID: {p_id}<br>Diameter: {p['diameter']}<br>Length: {length}<br>Bends: {bends}",
                hoverinfo="text"
            ))

    # 레이아웃 설정
    fig.update_layout(
        title="Interactive 3D Pipe Routing (Plotly)",
        scene=dict(
            xaxis_title='X Axis', yaxis_title='Y Axis', zaxis_title='Z Axis',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    # 결과물 HTML 파일로 저장 (웹브라우저로 언제든 열기 가능)
    save_path = "interactive_inspection.html"
    fig.write_html(save_path)
    print(f"저장 완료: '{save_path}' 파일을 웹 브라우저로 열어 확인하세요.")
    
    # 즉시 실행
    fig.show()

if __name__ == "__main__":
    visualizer_plotly()