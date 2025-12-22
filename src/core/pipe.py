"""
Pipe 클래스
파이프 하나의 정보를 담는 기본 데이터 구조입니다.
"""

class Pipe:
    """
    3D 공간에서 하나의 파이프를 나타내는 클래스
    
    파이프는 시작 nozzle에서 목표 nozzle까지 연결됩니다.
    """
    
    def __init__(self, pipe_id, start, goal, diameter):
        """
        파이프 초기화
        
        Args:
            pipe_id (int): 파이프 고유 번호 (0부터 시작)
            start (tuple): 시작 위치 (x, y, z)
            goal (tuple): 목표 위치 (x, y, z)
            diameter (float): 파이프 지름 (미터 단위)
        """
        self.id = pipe_id
        self.start = start  # (x, y, z) 튜플
        self.goal = goal    # (x, y, z) 튜플
        self.diameter = diameter
        
        # 현재 계산된 경로 (아직 없으면 None)
        self.path = None  # 경로는 [(x1,y1,z1), (x2,y2,z2), ...] 형태의 리스트
        
        # 경로의 비용 정보
        self.cost = None  # 총 비용 (None이면 아직 계산 안 됨)
        self.length = None  # 파이프 총 길이
        self.num_bends = None  # 구부림 개수
        
    def set_path(self, path):
        """
        파이프의 경로를 설정하고 비용을 계산합니다
        
        Args:
            path (list): 경로 좌표 리스트 [(x1,y1,z1), (x2,y2,z2), ...]
        """
        self.path = path
        if path is not None:
            self._calculate_cost()
        else:
            self.cost = None
            self.length = None
            self.num_bends = None
    
    def _calculate_cost(self):
        """
        설정된 경로의 비용을 계산합니다
        
        비용 = 길이 비용 + 구부림 비용 + 높이 페널티
        """
        if self.path is None or len(self.path) < 2:
            self.cost = float('inf')
            return
        
        # 1. 길이 계산
        self.length = 0
        for i in range(len(self.path) - 1):
            p1 = self.path[i]
            p2 = self.path[i + 1]
            # 유클리드 거리 (대부분 축 평행이므로 맨하탄 거리와 같음)
            dist = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)**0.5
            self.length += dist
        
        # 2. 구부림 개수 계산
        self.num_bends = self._count_bends()
        
        # 3. 높이 페널티 계산 (구부림이 지면/장비에서 멀 때)
        height_penalty = self._calculate_height_penalty()
        
        # 4. 총 비용 계산
        # 논문의 비용 함수: 길이 + 구부림 가중치 * 개수 + 높이 페널티
        BEND_WEIGHT = 100  # 구부림 하나당 비용
        self.cost = self.length * self.diameter + BEND_WEIGHT * self.num_bends + height_penalty
    
    def _count_bends(self):
        """
        경로에서 구부림(방향 전환)의 개수를 셉니다
        
        Returns:
            int: 구부림 개수
        """
        if len(self.path) < 3:
            return 0
        
        bends = 0
        for i in range(1, len(self.path) - 1):
            # 이전 방향과 다음 방향이 다르면 구부림
            prev_dir = self._get_direction(self.path[i-1], self.path[i])
            next_dir = self._get_direction(self.path[i], self.path[i+1])
            
            if prev_dir != next_dir:
                bends += 1
        
        return bends
    
    def _get_direction(self, p1, p2):
        """
        두 점 사이의 이동 방향을 반환합니다
        
        Returns:
            str: 'x', 'y', 'z' 중 하나 (또는 None)
        """
        if p1[0] != p2[0]:
            return 'x'
        elif p1[1] != p2[1]:
            return 'y'
        elif p1[2] != p2[2]:
            return 'z'
        return None
    
    def _calculate_height_penalty(self):
        """
        높이에 따른 페널티를 계산합니다
        구부림이 지면이나 장비에서 멀면 지지대 비용이 증가합니다
        
        Returns:
            float: 높이 페널티
        """
        # 간단한 버전: 평균 높이에 비례
        if self.path is None:
            return 0
        
        avg_height = sum(p[2] for p in self.path) / len(self.path)
        HEIGHT_PENALTY_WEIGHT = 10
        return HEIGHT_PENALTY_WEIGHT * avg_height * self.num_bends
    
    def has_path(self):
        """
        파이프에 경로가 할당되어 있는지 확인
        
        Returns:
            bool: 경로가 있으면 True
        """
        return self.path is not None
    
    def get_occupied_cells(self):
        """
        이 파이프가 차지하는 모든 셀(격자점)을 반환합니다
        실제로는 파이프 지름을 고려하여 여러 셀을 차지합니다
        
        Returns:
            set: 점유된 셀들의 집합 {(x,y,z), ...}
        """
        if self.path is None:
            return set()
        
        occupied = set()
        
        # 간단한 버전: 경로 상의 모든 점만 포함
        # 실제로는 지름을 고려하여 주변 셀도 포함해야 함
        for point in self.path:
            occupied.add(point)
        
        return occupied
    
    def __repr__(self):
        """디버깅용 문자열 표현"""
        status = "routed" if self.has_path() else "unrouted"
        return f"Pipe{self.id}({self.start}->{self.goal}, d={self.diameter}m, {status})"
    
    def __str__(self):
        """사용자 친화적 문자열 표현"""
        if self.has_path():
            return f"파이프 {self.id}: 길이={self.length:.1f}m, 구부림={self.num_bends}개, 비용={self.cost:.1f}"
        else:
            return f"파이프 {self.id}: 아직 경로 없음"
