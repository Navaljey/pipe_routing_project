"""
QualityEvaluator 클래스
파이프 배치 계획의 품질을 평가합니다.
"""

class QualityEvaluator:
    """
    계획의 품질을 평가하고 비교하는 클래스
    논문의 Quality 함수를 구현합니다
    """
    
    def __init__(self):
        """평가자 초기화"""
        pass
    
    def evaluate(self, plan):
        """
        계획의 품질을 평가
        Quality(S) = (num_missing, total_cost)
        
        Args:
            plan (Plan): 평가할 계획
            
        Returns:
            tuple: (missing 파이프 수, 총 비용)
        """
        return plan.get_quality()
    
    def compare(self, plan1, plan2):
        """
        두 계획을 비교
        사전식 순서: missing이 적으면 무조건 좋음, 같으면 비용으로 비교
        
        Args:
            plan1 (Plan): 첫 번째 계획
            plan2 (Plan): 두 번째 계획
            
        Returns:
            int: plan1이 더 좋으면 -1, 같으면 0, plan2가 더 좋으면 1
        """
        q1 = self.evaluate(plan1)
        q2 = self.evaluate(plan2)
        
        # missing 비교
        if q1[0] < q2[0]:
            return -1
        elif q1[0] > q2[0]:
            return 1
        
        # missing이 같으면 비용 비교
        if q1[1] < q2[1]:
            return -1
        elif q1[1] > q2[1]:
            return 1
        
        return 0
    
    def is_better(self, plan1, plan2):
        """
        plan1이 plan2보다 나은지 확인
        
        Args:
            plan1 (Plan): 첫 번째 계획
            plan2 (Plan): 두 번째 계획
            
        Returns:
            bool: plan1이 더 좋으면 True
        """
        return self.compare(plan1, plan2) < 0
    
    def calculate_cost_gap(self, plan, baseline_plan):
        """
        기준 계획 대비 비용 차이 계산 (%)
        논문의 cost gap 개념
        
        Args:
            plan (Plan): 평가할 계획
            baseline_plan (Plan): 기준 계획 (예: 독립 라우팅)
            
        Returns:
            float: 비용 차이 비율 (%)
        """
        baseline_cost = baseline_plan.total_cost()
        plan_cost = plan.total_cost()
        
        if baseline_cost == 0 or baseline_cost == float('inf'):
            return float('inf')
        
        if plan_cost == float('inf'):
            return float('inf')
        
        # (현재 비용 / 기준 비용 - 1) * 100
        gap = (plan_cost / baseline_cost - 1) * 100
        return gap
    
    def get_detailed_metrics(self, plan):
        """
        상세한 평가 지표들을 반환
        
        Args:
            plan (Plan): 평가할 계획
            
        Returns:
            dict: 평가 지표들
        """
        routed_pipes = plan.get_routed_pipes()
        
        if len(routed_pipes) == 0:
            return {
                'num_pipes': plan.num_pipes,
                'num_routed': 0,
                'num_missing': plan.num_pipes,
                'total_cost': float('inf'),
                'total_length': 0,
                'total_bends': 0,
                'avg_cost': 0,
                'avg_length': 0,
                'avg_bends': 0
            }
        
        # 통계 계산
        total_length = sum(p.length for p in routed_pipes)
        total_bends = sum(p.num_bends for p in routed_pipes)
        total_cost = plan.total_cost()
        
        num_routed = len(routed_pipes)
        
        return {
            'num_pipes': plan.num_pipes,
            'num_routed': num_routed,
            'num_missing': plan.num_missing(),
            'total_cost': total_cost,
            'total_length': total_length,
            'total_bends': total_bends,
            'avg_cost': total_cost / num_routed,
            'avg_length': total_length / num_routed,
            'avg_bends': total_bends / num_routed
        }
    
    def print_comparison(self, plan1, plan2, plan1_name="Plan 1", plan2_name="Plan 2"):
        """
        두 계획의 비교 결과를 출력
        
        Args:
            plan1 (Plan): 첫 번째 계획
            plan2 (Plan): 두 번째 계획
            plan1_name (str): 첫 번째 계획 이름
            plan2_name (str): 두 번째 계획 이름
        """
        metrics1 = self.get_detailed_metrics(plan1)
        metrics2 = self.get_detailed_metrics(plan2)
        
        print("=" * 70)
        print(f"계획 비교: {plan1_name} vs {plan2_name}")
        print("=" * 70)
        
        print(f"\n{'지표':<20} {plan1_name:<20} {plan2_name:<20}")
        print("-" * 70)
        
        # 배치된 파이프 수
        print(f"{'배치된 파이프':<20} "
              f"{metrics1['num_routed']:<20} "
              f"{metrics2['num_routed']:<20}")
        
        # Missing 파이프 수
        print(f"{'미배치 파이프':<20} "
              f"{metrics1['num_missing']:<20} "
              f"{metrics2['num_missing']:<20}")
        
        # 총 비용
        cost1_str = f"{metrics1['total_cost']:.1f}" if metrics1['total_cost'] != float('inf') else "N/A"
        cost2_str = f"{metrics2['total_cost']:.1f}" if metrics2['total_cost'] != float('inf') else "N/A"
        print(f"{'총 비용':<20} {cost1_str:<20} {cost2_str:<20}")
        
        # 총 길이
        print(f"{'총 길이 (m)':<20} "
              f"{metrics1['total_length']:.1f}m":<20} "
              f"{metrics2['total_length']:.1f}m":<20}")
        
        # 총 구부림
        print(f"{'총 구부림':<20} "
              f"{metrics1['total_bends']:<20} "
              f"{metrics2['total_bends']:<20}")
        
        print("-" * 70)
        
        # 어느 쪽이 더 좋은지
        comparison = self.compare(plan1, plan2)
        if comparison < 0:
            print(f"\n결과: {plan1_name}이(가) 더 좋습니다!")
        elif comparison > 0:
            print(f"\n결과: {plan2_name}이(가) 더 좋습니다!")
        else:
            print(f"\n결과: 두 계획이 동등합니다.")
        
        print("=" * 70)
