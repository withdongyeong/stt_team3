# 1. 개요

### 1.1 팀
대구 AI 스쿨

심화 3팀(매콤찜닭 스카이넷)

김동영, 장창대, 김성진, 조유경

### 1.2 프로젝트
Sound to Text 자연어 처리 프로젝트

한국어 음성 입력을 음성->텍스트로 변환 후

변환된 텍스트를 [인사, 사과, 감사, 위급, 날씨] 총 5개의 클래스로 분류하여 식별

# 2. 요구사항
    pip install -r requirements.txt

음성 식별에 애저 STT

한글 토크나이저로 konlpy를 사용

konlpy를 사용하기 위해 jdk 설치 및 환경 설정,

jpype 설치가 필요하며

특이사항으로 호환성 문제가 있어 jpype의 버전을 최신 버전이 아니라 0.7로

다운그레이드하여 사용

# 3. 사용방법
![img.png](imgs/main.png)

### 1. 음성 입력 및 예측하기
1. SubKey = 애저 STT subscriptionkey 입력
2. WeightPath = 예측에 사용할 pth 파일 경로를 browse로 입력
3. OK 버튼 클릭
4. mic start 버튼을 누른 후, 음성 입력
5. mic stop 버튼을 클릭하면 식별된 음성이 텍스트로 변환되어 출력
6. predict 버튼을 클릭하면 예측된 라벨을 출력

### 2. 수동 학습 데이터 만들기
1. SavePath = 데이터가 저장될 위치를 browse로 입력
2. 타이핑 체크박스 클릭
3. 수동으로 데이터 입력
4. 인사, 사과, 감사, 위급, 날씨 중 라벨을 선택
5. save 버튼을 누르면 SavePath에 학습 데이터 저장

### 3. 학습하기
![img.png](imgs/train.png)
1. 학습 및 평가 데이터 폴더 경로 입력
2. pth 파일의 저장 경로 입력
3. 학습 및 평가 데이터 분리 비율 입력
4. learning rate 입력
5. epochs 입력
6. batch size 입력
7. train start 버튼 클릭

### 4. 한글 text agumentation 기능
![img.png](imgs/augmentation.png)
1. 타겟 데이터 폴더 경로 입력
2. agument start 버튼 클릭