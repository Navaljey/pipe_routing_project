"""
PBS (Priority-Based Search) 알고리즘
논문의 Algorithm 1 구현입니다.
"""

import time
from ...core.plan import Plan
from ...core.ct_node import CTNode
from ...core.constraint import Constraint
from ...evaluation.conflict_manager import ConflictManager
from ...evaluation.quality_evaluator import QualityEvaluator

class PBS:
    """
    Priority-Based Search 알고리즘
    Conflict Tree를 탐색하여 최적의 우선순위 조합을 찾습니다
    """
    
    def __init__(self, environment, solver, max_missing=0, conflict_policy=2):
        """
        PBS 초기화
        
        Args:
            environment (Environment): 3D 환경
            solver (BaseSolver): 개별 파이프 솔버
            max_missing (int): 허용되는 최대 missing 파이프 수
            conflict_policy (int): 충돌 선택 정책 (1=균등, 2=비용기반)
        """
        self.environment = environment
        self.solver = solver
        self.max_missing = max_missing
        self.conflict_policy = conflict_policy
        
        self.conflict_manager = ConflictManager(environment)
        self.evaluator = QualityEvaluator()
        
        # 통계
        self.nodes_expanded = 0
        self.max_depth = 0
    
    def solve(self, pipes, timeout=3600):
        """
        PBS로 파이프 배치 문제 해결
        
        Args:
            pipes (list): Pipe 객체들
            timeout (int): 시간 제한 (초)
            
        Returns:
            Plan: 최선의 계획
        """
        start_time = time.time()
        
        print("PBS 시작...")
        print(f"  파이프 수: {len(pipes)}")
        print(f"  최대 missing: {self.max_missing}")
        print(f"  시간 제한: {timeout}초")
        
        # 1. 독립 라우팅으로 루트 노드 생성
        print("\n독립 라우팅 수행 중...")
        root_plan = self._independent_routing(pipes)
        root_node = CTNode(root_plan)
        
        print(f"독립 라우팅 완료: {root_plan.num_routed()}/{len(pipes)} 파이프")
        
        # 2. DFS 스택 초기화
        stack = [root_node]
        best_plan = None
        
        # 3. Conflict Tree 탐색
        while stack and (time.time() - start_time < timeout):
            # 현재 노드
            node = stack.pop()
            self.nodes_expanded += 1
            self.max_depth = max(self.max_depth, node.depth)
            
            # 진행 상황 출력
            if self.nodes_expanded % 10 == 0:
                elapsed = time.time() - start_time
                print(f"  노드 {self.nodes_expanded}, 깊이 {node.depth}, "
                      f"시간 {elapsed:.1f}s, 스택 {len(stack)}")
            
            # 현재 노드가 최선보다 나쁘면 가지치기
            if best_plan and not node.plan.is_better_than(best_plan):
                continue
            
            # 6. 충돌이 없으면 최선 갱신
            if not self.conflict_manager.has_conflicts(node.plan):
                if node.is_feasible(self.max_missing):
                    best_plan = node.plan
                    quality = best_plan.get_quality()
                    print(f"\n*** 새로운 최선 발견! ***")
                    print(f"    Missing: {quality[0]}, 비용: {quality[1]:.1f}")
                    print(f"    노드: {self.nodes_expanded}, 깊이: {node.depth}\n")
                continue
            
            # 10. 충돌이 있으면 분기
            children = self._branch(node)
            
            # 11. 자식 노드들을 품질 순으로 스택에 추가
            children.sort(key=lambda n: n.get_quality(), reverse=True)
            stack.extend(children)
        
        # 결과 출력
        elapsed_time = time.time() - start_time
        print(f"\nPBS 완료!")
        print(f"  탐색 시간: {elapsed_time:.1f}초")
        print(f"  탐색 노드: {self.nodes_expanded}개")
        print(f"  최대 깊이: {self.max_depth}")
        
        if best_plan:
            quality = best_plan.get_quality()
            print(f"  최종 결과: {best_plan.num_routed()}/{len(pipes)} 파이프")
            print(f"  Missing: {quality[0]}, 비용: {quality[1]:.1f}")
        else:
            print("  해를 찾지 못했습니다.")
            best_plan = root_plan  # 최소한 독립 라우팅 반환
        
        return best_plan
    
    def _independent_routing(self, pipes):
        """
        독립 라우팅: 각 파이프를 다른 파이프 무시하고 개별적으로 배치
        
        Args:
            pipes (list): Pipe 리스트
            
        Returns:
            Plan: 독립 라우팅 계획
        """
        for pipe in pipes:
            path = self.solver.solve(pipe, obstacles_pipes=[])
            if path:
                pipe.set_path(path)
        
        return Plan(pipes)
    
    def _branch(self, node):
        """
        충돌을 해결하기 위해 노드를 분기
        논문의 Branch 함수 (Algorithm 1, line 12-23)
        
        Args:
            node (CTNode): 현재 노드
            
        Returns:
            list: 자식 노드들
        """
        # 13. 충돌 선택
        conflict = self.conflict_manager.select_conflict(
            node.plan, 
            policy=self.conflict_policy
        )
        
        if conflict is None:
            return []
        
        pipe1_id, pipe2_id = conflict.get_pipes()
        children = []
        
        # 15. 두 가지 우선순위 시도
        for higher, lower in [(pipe1_id, pipe2_id), (pipe2_id, pipe1_id)]:
            # 16. 제약이 일관성 있는지 확인
            new_constraint = Constraint(higher, lower)
            test_constraints = node.constraints.copy()
            test_constraints.add(new_constraint)
            
            if not test_constraints.is_consistent():
                continue  # 순환이 생기면 스킵
            
            # 17-19. 자식 노드 생성
            child_plan = node.plan.copy()
            
            # 20. 낮은 우선순위 파이프 재배치
            lower_pipe = child_plan.get_pipe(lower)
            
            # 높은 우선순위 파이프들을 장애물로
            higher_priority_pipes = self._get_higher_priority_pipes(
                child_plan, 
                lower, 
                test_constraints
            )
            
            new_path = self.solver.solve(lower_pipe, higher_priority_pipes)
            
            # 21. 경로를 찾았거나 maxMissing 이내면 자식 추가
            if new_path is not None:
                lower_pipe.set_path(new_path)
                child = node.create_child(child_plan, new_constraint)
                children.append(child)
            elif child_plan.num_missing() <= self.max_missing:
                lower_pipe.set_path(None)  # 명시적으로 None 설정
                child = node.create_child(child_plan, new_constraint)
                children.append(child)
        
        return children
    
    def _get_higher_priority_pipes(self, plan, pipe_id, constraints):
        """
        특정 파이프보다 우선순위가 높은 파이프들을 반환
        
        Args:
            plan (Plan): 계획
            pipe_id (int): 기준 파이프 ID
            constraints (ConstraintSet): 제약 집합
            
        Returns:
            list: 높은 우선순위 파이프들
        """
        higher_pipes = []
        
        for constraint in constraints.constraints:
            if constraint.lower == pipe_id:
                # 이 파이프보다 우선순위가 높은 파이프
                higher_pipe = plan.get_pipe(constraint.higher)
                if higher_pipe.has_path():
                    higher_pipes.append(higher_pipe)
        
        return higher_pipes
