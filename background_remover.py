import cv2
import numpy as np
import logging
from rembg import remove
import os
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_removal.log'),
        logging.StreamHandler()
    ]
)

class BackgroundRemover:
    def __init__(self):
        """배경 제거 클래스 초기화"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("BackgroundRemover initialized")

    def remove_background(self, input_path, output_path=None):
        """
        이미지의 배경을 제거하는 메인 함수
        
        Args:
            input_path (str): 입력 이미지 경로
            output_path (str, optional): 출력 이미지 경로. 지정하지 않으면 자동 생성
        
        Returns:
            str: 처리된 이미지의 저장 경로
        """
        try:
            self.logger.info(f"Processing image: {input_path}")
            
            # 입력 이미지 읽기
            input_image = cv2.imread(input_path)
            if input_image is None:
                raise ValueError(f"Could not read image from {input_path}")
            
            # rembg를 사용하여 배경 제거
            output = remove(input_image)
            
            # 출력 경로가 지정되지 않은 경우 자동 생성
            if output_path is None:
                filename = os.path.splitext(os.path.basename(input_path))[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"output_{filename}_{timestamp}.png"
            
            # 결과 저장
            cv2.imwrite(output_path, output)
            self.logger.info(f"Processed image saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            raise

def main():
    """메인 실행 함수"""
    try:
        # BackgroundRemover 인스턴스 생성
        remover = BackgroundRemover()
        
        # 입력 이미지 경로 설정
        input_image = "input.jpg"  # 사용자가 원하는 이미지 경로로 변경
        
        # 배경 제거 실행
        output_path = remover.remove_background(input_image)
        
        print(f"배경이 제거된 이미지가 저장되었습니다: {output_path}")
        
    except Exception as e:
        logging.error(f"프로그램 실행 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 