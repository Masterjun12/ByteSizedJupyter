yolov8 코드는 https://youtu.be/fHf9aPkpuoY?si=ZUlyVHZQ73MPNs1j 유튜브를 참고했다


result 

- 공통적으로 3가지의 영상을 통해 분석해본 결과 특정 이상의 속도에서는 디텍팅이 안되는 문제가 발생한다.

	- 프레임과 time 속도 측정 부분의 오류가 발생하기 때문이라고 추측한다.

	- 실제로 고속도로에서 촬영된 걸로 추정되는 video 2 는 높은 속도 탓에 한대가 검출 되는게 전부였다.
	
	- 영상에도 볼수 있는 것처럼 구동시 많이 떨어지는 프레임 탓에 속도 측정에 오류가 있는것 같다고 추정된다.


Tracking 에 사용되는 DeepSORT에 대해 알아보고 Kalman Filter를 공부해볼수 있었다

https://taehyeong51.github.io/%EB%85%BC%EB%AC%B8%EB%A6%AC%EB%B7%B0/PaperReview_01_DeepSORT/