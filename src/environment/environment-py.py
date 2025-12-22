"""
Environment 클래스
3D 공간을 관리하고 충돌 체크를 수행합니다.
"""

import numpy as np
from .obstacle import Obstacle

class Environment:
    """
    3D 파이프 배치 환경
    격자 기반으로 공간을 표현하고 장애물을 관리합니다
    """
    
    def __init__(self, bounds, grid_resolution=1.0):
        """
        환경 초기화
        
        Args:
            bounds (tuple): 공간 크기 (x_size, y_size, z_size) 미터 단위
            grid_resolution (float): 격자 해상도 (미터), 작을수록 정밀
        """
        self.bounds = bounds  # (width, depth, height) in meters
        self.resolution = grid_resolution
        
        # 격자 크기 계산
        self.grid_size = (
            int(bounds[0] / grid_resolution),
            int(bounds[1] / grid_resolution),
            int(bounds[2] / grid_resolution)
        )
        
        # 3D 격자: 0=비어있음, 1=장애물, 2=파이프
        self.grid = np.zeros(self.grid_size, dtype=np.int8)
        
        # 장애물 리스트
        self.obstacles = []
        
        # 점유 정보 (어떤 파이프가 어느 셀을 차지하는지)
        self.occupation_map = {}  # {(x,y,z): pipe_id}
    
    def add_obstacle(self, obstacle):
        """
        환경에 장애물 추가
        
        Args:
            obstacle (Obstacle): 추가할 장애물
        """
        self.obstacles.append(obstacle)
        
        # 격자에 장애물 표시
        occupied_cells = obstacle.get_occupied_cells(self.resolution)
        for cell in occupied_cells:
            if self._is_valid_cell(cell):
                self.grid[cell] = 1  # 1 = 장애물
    
    def is_free(self, point):
        """
        특정 점이 비어있는지 확인 (장애물이나 다른 파이프가 없음)
        
        Args:
            point (tuple): 확인할 점 (x, y, z)
            
        Returns:
            bool: 비어있으면 True
        """
        cell = self._point_to_cell(point)
        
        if not self._is_valid_cell(cell):
            return False
        
        return self.grid[cell] == 0
    
    def is_occupied_by_pipe(self, point):
        """
        특정 점이 파이프에 의해 점유되어 있는지 확인
        
        Args:
            point (tuple): 확인할 점
            
        Returns:
            bool: 파이프가 있으면 True
        """
        cell = self._point_to_cell(point)
        return cell in self.occupation_map
    
    def get_occupying_pipe(self, point):
        """
        특정 점을 차지하고 있는 파이프 ID 반환
        
        Args:
            point (tuple): 확인할 점
            
        Returns:
            int or None: 파이프 ID, 없으면 None
        """
        cell = self._point_to_cell(point)
        return self.occupation_map.get(cell, None)
    
    def mark_pipe_path(self, pipe):
        """
        파이프의 경로를 환경에 표시
        
        Args:
            pipe (Pipe): 표시할 파이프
        """
        if pipe.path is None:
            return
        
        occupied_cells = pipe.get_occupied_cells()
        for point in occupied_cells:
            cell = self._point_to_cell(point)
            if self._is_valid_cell(cell):
                self.grid[cell] = 2  # 2 = 파이프
                self.occupation_map[cell] = pipe.id
    
    def unmark_pipe_path(self, pipe):
        """
        파이프의 경로 표시를 제거
        
        Args:
            pipe (Pipe): 제거할 파이프
        """
        if pipe.path is None:
            return
        
        occupied_cells = pipe.get_occupied_cells()
        for point in occupied_cells:
            cell = self._point_to_cell(point)
            if cell in self.occupation_map and self.occupation_map[cell] == pipe.id:
                self.grid[cell] = 0  # 다시 비움
                del self.occupation_map[cell]
    
    def check_path_collision(self, path, ignore_pipes=None):
        """
        경로가 장애물이나 다른 파이프와 충돌하는지 확인
        
        Args:
            path (list): 확인할 경로 [(x1,y1,z1), ...]
            ignore_pipes (set): 무시할 파이프 ID들
            
        Returns:
            tuple: (충돌 여부, 충돌한 파이프 ID 또는 None)
        """
        if ignore_pipes is None:
            ignore_pipes = set()
        
        for point in path:
            cell = self._point_to_cell(point)
            
            # 범위 밖
            if not self._is_valid_cell(cell):
                return (True, None)
            
            # 장애물과 충돌
            if self.grid[cell] == 1:
                return (True, None)
            
            # 다른 파이프와 충돌
            if cell in self.occupation_map:
                occupying_pipe = self.occupation_map[cell]
                if occupying_pipe not in ignore_pipes:
                    return (True, occupying_pipe)
        
        return (False, None)
    
    def _point_to_cell(self, point):
        """
        실제 좌표를 격자 인덱스로 변환
        
        Args:
            point (tuple): 실제 좌표 (미터)
            
        Returns:
            tuple: 격자 인덱스 (i, j, k)
        """
        return (
            int(point[0] / self.resolution),
            int(point[1] / self.resolution),
            int(point[2] / self.resolution)
        )
    
    def _cell_to_point(self, cell):
        """
        격자 인덱스를 실제 좌표로 변환
        
        Args:
            cell (tuple): 격자 인덱스
            
        Returns:
            tuple: 실제 좌표 (미터)
        """
        return (
            cell[0] * self.resolution,
            cell[1] * self.resolution,
            cell[2] * self.resolution
        )
    
    def _is_valid_cell(self, cell):
        """
        격자 인덱스가 유효한 범위 내에 있는지 확인
        
        Args:
            cell (tuple): 격자 인덱스
            
        Returns:
            bool: 유효하면 True
        """
        return (0 <= cell[0] < self.grid_size[0] and
                0 <= cell[1] < self.grid_size[1] and
                0 <= cell[2] < self.grid_size[2])
    
    def get_neighbors(self, point):
        """
        특정 점의 이웃 셀들을 반환 (6방향: ±x, ±y, ±z)
        
        Args:
            point (tuple): 중심 점
            
        Returns:
            list: 이웃 점들의 리스트
        """
        cell = self._point_to_cell(point)
        neighbors = []
        
        # 6방향 (상하좌우전후)
        directions = [
            (1, 0, 0), (-1, 0, 0),  # x 방향
            (0, 1, 0), (0, -1, 0),  # y 방향
            (0, 0, 1), (0, 0, -1)   # z 방향
        ]
        
        for dx, dy, dz in directions:
            neighbor_cell = (cell[0] + dx, cell[1] + dy, cell[2] + dz)
            if self._is_valid_cell(neighbor_cell):
                neighbors.append(self._cell_to_point(neighbor_cell))
        
        return neighbors
    
    def get_statistics(self):
        """
        환경 통계 정보 반환
        
        Returns:
            dict: 통계 정보
        """
        total_cells = self.grid.size
        obstacle_cells = np.sum(self.grid == 1)
        pipe_cells = np.sum(self.grid == 2)
        free_cells = np.sum(self.grid == 0)
        
        return {
            'total_cells': total_cells,
            'obstacle_cells': obstacle_cells,
            'pipe_cells': pipe_cells,
            'free_cells': free_cells,
            'obstacle_ratio': obstacle_cells / total_cells * 100,
            'pipe_ratio': pipe_cells / total_cells * 100,
            'free_ratio': free_cells / total_cells * 100
        }
    
    def __repr__(self):
        """디버깅용 표현"""
        return f"Environment({self.bounds}, grid={self.grid_size})"
    
    def __str__(self):
        """사용자 친화적 표현"""
        stats = self.get_statistics()
        return (f"환경: {self.bounds[0]}m × {self.bounds[1]}m × {self.bounds[2]}m\n"
                f"격자: {self.grid_size}\n"
                f"장애물: {len(self.obstacles)}개 ({stats['obstacle_ratio']:.1f}%)\n"
                f"파이프: {stats['pipe_cells']}개 셀 ({stats['pipe_ratio']:.1f}%)")
