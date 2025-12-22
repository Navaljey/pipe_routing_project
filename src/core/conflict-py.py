"""
Conflict 클래스
두 파이프 간의 충돌 정보를 나타냅니다.
"""

class Conflict:
    """
    두 파이프가 같은 공간을 차지하는 충돌을 나타냅니다
    """
    
    def __init__(self, pipe1_id, pipe2_id, location=None):
        """
        충돌 생성
        
        Args:
            pipe1_id (int): 첫 번째 파이프 ID
            pipe2_id (int): 두 번째 파이프 ID
            location (tuple): 충돌 위치 (x, y, z) - 선택사항
        """
        # 항상 작은 ID를 먼저 저장 (순서 통일)
        if pipe1_id < pipe2_id:
            self.pipe1 = pipe1_id
            self.pipe2 = pipe2_id
        else:
            self.pipe1 = pipe2_id
            self.pipe2 = pipe1_id
        
        self.location = location  # 충돌이 발생한 위치
    
    def get_pipes(self):
        """
        충돌하는 두 파이프의 ID를 반환
        
        Returns:
            tuple: (pipe1_id, pipe2_id)
        """
        return (self.pipe1, self.pipe2)
    
    def involves(self, pipe_id):
        """
        이 충돌에 특정 파이프가 관련되어 있는지 확인
        
        Args:
            pipe_id (int): 확인할 파이프 ID
            
        Returns:
            bool: 관련되어 있으면 True
        """
        return pipe_id == self.pipe1 or pipe_id == self.pipe2
    
    def get_other_pipe(self, pipe_id):
        """
        충돌하는 파이프 중 주어진 파이프가 아닌 다른 파이프 반환
        
        Args:
            pipe_id (int): 한 파이프의 ID
            
        Returns:
            int: 다른 파이프의 ID
        """
        if pipe_id == self.pipe1:
            return self.pipe2
        elif pipe_id == self.pipe2:
            return self.pipe1
        else:
            return None
    
    def __eq__(self, other):
        """같은 충돌인지 비교"""
        return (self.pipe1 == other.pipe1 and 
                self.pipe2 == other.pipe2)
    
    def __hash__(self):
        """집합에 넣을 수 있도록 해시 함수"""
        return hash((self.pipe1, self.pipe2))
    
    def __repr__(self):
        """디버깅용 표현"""
        loc_str = f" at {self.location}" if self.location else ""
        return f"Conflict({self.pipe1}, {self.pipe2}{loc_str})"
    
    def __str__(self):
        """사용자 친화적 표현"""
        if self.location:
            return f"파이프 {self.pipe1}과 {self.pipe2}가 {self.location}에서 충돌"
        else:
            return f"파이프 {self.pipe1}과 {self.pipe2}가 충돌"
