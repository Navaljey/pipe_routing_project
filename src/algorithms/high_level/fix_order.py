"""
FixOrder 알고리즘
고정된 우선순위로 파이프를 순차적으로 배치합니다.
논문의 기준(baseline) 알고리즘입니다.
"""

from ...core.plan import Plan

class FixOrder:
    """
    고정된 순서로 파이프를 배치하는 알고리즘
    비용 추정치 기준 내림차순으로 정렬하여 배치합니다
    """
    
    def __init__(self, environment, solver):
        """
        FixOrder 초기화
        
        Args:
            environment (Environment): 3D 환경
            solver (BaseSolver): 개별 파이프 경로 탐색 솔버
        """
        self.environment = environment
        self.solver = solver
    
    def solve(self, pipes):
        """
        고정된 순서로 모든 파이프 배치
        
        Args:
            pipes (list): Pipe 객체들의 리스트
            
        Returns:
            Plan: 완성된 계획
        """
        # 파이프들을 추정 비용 기준으로 정렬
        sorted_pipes = self._sort_pipes_by_cost(pipes)
        
        # 순차적으로 배치
        routed_pipes = []
        
        for pipe in sorted_pipes:
            print(f"파이프 {pipe.id} 배치 중...")
            
            # 이미 배치된 파이프들을 장애물로 간주
            path = self.solver.solve(pipe, routed_pipes)
            
            if path is not None:
                pipe.set_path(path)
                routed_pipes.append(pipe)
                print(f"  -> 성공: 길이 {pipe.length:.1f}m, 비용 {pipe.cost:.1f}")
            else:
                print(f"  -> 실패: 경로를 찾을 수 없음")
        
        # 최종 계획 생성
        plan = Plan(pipes)
        
        print(f"\nFixOrder 완료: {plan.num_routed()}/{plan.num_pipes} 파이프 배치됨")
        
        return plan
    
    def _sort_pipes_by_cost(self, pipes):
        """
        파이프를 추정 비용 기준으로 정렬
        큰 지름의 파이프, 긴 거리의 파이프를 먼저 배치
        
        Args:
            pipes (list): Pipe 리스트
            
        Returns:
            list: 정렬된 Pipe 리스트
        """
        def estimate_cost(pipe):
            # 맨하탄 거리로 추정
            distance = (abs(pipe.goal[0] - pipe.start[0]) +
                       abs(pipe.goal[1] - pipe.start[1]) +
                       abs(pipe.goal[2] - pipe.start[2]))
            
            # 거리 * 지름으로 추정 비용 계산
            return distance * pipe.diameter
        
        # 비용 내림차순으로 정렬 (큰 것부터)
        return sorted(pipes, key=estimate_cost, reverse=True)
