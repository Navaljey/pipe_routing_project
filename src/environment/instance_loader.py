"""
InstanceLoader 클래스
JSON 파일에서 문제 인스턴스를 로드합니다.
"""

import json
import os
from ..core.pipe import Pipe
from .environment import Environment
from .obstacle import Obstacle

class InstanceLoader:
    """
    JSON 파일로부터 파이프 라우팅 문제를 로드하는 클래스
    """
    
    def __init__(self, data_dir="data/instances"):
        """
        로더 초기화
        
        Args:
            data_dir (str): 인스턴스 파일들이 있는 디렉토리
        """
        self.data_dir = data_dir
    
    def load_instance(self, instance_name):
        """
        특정 인스턴스를 로드
        
        Args:
            instance_name (str): 인스턴스 이름 (예: "small", "medium_1")
            
        Returns:
            tuple: (environment, pipes 리스트)
        """
        # JSON 파일 경로
        file_path = os.path.join(self.data_dir, f"{instance_name}.json")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"인스턴스 파일을 찾을 수 없습니다: {file_path}")
        
        # JSON 로드
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 환경 생성
        bounds = tuple(data['bounding_box'])
        grid_resolution = data.get('grid_resolution', 1.0)
        environment = Environment(bounds, grid_resolution)
        
        # 장애물 추가
        for obs_data in data['obstacles']:
            obstacle = Obstacle(
                name=obs_data['name'],
                min_corner=tuple(obs_data['min_corner']),
                max_corner=tuple(obs_data['max_corner']),
                obstacle_type=obs_data.get('type', 'physical')
            )
            environment.add_obstacle(obstacle)
        
        # 파이프 생성
        pipes = []
        for i, pipe_data in enumerate(data['pipes']):
            pipe = Pipe(
                pipe_id=i,
                start=tuple(pipe_data['start']),
                goal=tuple(pipe_data['goal']),
                diameter=pipe_data['diameter']
            )
            pipes.append(pipe)
        
        return environment, pipes
    
    def get_available_instances(self):
        """
        사용 가능한 모든 인스턴스 이름 반환
        
        Returns:
            list: 인스턴스 이름들
        """
        if not os.path.exists(self.data_dir):
            return []
        
        instances = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                instance_name = filename[:-5]  # .json 제거
                instances.append(instance_name)
        
        return sorted(instances)
    
    def create_sample_instance(self, instance_name="small"):
        """
        테스트용 샘플 인스턴스 생성 및 저장
        
        Args:
            instance_name (str): 저장할 인스턴스 이름
        """
        # Small 인스턴스 예시 데이터
        if instance_name == "small":
            data = {
                "name": "Small",
                "description": "8개 파이프를 가진 작은 테스트 인스턴스",
                "bounding_box": [11, 10, 12],
                "grid_resolution": 0.5,
                "equipment_pieces": 4,
                "logical_obstacles": 7,
                "obstacles": [
                    {
                        "name": "Equipment-1",
                        "type": "physical",
                        "min_corner": [2, 2, 0],
                        "max_corner": [4, 4, 3]
                    },
                    {
                        "name": "Equipment-2",
                        "type": "physical",
                        "min_corner": [6, 2, 0],
                        "max_corner": [8, 4, 3]
                    },
                    {
                        "name": "Equipment-3",
                        "type": "physical",
                        "min_corner": [2, 6, 0],
                        "max_corner": [4, 8, 3]
                    },
                    {
                        "name": "Equipment-4",
                        "type": "physical",
                        "min_corner": [6, 6, 0],
                        "max_corner": [8, 8, 3]
                    },
                    {
                        "name": "Access-Zone-1",
                        "type": "logical",
                        "min_corner": [4.5, 0, 0],
                        "max_corner": [5.5, 10, 2]
                    }
                ],
                "pipes": [
                    {
                        "id": 0,
                        "start": [2.5, 2, 3],
                        "goal": [6.5, 6, 3],
                        "diameter": 1.0
                    },
                    {
                        "id": 1,
                        "start": [7.5, 2, 3],
                        "goal": [2.5, 7, 3],
                        "diameter": 1.0
                    },
                    {
                        "id": 2,
                        "start": [3, 3, 0],
                        "goal": [7, 7, 0],
                        "diameter": 0.5
                    },
                    {
                        "id": 3,
                        "start": [3, 7, 0],
                        "goal": [7, 3, 0],
                        "diameter": 0.5
                    },
                    {
                        "id": 4,
                        "start": [1, 1, 1],
                        "goal": [9, 9, 1],
                        "diameter": 0.75
                    },
                    {
                        "id": 5,
                        "start": [1, 9, 1],
                        "goal": [9, 1, 1],
                        "diameter": 0.75
                    },
                    {
                        "id": 6,
                        "start": [2, 5, 2],
                        "goal": [8, 5, 2],
                        "diameter": 0.6
                    },
                    {
                        "id": 7,
                        "start": [5, 2, 2],
                        "goal": [5, 8, 2],
                        "diameter": 0.6
                    }
                ]
            }
        else:
            raise ValueError(f"샘플 인스턴스 '{instance_name}'를 생성할 수 없습니다")
        
        # 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
        
        # JSON 파일로 저장
        file_path = os.path.join(self.data_dir, f"{instance_name}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"샘플 인스턴스 '{instance_name}' 생성 완료: {file_path}")
        
        return data


# 편의 함수들
def load_instance(instance_name, data_dir="data/instances"):
    """
    인스턴스를 로드하는 편의 함수
    
    Args:
        instance_name (str): 인스턴스 이름
        data_dir (str): 데이터 디렉토리
        
    Returns:
        tuple: (environment, pipes)
    """
    loader = InstanceLoader(data_dir)
    return loader.load_instance(instance_name)


def create_small_instance():
    """Small 인스턴스를 생성하고 로드"""
    loader = InstanceLoader()
    loader.create_sample_instance("small")
    return loader.load_instance("small")
