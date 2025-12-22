"""
CTNode 클래스
Conflict Tree(충돌 트리)의 노드를 나타냅니다.
PBS 알고리즘에서 사용됩니다.
"""

from .constraint import ConstraintSet

class CTNode:
    """
    Conflict Tree의 노드
    각 노드는 하나의 계획(plan)과 제약 집합(constraints)을 가집니다
    """
    
    def __init__(self, plan, constraints=None):
        """
        CT 노드 생성
        
        Args:
            plan (Plan): 이 노드의 파이프 배치 계획
            constraints (ConstraintSet): 우선순위 제약들
        """
        self.plan = plan
        
        if constraints is None:
            self.constraints = ConstraintSet()
        else:
            self.constraints = constraints
        
        # 트리 구조
        self.parent = None
        self.children = []
        
        # 노드 정보
        self.depth = 0  # 루트로부터의 깊이
    
    def add_constraint(self, constraint):
        """
        이 노드에 제약 추가
        
        Args:
            constraint (Constraint): 추가할 제약
        """
        self.constraints.add(constraint)
    
    def is_consistent(self):
        """
        이 노드의 제약 집합이 일관성이 있는지 확인
        
        Returns:
            bool: 일관성이 있으면 True (순환이 없음)
        """
        return self.constraints.is_consistent()
    
    def get_quality(self):
        """
        이 노드 계획의 품질 반환
        
        Returns:
            tuple: (missing pipes 수, 총 비용)
        """
        return self.plan.get_quality()
    
    def is_complete(self):
        """
        이 노드의 계획이 완전한지 확인
        (모든 파이프가 배치됨)
        
        Returns:
            bool: 완전하면 True
        """
        return self.plan.is_complete()
    
    def is_feasible(self, max_missing=0):
        """
        이 노드의 계획이 실행 가능한지 확인
        
        Args:
            max_missing (int): 허용되는 최대 missing pipes
            
        Returns:
            bool: 실행 가능하면 True
        """
        return self.plan.is_feasible(max_missing)
    
    def create_child(self, new_plan, new_constraint):
        """
        자식 노드를 생성합니다
        
        Args:
            new_plan (Plan): 새로운 계획
            new_constraint (Constraint): 추가할 제약
            
        Returns:
            CTNode: 생성된 자식 노드
        """
        # 제약 집합 복사
        child_constraints = self.constraints.copy()
        child_constraints.add(new_constraint)
        
        # 자식 노드 생성
        child = CTNode(new_plan, child_constraints)
        child.parent = self
        child.depth = self.depth + 1
        
        self.children.append(child)
        
        return child
    
    def __repr__(self):
        """디버깅용 표현"""
        quality = self.get_quality()
        return f"CTNode(depth={self.depth}, missing={quality[0]}, cost={quality[1]:.1f})"
    
    def __str__(self):
        """사용자 친화적 표현"""
        quality = self.get_quality()
        return (f"CT 노드 (깊이 {self.depth}): "
                f"{quality[0]}개 미배치, 비용 {quality[1]:.1f}")
