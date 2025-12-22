"""
BaseSolver 클래스
개별 파이프의 경로를 찾는 솔버의 기본 인터페이스입니다.
"""

from abc import ABC, abstractmethod

class BaseSolver(ABC):
    """
    하위 레벨 솔버의 추상 기본 클래스
    한 개의 파이프에 대해 최적 경로를 찾습니다
    """
    
    def __init__(self, environment):
        """
        솔버 초기화
        
        Args:
            environment (Environment): 3D 환경
        """
        self.environment = environment
        self.timeout = 180  # 초 단위 시간 제한
    
    @abstractmethod
    def solve(self, pipe, obstacles_pipes=None):
        """
        파이프의 최적 경로를 찾습니다
        
        Args:
            pipe (Pipe): 경로를 찾을 파이프
            obstacles_pipes (list): 장애물로 간주할 다른 파이프들
            
        Returns:
            list or None: 경로 [(x,y,z), ...] 또는 None (실패 시)
        """
        pass
    
    def set_timeout(self, timeout):
        """
        시간 제한 설정
        
        Args:
            timeout (int): 초 단위 시간 제한
        """
        self.timeout = timeout
