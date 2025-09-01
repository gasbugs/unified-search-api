# 1. Base Image
# Python 3.12 버전의 공식 이미지를 기반으로 합니다.
# alpine 기반의 경량화된 이미지로, 보안과 크기 면에서 이점이 있습니다.
FROM python:3.12-alpine

# 2. Working Directory
# 컨테이너 내에서 작업할 디렉토리를 설정합니다.
# 이후의 모든 명령어(COPY, RUN 등)는 이 디렉토리(/app)를 기준으로 실행됩니다.
WORKDIR /app

# 3. Copy requirements.txt
# 호스트의 requirements.txt 파일을 컨테이너의 /app 디렉토리로 복사합니다.
# 소스 코드보다 먼저 복사하여, 의존성이 변경되지 않으면 Docker 빌드 캐시를 활용해 빌드 시간을 단축합니다.
COPY requirements.txt .

# 4. Install Dependencies
# requirements.txt에 명시된 파이썬 패키지들을 설치합니다.
# --no-cache-dir 옵션은 불필요한 캐시를 저장하지 않아 이미지 크기를 최적화합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Source Code
# 현재 디렉토리(호스트)의 모든 파일을 컨테이너의 /app 디렉토리로 복사합니다.
# .dockerignore 파일에 명시된 파일 및 디렉토리는 이 과정에서 제외됩니다.
COPY . .

# 6. Expose Port
# 컨테이너가 8000번 포트를 외부에 노출하도록 설정합니다.
# FastAPI 애플리케이션이 이 포트에서 실행될 예정입니다.
EXPOSE 8000

# 7. Command to Run
# 컨테이너가 시작될 때 실행할 명령어를 정의합니다.
# Uvicorn 서버를 실행하여 FastAPI 애플리케이션을 서비스합니다.
# --host 0.0.0.0: 컨테이너 외부에서 접근할 수 있도록 모든 네트워크 인터페이스에 바인딩합니다.
# --port 8000: 8000번 포트에서 서비스를 실행합니다.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
