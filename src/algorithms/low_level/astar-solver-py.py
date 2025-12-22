"""
A* 알고리즘 기반 파이프 경로 탐색
간단하고 빠른 경로 탐색을 위한 솔버입니다.
"""

import heapq
import time
from .base_solver import BaseSolver

class AStarSolver(BaseSolver):
    """
    A* 알고리즘으로 파이프 경로를 찾는 솔버
    MiniZinc보다 빠르지만 덜 최적화된 경로를 찾을 수 있습니다
    """
    
    def __init__(self, environment):
        """
        A* 솔버 초기화
        
        Args:
            environment (Environment): 3D 환경
        """
        super().__init__(environment)
        
        # 구부림 페널티
        self.bend_penalty = 50
    
    def solve(self, pipe, obstacles_pipes=None):
        """
        A* 알고리즘으로 파이프 경로 찾기
        
        Args:
            pipe (Pipe): 경로를 찾을 파이프
            obstacles_pipes (list): 장애물로 간주할 파이프들
            
        Returns:
            list or None: 경로 또는 None
        """
        start_time = time.time()
        
        # 장애물 파이프들을 환경에 임시로 표시
        if obstacles_pipes:
            for obs_pipe in obstacles_pipes:
                if obs_pipe.has_path():
                    self.environment.mark_pipe_path(obs_pipe)
        
        try:
            # A* 탐색 실행
            path = self._a_star_search(
                pipe.start, 
                pipe.goal, 
                pipe.diameter,
                start_time
            )
            
            return path
        
        finally:
            # 임시 표시 제거
            if obstacles_pipes:
                for obs_pipe in obstacles_pipes:
                    if obs_pipe.has_path():
                        self.environment.unmark_pipe_path(obs_pipe)
    
    def _a_star_search(self, start, goal, diameter, start_time):
        """
        A* 탐색 알고리즘 구현
        
        Args:
            start (tuple): 시작 위치
            goal (tuple): 목표 위치
            diameter (float): 파이프 지름
            start_time (float): 시작 시간
            
        Returns:
            list or None: 경로 또는 None
        """
        # 우선순위 큐: (f_score, g_score, position, path, last_direction)
        # f_score = g_score + h_score (총 예상 비용)
        # g_score = 현재까지의 실제 비용
        # h_score = 휴리스틱 (목표까지의 추정 비용)
        
        start_h = self._heuristic(start, goal)
        heap = [(start_h, 0, start, [start], None)]
        
        # 방문한 위치들: {position: best_g_score}
        visited = {start: 0}
        
        while heap:
            # 시간 제한 체크
            if time.time() - start_time > self.timeout:
                return None
            
            f_score, g_score, current, path, last_dir = heapq.heappop(heap)
            
            # 목표 도달
            if current == goal:
                return path
            
            # 이미 더 좋은 경로로 방문했으면 스킵
            if current in visited and visited[current] < g_score:
                continue
            
            # 이웃 탐색
            for neighbor in self.environment.get_neighbors(current):
                # 비어있는지 확인
                if not self.environment.is_free(neighbor):
                    continue
                
                # 방향 계산
                current_dir = self._get_direction(current, neighbor)
                
                # 이동 비용 계산
                move_cost = self._calculate_distance(current, neighbor) * diameter
                
                # 구부림 페널티 추가
                if last_dir is not None and current_dir != last_dir:
                    move_cost += self.bend_penalty
                
                new_g = g_score + move_cost
                
                # 더 나은 경로를 찾았으면 업데이트
                if neighbor not in visited or new_g < visited[neighbor]:
                    visited[neighbor] = new_g
                    new_h = self._heuristic(neighbor, goal)
                    new_f = new_g + new_h
                    new_path = path + [neighbor]
                    
                    heapq.heappush(heap, (new_f, new_g, neighbor, new_path, current_dir))
        
        # 경로를 찾지 못함
        return None
    
    def _heuristic(self, pos1, pos2):
        """
        휴리스틱 함수: 맨하탄 거리
        
        Args:
            pos1 (tuple): 위치 1
            pos2 (tuple): 위치 2
            
        Returns:
            float: 추정 거리
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) + abs(pos1[2] - pos2[2])
    
    def _calculate_distance(self, pos1, pos2):
        """
        두 위치 사이의 유클리드 거리
        
        Args:
            pos1 (tuple): 위치 1
            pos2 (tuple): 위치 2
            
        Returns:
            float: 거리
        """
        return ((pos1[0] - pos2[0])**2 + 
                (pos1[1] - pos2[1])**2 + 
                (pos1[2] - pos2[2])**2)**0.5
    
    def _get_direction(self, pos1, pos2):
        """
        두 위치 사이의 방향 반환
        
        Args:
            pos1 (tuple): 시작 위치
            pos2 (tuple): 끝 위치
            
        Returns:
            str: 'x', 'y', 'z' 중 하나
        """
        if pos1[0] != pos2[0]:
            return 'x'
        elif pos1[1] != pos2[1]:
            return 'y'
        elif pos1[2] != pos2[2]:
            return 'z'
        return None
