import cv2
import numpy as np

filter_list = [
    "블러링",
    "샤프닝",
    "엣지검출",
    "애드",
    "섭트렉트",
    "머지",
    "콘트라스트",
    "가우시안블러링",
    "박스블러링",
    "미디안_블러링",
    "언샤프_마스크_필터링",
    "라플라시안_샤프닝",
    "커스텀_커널_사용_샤프닝",
    "엣지검출_1차미분마스크",
    "엣지검출_로버츠마스크",
    "엣지검출_소벨마스크",
    "엣지검출_라플라시안",
    "엣지검출_LoG",
    "엣지검출_케니엣지",
    "엣지검출_모폴로지",
    "엣지검출_팽창",
    "리사이즈_확대",
    "리사이즈_축소",
    "인터폴레이션",
    "평행이동",
    "회전_90도",
    "원근투시변환",
    "매핑",
    "이산푸리에변환",
    "dft_필터링"
]

def 블러링(img):
    return cv2.blur(img, (9, 9))

def 샤프닝(img):
    blurred = cv2.GaussianBlur(img, (0, 0), 3)
    return cv2.addWeighted(img, 1.5, blurred, -0.5, 0)

def 엣지검출(img):
    edge = cv2.Canny(img, 100, 200)
    return cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)

def 애드(img):
    return cv2.add(img, np.full_like(img, 50))

def 섭트렉트(img):
    return cv2.subtract(img, np.full_like(img, 50))

def 머지(img1, img2):
    img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))  # 크기 맞추기
    return cv2.addWeighted(img1, 0.5, img2_resized, 0.5, 0)


def 콘트라스트(img):
    return cv2.convertScaleAbs(img, alpha=1.5, beta=0)

def 가우시안블러링(img):
    return cv2.GaussianBlur(img, (9, 9), 0)

def 박스블러링(img):
    return cv2.boxFilter(img, -1, (9, 9))

def 미디안_블러링(img):
    return cv2.medianBlur(img, 9)

def 언샤프_마스크_필터링(img):
    gaussian = cv2.GaussianBlur(img, (9, 9), 10.0)
    return cv2.addWeighted(img, 1.5, gaussian, -0.5, 0)

def 라플라시안_샤프닝(img):
    lap = cv2.Laplacian(img, cv2.CV_64F)
    sharp = cv2.convertScaleAbs(lap)
    return sharp

def 커스텀_커널_사용_샤프닝(img):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)

def 엣지검출_1차미분마스크(img):
    kernel = np.array([[1, -1]])
    return cv2.filter2D(img, -1, kernel)

def 엣지검출_로버츠마스크(img):
    kernel = np.array([[1, 0], [0, -1]])
    return cv2.filter2D(img, -1, kernel)

def 엣지검출_소벨마스크(img):
    sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1)
    return cv2.convertScaleAbs(cv2.magnitude(sobelx, sobely))

def 엣지검출_라플라시안(img):
    return cv2.convertScaleAbs(cv2.Laplacian(img, cv2.CV_64F))

def 엣지검출_LoG(img):
    blur = cv2.GaussianBlur(img, (3, 3), 0)
    return cv2.Laplacian(blur, cv2.CV_64F)

def 엣지검출_케니엣지(img):
    edge = cv2.Canny(img, 100, 200)
    return cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)

def 엣지검출_모폴로지(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, np.ones((3,3),np.uint8))
    return cv2.cvtColor(gradient, cv2.COLOR_GRAY2BGR)

def 엣지검출_팽창(img):
    kernel = np.ones((3, 3), np.uint8)
    dilation = cv2.dilate(img, kernel, iterations=1)
    return dilation

def 리사이즈_확대(img):
    rows, cols = img.shape[:2]
    return cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

def 리사이즈_축소(img):
    rows, cols = img.shape[:2]
    return cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)

def 인터폴레이션(img):
    return cv2.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv2.INTER_CUBIC)

def 평행이동(img):
    rows, cols = img.shape[:2]
    M = np.float32([[1, 0, 50], [0, 1, 50]])
    return cv2.warpAffine(img, M, (cols, rows))

def 회전_90도(img):
    return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

def 원근투시변환(img):
    rows, cols = img.shape[:2]
    pts1 = np.float32([[50,50],[200,50],[50,200],[200,200]])
    pts2 = np.float32([[10,100],[200,50],[100,250],[220,220]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(img, M, (cols, rows))

def 매핑(img):
    h, w = img.shape[:2]
    K = np.eye(3)
    D = np.zeros(5)
    map1, map2 = cv2.initUndistortRectifyMap(K, D, None, K, (w, h), cv2.CV_32FC1)
    return cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR)

def 이산푸리에변환(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude = cv2.magnitude(dft_shift[:,:,0], dft_shift[:,:,1])
    magnitude = np.log(magnitude + 1)
    return cv2.cvtColor(cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8), cv2.COLOR_GRAY2BGR)

def dft_필터링(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    rows, cols = gray.shape
    crow, ccol = rows//2 , cols//2
    mask = np.zeros((rows, cols, 2), np.uint8)
    mask[crow-30:crow+30, ccol-30:ccol+30] = 1
    fshift = dft_shift * mask
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:,:,0], img_back[:,:,1])
    return cv2.cvtColor(cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8), cv2.COLOR_GRAY2BGR)