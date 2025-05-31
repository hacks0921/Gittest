# 이미지 배경 제거 프로그램

이 프로그램은 OpenCV와 rembg 라이브러리를 사용하여 이미지의 배경을 제거하는 기능을 제공합니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 사용 방법

1. 배경을 제거하고 싶은 이미지를 프로젝트 폴더에 넣습니다.
2. `background_remover.py` 파일에서 `input_image` 변수의 값을 원하는 이미지 파일명으로 변경합니다.
3. 프로그램을 실행합니다:
```bash
python background_remover.py
```

## 기능

- 이미지 배경 자동 제거
- 로그 파일 생성 (`background_removal.log`)
- 자동 파일명 생성 (타임스탬프 포함)

## 주의사항

- 입력 이미지는 JPG, PNG 형식을 지원합니다.
- 출력 이미지는 PNG 형식으로 저장됩니다.
- 처리된 이미지는 자동으로 생성된 파일명으로 저장됩니다. 