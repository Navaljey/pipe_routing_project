"""
Obstacle 클래스
3D 공간의 장애물(장비, 접근 금지 구역 등)을 나타냅니다.
"""

class Obstacle:
    """
    3D 공간의 장애물
    직육면체(cuboid) 형태로 근사합니다
    """
    
    def __init__(self, name, min_corner, max_corner, obstacle_type="physical"):
        """
        장애물 생성
        
        Args:
            name (str): 장애물 이름 (예: "Pump-1", "Tank-A")
            min_corner (tuple): 최소 좌표 (x_min, y_min, z_min)
            max_corner (tuple): 최대 좌표 (x_max, y_max, z_max)
            obstacle_type (str): 'physical' 또는 'logical'
        """
        self.name = name
        self.min_corner = min_corner
        self.max_corner = max_corner
        self.type = obstacle_type
        
        # 크기 계산
        self.width = max_corner[0] - min_corner[0]
        self.depth = max_corner[1] - min_corner[1]
        self.height = max_corner[2] - min_corner[2]
    
    def contains_point(self, point):
        """
        점이 이 장애물 내부에 있는지 확인
        
        Args:
            point (tuple): 확인할 점 (x, y, z)
            
        Returns:
            bool: 내부에 있으면 True
        """
        x, y, z = point
        
        return (self.min_corner[0] <= x <= self.max_corner[0] and
                self.min_corner[1] <= y <= self.max_corner[1] and
                self.min_corner[2] <= z <= self.max_corner[2])
    
    def intersects_segment(self, p1, p2):
        """
        선분이 이 장애물과 교차하는지 확인
        
        Args:
            p1 (tuple): 선분의 시작점
            p2 (tuple): 선분의 끝점
            
        Returns:
            bool: 교차하면 True
        """
        # 간단한 버전: 시작점이나 끝점이 내부에 있으면 교차
        if self.contains_point(p1) or self.contains_point(p2):
            return True
        
        # 더 정확한 버전은 선분-박스 교차 알고리즘 필요
        # 여기서는 간단히 구현
        return False
    
    def get_occupied_cells(self, grid_resolution=1.0):
        """
        이 장애물이 차지하는 모든 격자 셀을 반환
        
        Args:
            grid_resolution (float): 격자 해상도 (미터)
            
        Returns:
            set: 점유된 셀들 {(x, y, z), ...}
        """
        cells = set()
        
        # 최소/최대 좌표를 격자 인덱스로 변환
        x_min = int(self.min_corner[0] / grid_resolution)
        x_max = int(self.max_corner[0] / grid_resolution)
        y_min = int(self.min_corner[1] / grid_resolution)
        y_max = int(self.max_corner[1] / grid_resolution)
        z_min = int(self.min_corner[2] / grid_resolution)
        z_max = int(self.max_corner[2] / grid_resolution)
        
        # 모든 셀 추가
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                for z in range(z_min, z_max + 1):
                    cells.add((x, y, z))
        
        return cells
    
    def __repr__(self):
        """디버깅용 표현"""
        return f"Obstacle('{self.name}', {self.min_corner}, {self.max_corner})"
    
    def __str__(self):
        """사용자 친화적 표현"""
        return (f"{self.name} ({self.type}): "
                f"{self.width}m × {self.depth}m × {self.height}m")
