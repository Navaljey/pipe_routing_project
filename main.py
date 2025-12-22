"""
3D Pipe Routing 메인 실행 파일
"""

import argparse
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.environment.instance_loader import InstanceLoader
from src.algorithms.low_level.a_star_solver import AStarSolver
from src.algorithms.high_level.fix_order import FixOrder
from src.algorithms.high_level.pbs import PBS
from src.evaluation.quality_evaluator import QualityEvaluator


def main():
    """메인 함수"""
    
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(
        description='3D Pipe Routing with Priority-Based Search'
    )
    
    parser.add_argument(
        '--instance',
        type=str,
        default='small',
        help='인스턴스 이름 (small, medium_1, medium_2, medium_3, medium_4, agru, lng_train)'
    )
    
    parser.add_argument(
        '--algorithm',
        type=str,
        default='PBS',
        choices=['FixOrder', 'PBS', 'PBS-MP'],
        help='사용할 알고리즘'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=960,
        help='최대 실행 시간 (초)'
    )
    
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='샘플 인스턴스 생성'
    )
    
    args = parser.parse_args()
    
    # 샘플 인스턴스 생성
    if args.create_sample:
        print("샘플 인스턴스 생성 중...")
        loader = InstanceLoader()
        loader.create_sample_instance('small')
        print("샘플 인스턴스 생성 완료!")
        return
    
    # 헤더 출력
    print("=" * 70)
    print("3D Pipe Routing with Priority-Based Search")
    print("=" * 70)
    print(f"인스턴스: {args.instance}")
    print(f"알고리즘: {args.algorithm}")
    print(f"시간 제한: {args.timeout}초")
    print("=" * 70)
    print()
    
    # 1. 인스턴스 로드
    print("1. 인스턴스 로딩...")
    try:
        loader = InstanceLoader()
        environment, pipes = loader.load_instance(args.instance)
        print(f"   ✓ 로드 완료")
        print(f"   - 파이프: {len(pipes)}개")
        print(f"   - 장애물: {len(environment.obstacles)}개")
        print(f"   - 공간 크기: {environment.bounds}")
        print()
    except FileNotFoundError as e:
        print(f"   ✗ 오류: {e}")
        print(f"   샘플 인스턴스를 생성하려면: python main.py --create-sample")
        return
    
    # 2. 솔버 초기화
    print("2. 솔버 초기화...")
    solver = AStarSolver(environment)
    solver.set_timeout(180)
    print(f"   ✓ A* 솔버 준비 완료")
    print()
    
    # 3. 알고리즘 실행
    print(f"3. {args.algorithm} 알고리즘 실행...")
    print("-" * 70)
    
    if args.algorithm == 'FixOrder':
        algorithm = FixOrder(environment, solver)
        result_plan = algorithm.solve(pipes)
    
    elif args.algorithm == 'PBS':
        algorithm = PBS(environment, solver, max_missing=0, conflict_policy=2)
        result_plan = algorithm.solve(pipes, timeout=args.timeout)
    
    elif args.algorithm == 'PBS-MP':
        # PBS with Missing Pipes (maxMissing = ∞)
        algorithm = PBS(environment, solver, max_missing=float('inf'), conflict_policy=2)
        result_plan = algorithm.solve(pipes, timeout=args.timeout)
    
    print("-" * 70)
    print()
    
    # 4. 결과 출력
    print("4. 결과 요약")
    print("=" * 70)
    result_plan.summary()
    
    # 5. 품질 평가
    print("\n5. 품질 평가")
    print("=" * 70)
    evaluator = QualityEvaluator()
    metrics = evaluator.get_detailed_metrics(result_plan)
    
    print(f"배치 성공률: {metrics['num_routed']}/{metrics['num_pipes']} "
          f"({metrics['num_routed']/metrics['num_pipes']*100:.1f}%)")
    
    if metrics['num_routed'] > 0:
        print(f"평균 길이: {metrics['avg_length']:.2f}m")
        print(f"평균 구부림: {metrics['avg_bends']:.2f}개")
        print(f"평균 비용: {metrics['avg_cost']:.2f}")
    
    print("=" * 70)
    print("\n실행 완료!")


if __name__ == '__main__':
    main()
