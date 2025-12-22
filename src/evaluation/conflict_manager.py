"""
ConflictManager 클래스
파이프 간의 충돌을 감지하고 관리합니다.
"""

import random
from ..core.conflict import Conflict

class ConflictManager:
    """
    충돌 감지 및 선택 정책을 관리하는 클래스
    """
    
    def __init__(self, environment):
        """
        충돌 관리자 초기화
        
        Args:
            environment (Environment): 3D 환경
        """
        self.environment = environment
    
    def find_all_conflicts(self, plan):
        """
        계획에서 모든 충돌을 찾습니다
        
        Args:
            plan (Plan): 확인할 계획
            
        Returns:
            list: Conflict 객체들의 리스트
        """
        conflicts = []
        routed_pipes = plan.get_routed_pipes()
        
        # 모든 파이프 쌍을 확인
        for i in range(len(routed_pipes)):
            for j in range(i + 1, len(routed_pipes)):
                pipe1 = routed_pipes[i]
                pipe2 = routed_pipes[j]
                
                # 두 파이프가 충돌하는지 확인
                if self._check_collision(pipe1, pipe2):
                    conflict = Conflict(pipe1.id, pipe2.id)
                    conflicts.append(conflict)
        
        return conflicts
    
    def _check_collision(self, pipe1, pipe2):
        """
        두 파이프가 충돌하는지 확인
        
        Args:
            pipe1 (Pipe): 첫 번째 파이프
            pipe2 (Pipe): 두 번째 파이프
            
        Returns:
            bool: 충돌하면 True
        """
        if pipe1.path is None or pipe2.path is None:
            return False
        
        # 두 파이프가 차지하는 셀들
        cells1 = pipe1.get_occupied_cells()
        cells2 = pipe2.get_occupied_cells()
        
        # 교집합이 있으면 충돌
        intersection = cells1 & cells2
        return len(intersection) > 0
    
    def has_conflicts(self, plan):
        """
        계획에 충돌이 있는지 확인
        
        Args:
            plan (Plan): 확인할 계획
            
        Returns:
            bool: 충돌이 있으면 True
        """
        return len(self.find_all_conflicts(plan)) > 0
    
    def select_conflict(self, plan, policy=1):
        """
        충돌을 선택하는 함수 (여러 충돌 중 하나를 선택)
        
        Args:
            plan (Plan): 계획
            policy (int): 선택 정책
                1 = 균등 랜덤
                2 = 비용 기반 가중치
                
        Returns:
            Conflict or None: 선택된 충돌 (없으면 None)
        """
        conflicts = self.find_all_conflicts(plan)
        
        if len(conflicts) == 0:
            return None
        
        if policy == 1:
            # 정책 1: 균등 랜덤 선택
            return random.choice(conflicts)
        
        elif policy == 2:
            # 정책 2: 비용에 비례한 가중치로 선택
            return self._select_conflict_by_cost(conflicts, plan)
        
        else:
            raise ValueError(f"알 수 없는 충돌 선택 정책: {policy}")
    
    def _select_conflict_by_cost(self, conflicts, plan):
        """
        파이프 비용에 비례한 확률로 충돌 선택
        비용이 큰 파이프가 관련된 충돌을 우선 선택
        
        Args:
            conflicts (list): 충돌 리스트
            plan (Plan): 계획
            
        Returns:
            Conflict: 선택된 충돌
        """
        # 각 충돌의 가중치 계산 (두 파이프 비용의 합)
        weights = []
        for conflict in conflicts:
            pipe1 = plan.get_pipe(conflict.pipe1)
            pipe2 = plan.get_pipe(conflict.pipe2)
            
            cost1 = pipe1.cost if pipe1.cost is not None else 0
            cost2 = pipe2.cost if pipe2.cost is not None else 0
            
            weight = cost1 + cost2
            weights.append(weight)
        
        # 가중치에 따라 랜덤 선택
        total_weight = sum(weights)
        if total_weight == 0:
            # 모든 비용이 0이면 균등 선택
            return random.choice(conflicts)
        
        # 가중치 정규화
        probabilities = [w / total_weight for w in weights]
        
        # 확률에 따라 선택
        return random.choices(conflicts, weights=probabilities)[0]
    
    def find_conflicted_pipes(self, plan, pipe_id):
        """
        특정 파이프와 충돌하는 모든 파이프 찾기
        
        Args:
            plan (Plan): 계획
            pipe_id (int): 확인할 파이프 ID
            
        Returns:
            list: 충돌하는 파이프 ID들
        """
        all_conflicts = self.find_all_conflicts(plan)
        conflicted = []
        
        for conflict in all_conflicts:
            if conflict.involves(pipe_id):
                other = conflict.get_other_pipe(pipe_id)
                if other is not None:
                    conflicted.append(other)
        
        return conflicted
    
    def get_conflict_statistics(self, plan):
        """
        충돌 통계 반환
        
        Args:
            plan (Plan): 계획
            
        Returns:
            dict: 통계 정보
        """
        conflicts = self.find_all_conflicts(plan)
        
        # 각 파이프가 몇 개의 충돌에 연루되었는지
        pipe_conflict_count = {}
        for conflict in conflicts:
            for pipe_id in conflict.get_pipes():
                pipe_conflict_count[pipe_id] = pipe_conflict_count.get(pipe_id, 0) + 1
        
        return {
            'total_conflicts': len(conflicts),
            'pipes_with_conflicts': len(pipe_conflict_count),
            'max_conflicts_per_pipe': max(pipe_conflict_count.values()) if pipe_conflict_count else 0,
            'pipe_conflict_count': pipe_conflict_count
        }
