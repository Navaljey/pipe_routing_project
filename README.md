# 3D Pipe Routing with Priority-Based Search

이 프로젝트는 "From Multi-Agent Pathfinding to 3D Pipe Routing" 논문을 구현한 것입니다.
산업 플랜트에서 여러 파이프를 충돌 없이 배치하는 문제를 해결합니다.

## 프로젝트 소개

### 문제 정의
- **목표**: 3D 공간에서 여러 개의 파이프를 시작점에서 목표점까지 연결
- **제약**: 파이프끼리 충돌하면 안 됨, 장비를 피해야 함
- **최소화**: 총 비용 (파이프 길이 + 구부림 비용 + 지지대 비용)

### 구현된 알고리즘
1. **PBS (Priority-Based Search)**: 우선순위를 동적으로 결정하는 메인 알고리즘
2. **PBS-MP**: 일부 파이프를 배치하지 못해도 허용하는 버전
3. **FixOrder**: 고정된 순서로 배치 (기준 알고리즘)
4. **OneDive**: 한 번의 깊은 탐색
5. **Randomized Restart**: 여러 번 재시작
6. **Hill Climbing**: 해를 점진적으로 개선

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/pipe-routing.git
cd pipe-routing
```

### 2. Python 가상환경 생성 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. MiniZinc 설치 (선택사항 - 더 최적화된 경로 원할 때)

#### MiniZinc 다운로드 및 설치
1. [MiniZinc 공식 사이트](https://www.minizinc.org/software.html)에서 다운로드
2. OS에 맞는 버전 설치
   - Windows: MiniZinc-X.X.X-bundle-windows.exe 실행
   - Mac: MiniZinc-X.X.X-bundle-macos.dmg 마운트 후 설치
   - Linux: `sudo apt install minizinc` 또는 AppImage 다운로드

#### 백엔드 솔버 확인
MiniZinc 설치 시 다음 오픈소스 솔버가 포함됩니다:
- **COIN-OR CBC**: 빠른 MIP 솔버 (기본값, 권장)
- **SCIP**: 강력한 제약 최적화 솔버
- **Chuffed**: CP 솔버
- **Gecode**: CP 솔버

설치 확인:
```bash
minizinc --solvers
```

## 실행 방법

### 기본 실행
```bash
python main.py --instance small --algorithm PBS
```

### 모든 알고리즘 비교
```bash
python scripts/run_all_experiments.sh
```

### 실행 옵션
- `--instance`: 실험 인스턴스 선택 (small, medium_1, medium_2, medium_3, medium_4, agru, lng_train)
- `--algorithm`: 알고리즘 선택 (PBS, PBS-MP, FixOrder, OneDive, RR, HC)
- `--timeout`: 최대 실행 시간 (초)
- `--visualize`: 결과를 3D로 시각화

### 예시
```bash
# Small 인스턴스를 PBS로 풀고 결과 시각화
python main.py --instance small --algorithm PBS --visualize

# Medium_1 인스턴스를 1시간 동안 Hill Climbing으로 실행
python main.py --instance medium_1 --algorithm HC --timeout 3600
```

## 프로젝트 구조

```
pipe_routing_project/
├── main.py                    # 프로그램 진입점
├── config/                    # 설정 파일
├── data/                      # 실험 데이터
│   └── instances/            # 문제 인스턴스들
├── src/                       # 소스 코드
│   ├── core/                 # 핵심 데이터 구조
│   ├── environment/          # 3D 환경 관리
│   ├── algorithms/           # 경로 탐색 알고리즘
│   ├── evaluation/           # 품질 평가
│   ├── experiment/           # 실험 관리
│   └── visualization/        # 결과 시각화
├── results/                   # 실험 결과
└── tests/                     # 테스트 코드
```

## 실험 결과

실행하면 다음과 같은 결과물이 생성됩니다:
- `results/plots/`: 시간에 따른 성능 그래프 (논문 Figure 4)
- `results/tables/`: 알고리즘 비교 표 (논문 Table 2, 3)
- `results/raw_data/`: 원본 실험 데이터 (CSV 형식)

## 개발자 가이드

### 새로운 알고리즘 추가하기
1. `src/algorithms/high_level/` 폴더에 새 파일 생성
2. `BaseAlgorithm` 클래스를 상속받아 구현
3. `main.py`에 새 알고리즘 등록

### 테스트 실행
```bash
pytest tests/
```

### 코드 스타일
이 프로젝트는 PEP 8 스타일 가이드를 따릅니다.

## 참고 문헌

Belov, G., Du, W., Garcia de la Banda, M., Harabor, D., Koenig, S., & Wei, X. (2020). 
From Multi-Agent Pathfinding to 3D Pipe Routing. 
In Proceedings of the Thirteenth International Symposium on Combinatorial Search (SoCS 2020).

## 라이선스

MIT License

## 문의

문제가 발생하면 GitHub Issues에 등록해주세요.
