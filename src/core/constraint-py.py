"""
Constraint 클래스
파이프 간의 우선순위 제약을 나타냅니다.
"""

class Constraint:
    """
    우선순위 제약: pipe_i ≺ pipe_j
    즉, pipe_i가 pipe_j보다 먼저 경로를 정합니다
    """
    
    def __init__(self, higher_priority_pipe, lower_priority_pipe):
        """
        제약 생성
        
        Args:
            higher_priority_pipe (int): 높은 우선순위 파이프 ID
            lower_priority_pipe (int): 낮은 우선순위 파이프 ID
        """
        self.higher = higher_priority_pipe
        self.lower = lower_priority_pipe
    
    def __eq__(self, other):
        """같은 제약인지 비교"""
        return (self.higher == other.higher and 
                self.lower == other.lower)
    
    def __hash__(self):
        """집합(set)에 넣을 수 있도록 해시 함수 제공"""
        return hash((self.higher, self.lower))
    
    def __repr__(self):
        """디버깅용 표현"""
        return f"Constraint({self.higher} ≺ {self.lower})"
    
    def __str__(self):
        """사용자 친화적 표현"""
        return f"파이프 {self.higher}이(가) 파이프 {self.lower}보다 우선"


class ConstraintSet:
    """
    여러 제약들의 집합을 관리하는 클래스
    제약들 간의 일관성(consistency)을 체크합니다
    """
    
    def __init__(self):
        """빈 제약 집합 생성"""
        self.constraints = set()  # Constraint 객체들의 집합
    
    def add(self, constraint):
        """
        제약 추가
        
        Args:
            constraint (Constraint): 추가할 제약
        """
        self.constraints.add(constraint)
    
    def add_priority(self, higher, lower):
        """
        우선순위 제약을 추가하는 편의 함수
        
        Args:
            higher (int): 높은 우선순위 파이프 ID
            lower (int): 낮은 우선순위 파이프 ID
        """
        self.add(Constraint(higher, lower))
    
    def is_consistent(self):
        """
        제약 집합이 일관성이 있는지 확인
        즉, 순환(cycle)이 없는지 체크합니다
        
        예: A ≺ B, B ≺ C, C ≺ A 는 불가능 (순환)
        
        Returns:
            bool: 일관성이 있으면 True
        """
        # 방향 그래프를 만들어서 사이클 탐지
        graph = self._build_graph()
        
        # DFS로 사이클 탐지
        visited = set()
        rec_stack = set()  # 현재 DFS 경로에 있는 노드들
        
        for node in graph:
            if node not in visited:
                if self._has_cycle_dfs(node, graph, visited, rec_stack):
                    return False
        
        return True
    
    def _build_graph(self):
        """
        제약들로부터 방향 그래프를 만듭니다
        
        Returns:
            dict: {노드: [이웃 노드들]} 형태의 인접 리스트
        """
        graph = {}
        
        for constraint in self.constraints:
            # higher -> lower 방향의 간선
            if constraint.higher not in graph:
                graph[constraint.higher] = []
            graph[constraint.higher].append(constraint.lower)
            
            # lower 노드도 그래프에 추가 (간선이 없어도)
            if constraint.lower not in graph:
                graph[constraint.lower] = []
        
        return graph
    
    def _has_cycle_dfs(self, node, graph, visited, rec_stack):
        """
        DFS로 사이클이 있는지 확인
        
        Args:
            node: 현재 노드
            graph: 그래프 (인접 리스트)
            visited: 방문한 노드들
            rec_stack: 현재 DFS 경로의 노드들
            
        Returns:
            bool: 사이클이 있으면 True
        """
        visited.add(node)
        rec_stack.add(node)
        
        # 이웃 노드들 확인
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if self._has_cycle_dfs(neighbor, graph, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                # 현재 경로에 있는 노드를 다시 방문 -> 사이클!
                return True
        
        rec_stack.remove(node)
        return False
    
    def get_priority_order(self):
        """
        제약 조건을 만족하는 위상 정렬 순서를 반환
        
        Returns:
            list: 파이프 ID들의 순서 (높은 우선순위부터)
                 순환이 있으면 None 반환
        """
        if not self.is_consistent():
            return None
        
        graph = self._build_graph()
        return self._topological_sort(graph)
    
    def _topological_sort(self, graph):
        """
        위상 정렬 구현 (Kahn's algorithm)
        
        Args:
            graph: 인접 리스트 그래프
            
        Returns:
            list: 정렬된 노드 리스트
        """
        # 각 노드의 진입 차수(in-degree) 계산
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1
        
        # 진입 차수가 0인 노드들로 시작
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # 이웃 노드들의 진입 차수 감소
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def copy(self):
        """
        제약 집합의 복사본 생성
        
        Returns:
            ConstraintSet: 복사된 제약 집합
        """
        new_set = ConstraintSet()
        new_set.constraints = self.constraints.copy()
        return new_set
    
    def __len__(self):
        """제약 개수"""
        return len(self.constraints)
    
    def __repr__(self):
        """디버깅용 표현"""
        return f"ConstraintSet({len(self)} constraints)"
    
    def __str__(self):
        """사용자 친화적 표현"""
        if len(self.constraints) == 0:
            return "제약 없음"
        
        lines = [f"총 {len(self)}개의 우선순위 제약:"]
        for constraint in sorted(self.constraints, key=lambda c: (c.higher, c.lower)):
            lines.append(f"  {constraint}")
        
        return "\n".join(lines)
