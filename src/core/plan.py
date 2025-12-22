"""
Plan 클래스
모든 파이프들의 경로 계획을 담는 클래스입니다.
"""

class Plan:
    """
    전체 파이프 배치 계획
    여러 파이프들의 경로를 모아서 관리합니다
    """
    
    def __init__(self, pipes):
        """
        계획 초기화
        
        Args:
            pipes (list): Pipe 객체들의 리스트
        """
        self.pipes = pipes  # 전체 파이프 리스트
        self.num_pipes = len(pipes)
        
    def get_pipe(self, pipe_id):
        """
        특정 ID의 파이프를 가져옵니다
        
        Args:
            pipe_id (int): 파이프 ID
            
        Returns:
            Pipe: 해당 파이프 객체
        """
        return self.pipes[pipe_id]
    
    def get_routed_pipes(self):
        """
        경로가 할당된 파이프들만 반환
        
        Returns:
            list: 경로가 있는 파이프들
        """
        return [p for p in self.pipes if p.has_path()]
    
    def get_missing_pipes(self):
        """
        경로가 없는 파이프들을 반환
        
        Returns:
            list: 경로가 없는 파이프들
        """
        return [p for p in self.pipes if not p.has_path()]
    
    def num_routed(self):
        """
        경로가 할당된 파이프 개수
        
        Returns:
            int: 배치된 파이프 수
        """
        return len(self.get_routed_pipes())
    
    def num_missing(self):
        """
        경로가 없는 파이프 개수
        
        Returns:
            int: 배치 안 된 파이프 수
        """
        return len(self.get_missing_pipes())
    
    def total_cost(self):
        """
        모든 배치된 파이프의 총 비용을 계산
        
        Returns:
            float: 총 비용 (missing pipe가 있으면 inf)
        """
        routed = self.get_routed_pipes()
        if len(routed) == 0:
            return float('inf')
        
        return sum(p.cost for p in routed)
    
    def get_quality(self):
        """
        논문의 Quality 함수 구현
        Quality(S) = (num_missing, total_cost)
        
        Returns:
            tuple: (missing 파이프 수, 총 비용)
        """
        return (self.num_missing(), self.total_cost())
    
    def is_better_than(self, other_plan):
        """
        이 계획이 다른 계획보다 나은지 비교
        사전식 순서: missing 개수가 적으면 무조건 좋음
        같으면 비용이 적은 쪽이 좋음
        
        Args:
            other_plan (Plan): 비교할 다른 계획
            
        Returns:
            bool: 이 계획이 더 좋으면 True
        """
        if other_plan is None:
            return True
        
        my_quality = self.get_quality()
        other_quality = other_plan.get_quality()
        
        # missing 개수 비교
        if my_quality[0] < other_quality[0]:
            return True
        elif my_quality[0] > other_quality[0]:
            return False
        
        # missing 개수가 같으면 비용 비교
        return my_quality[1] < other_quality[1]
    
    def is_complete(self):
        """
        모든 파이프가 배치되었는지 확인
        
        Returns:
            bool: 완전한 계획이면 True
        """
        return self.num_missing() == 0
    
    def is_feasible(self, max_missing=0):
        """
        허용 가능한 계획인지 확인
        
        Args:
            max_missing (int): 허용되는 최대 missing 파이프 수
            
        Returns:
            bool: 실행 가능하면 True
        """
        return self.num_missing() <= max_missing
    
    def copy(self):
        """
        계획의 깊은 복사본을 만듭니다
        
        Returns:
            Plan: 복사된 계획
        """
        import copy
        new_pipes = [copy.deepcopy(p) for p in self.pipes]
        return Plan(new_pipes)
    
    def get_all_occupied_cells(self):
        """
        모든 배치된 파이프가 차지하는 셀들을 반환
        
        Returns:
            set: 점유된 모든 셀 {(x,y,z), ...}
        """
        occupied = set()
        for pipe in self.get_routed_pipes():
            occupied.update(pipe.get_occupied_cells())
        return occupied
    
    def __repr__(self):
        """디버깅용 문자열"""
        return f"Plan({self.num_routed()}/{self.num_pipes} routed, cost={self.total_cost():.1f})"
    
    def __str__(self):
        """사용자 친화적 문자열"""
        routed = self.num_routed()
        total = self.num_pipes
        cost = self.total_cost()
        
        if cost == float('inf'):
            cost_str = "N/A"
        else:
            cost_str = f"{cost:.1f}"
        
        return f"계획: {routed}/{total} 파이프 배치됨, 총 비용: {cost_str}"
    
    def summary(self):
        """
        계획의 상세 요약을 출력합니다
        """
        print("=" * 60)
        print(f"파이프 배치 계획 요약")
        print("=" * 60)
        print(f"전체 파이프 수: {self.num_pipes}")
        print(f"배치된 파이프: {self.num_routed()}")
        print(f"배치 안 된 파이프: {self.num_missing()}")
        
        if self.num_routed() > 0:
            print(f"\n총 비용: {self.total_cost():.1f}")
            
            routed = self.get_routed_pipes()
            total_length = sum(p.length for p in routed)
            total_bends = sum(p.num_bends for p in routed)
            
            print(f"총 길이: {total_length:.1f}m")
            print(f"총 구부림: {total_bends}개")
            
            print("\n개별 파이프 정보:")
            for pipe in routed:
                print(f"  {pipe}")
        
        if self.num_missing() > 0:
            print("\n배치 안 된 파이프:")
            for pipe in self.get_missing_pipes():
                print(f"  파이프 {pipe.id}: {pipe.start} -> {pipe.goal}")
        
        print("=" * 60)
