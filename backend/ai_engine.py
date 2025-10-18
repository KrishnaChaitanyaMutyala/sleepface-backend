import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from PIL import Image
import io
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import asyncio
from skimage import exposure, filters
from skimage.feature import local_binary_pattern

from models import AnalysisResponse, FeatureScores, RoutineData, DailySummary, WeeklySummary, NoFaceDetectedError, ImageProcessingError, InvalidImageFormatError

class Core5Engine:
    """
    Core 5 AI Engine for analyzing sleep and skin health from selfies
    """
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        # Load TensorFlow Lite models (placeholder - you'll need to train these)
        self.dark_circles_model = None
        self.puffiness_model = None
        self.brightness_model = None
        self.wrinkles_model = None
        self.texture_model = None
        
        # Initialize models
        self._load_models()
    
    def _load_models(self):
        """Load actual trained models"""
        try:
            # Try to load TensorFlow Lite models
            self.dark_circles_model = tf.lite.Interpreter(model_path="models/dark_circles.tflite")
            self.puffiness_model = tf.lite.Interpreter(model_path="models/puffiness.tflite")
            self.brightness_model = tf.lite.Interpreter(model_path="models/brightness.tflite")
            self.wrinkles_model = tf.lite.Interpreter(model_path="models/wrinkles.tflite")
            self.texture_model = tf.lite.Interpreter(model_path="models/texture.tflite")
            
            # Allocate tensors
            self.dark_circles_model.allocate_tensors()
            self.puffiness_model.allocate_tensors()
            self.brightness_model.allocate_tensors()
            self.wrinkles_model.allocate_tensors()
            self.texture_model.allocate_tensors()
            
            print("✅ [AI ENGINE] ML models loaded successfully")
        except Exception as e:
            print(f"⚠️ [AI ENGINE] Models not found, using enhanced heuristics: {e}")
            # Set to None to indicate fallback mode
            self.dark_circles_model = None
            self.puffiness_model = None
            self.brightness_model = None
            self.wrinkles_model = None
            self.texture_model = None
    
    async def analyze_image(self, image_data: bytes, user_id: str, routine: Dict[str, Any]) -> AnalysisResponse:
        """Enhanced analysis with confidence scoring - maintains existing flow"""
        try:
            print(f"🔍 [AI ENGINE] Starting enhanced analysis for user: {user_id}")
            print(f"📊 [AI ENGINE] Routine data: {routine}")
            
            # Convert bytes to OpenCV image
            image = self._bytes_to_cv2(image_data)
            print(f"🖼️ [AI ENGINE] Image converted to OpenCV format: {image.shape}")
            
            # Extract face landmarks
            landmarks = self._extract_landmarks(image)
            if landmarks is None:
                print("❌ [AI ENGINE] No face detected in image")
                raise NoFaceDetectedError()
            
            print(f"👤 [AI ENGINE] Face landmarks extracted: {landmarks.shape}")
            
            # Analyze each feature
            print("🔬 [AI ENGINE] Starting feature analysis...")
            features = await self._analyze_features(image, landmarks)
            print(f"📈 [AI ENGINE] Features analyzed: {features}")
            
            # NEW: Quality assessment
            quality_metrics = self._assess_analysis_quality(image, landmarks, features)
            print(f"📊 [AI ENGINE] Quality assessment: {quality_metrics}")
            
            # Calculate scores with lifestyle data integration
            sleep_score = self._calculate_sleep_score(features, routine)
            skin_health_score = self._calculate_skin_health_score(features, routine)
            print(f"🎯 [AI ENGINE] Scores calculated - Sleep: {sleep_score}, Skin: {skin_health_score}")
            
            # Generate fun label
            fun_label = self._generate_fun_label(sleep_score, skin_health_score)
            print(f"🏷️ [AI ENGINE] Fun label generated: {fun_label}")
            
            # Enhanced response with quality metrics
            response = AnalysisResponse(
                user_id=user_id,
                date=datetime.now().isoformat()[:10],
                sleep_score=sleep_score,
                skin_health_score=skin_health_score,
                features=FeatureScores(**features),
                routine=RoutineData(**routine) if routine else None,
                fun_label=fun_label,
                confidence=quality_metrics['overall_confidence']  # Enhanced from static 0.85
            )
            
            print(f"✅ [AI ENGINE] Enhanced analysis complete! Confidence: {quality_metrics['overall_confidence']:.2f}")
            return response
            
        except (NoFaceDetectedError, ImageProcessingError, InvalidImageFormatError) as e:
            # Re-raise custom exceptions as-is
            print(f"❌ [AI ENGINE] {type(e).__name__}: {str(e)}")
            raise
        except Exception as e:
            print(f"❌ [AI ENGINE] Enhanced analysis failed: {str(e)}")
            raise Exception(f"Enhanced analysis failed: {str(e)}")
    
    def _assess_analysis_quality(self, image: np.ndarray, landmarks: np.ndarray, features: Dict) -> Dict[str, float]:
        """Assess quality of analysis for confidence scoring"""
        quality_factors = {
            'image_sharpness': self._assess_image_sharpness(image),
            'lighting_quality': self._assess_lighting_quality(image),
            'face_detection_confidence': self._assess_face_detection_quality(landmarks),
            'feature_consistency': self._assess_feature_consistency(features)
        }
        
        # Calculate weighted overall confidence
        weights = {'image_sharpness': 0.25, 'lighting_quality': 0.25, 
                   'face_detection_confidence': 0.3, 'feature_consistency': 0.2}
        
        overall_confidence = sum(quality_factors[k] * weights[k] for k in weights)
        
        return {
            'overall_confidence': min(max(overall_confidence, 0.0), 1.0),
            **quality_factors
        }
    
    def _assess_image_sharpness(self, image: np.ndarray) -> float:
        """Assess image sharpness using Laplacian variance"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Normalize sharpness score (typical range: 0-2000)
        sharpness_score = min(laplacian_var / 500.0, 1.0)
        return sharpness_score
    
    def _assess_lighting_quality(self, image: np.ndarray) -> float:
        """Assess lighting conditions"""
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Check for overexposure and underexposure
        overexposed = np.sum(gray > 240) / gray.size
        underexposed = np.sum(gray < 20) / gray.size
        
        # Check contrast
        contrast = gray.std()
        
        # Good lighting: low over/under exposure, reasonable contrast
        lighting_score = 1.0 - (overexposed + underexposed)
        lighting_score *= min(contrast / 50.0, 1.0)  # Penalize low contrast
        
        return max(lighting_score, 0.0)
    
    def _assess_face_detection_quality(self, landmarks: np.ndarray) -> float:
        """Assess quality of face detection"""
        # Check landmark distribution and stability
        landmark_spread = np.std(landmarks, axis=0)
        
        # Good detection should have reasonable spread in x,y but not z
        x_spread = landmark_spread[0]
        y_spread = landmark_spread[1]
        
        # Normalize based on typical face size
        detection_quality = min((x_spread + y_spread) / 0.4, 1.0)
        
        return detection_quality
    
    def _assess_feature_consistency(self, features: Dict[str, float]) -> float:
        """Assess consistency of feature detection"""
        feature_values = list(features.values())
        
        # Check for extreme outliers that might indicate errors
        feature_array = np.array(feature_values)
        z_scores = np.abs((feature_array - np.mean(feature_array)) / (np.std(feature_array) + 1e-7))
        
        # Penalize features with extreme Z-scores (likely errors)
        outlier_penalty = np.sum(z_scores > 3) / len(feature_values)
        consistency_score = 1.0 - outlier_penalty
        
        return max(consistency_score, 0.0)
    
    def _bytes_to_cv2(self, image_data: bytes) -> np.ndarray:
        """Enhanced image preprocessing with lighting normalization"""
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise InvalidImageFormatError()
            
            # Convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Apply minimal preprocessing for accurate analysis
            # Only resize if too small, no aggressive filtering
            h, w = image.shape[:2]
            if h < 200 or w < 200:
                # Only resize if image is too small
                scale = max(200/h, 200/w)
                new_h, new_w = int(h * scale), int(w * scale)
                image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            
            return image
        except Exception as e:
            if isinstance(e, InvalidImageFormatError):
                raise
            raise ImageProcessingError(f"Failed to process image: {str(e)}")
    
    def _apply_preprocessing_pipeline(self, image: np.ndarray) -> np.ndarray:
        """Apply advanced preprocessing while maintaining original size/format"""
        # CLAHE for lighting normalization
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        lab[:,:,0] = clahe.apply(lab[:,:,0])
        image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        # Noise reduction while preserving edges
        image = cv2.bilateralFilter(image, 9, 75, 75)
        
        # Skin tone normalization
        image = self._normalize_skin_tone(image)
        
        return image
    
    def _normalize_skin_tone(self, image: np.ndarray) -> np.ndarray:
        """Normalize skin tone for consistent analysis"""
        # Detect dominant skin color and normalize
        # Convert to HSV for better skin tone detection
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Create skin mask using HSV thresholds
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Calculate average skin tone
        skin_pixels = image[skin_mask > 0]
        if len(skin_pixels) > 0:
            avg_skin_color = np.mean(skin_pixels, axis=0)
            # Apply subtle normalization
            target_skin = np.array([200, 180, 160])  # Target skin tone
            adjustment = (target_skin - avg_skin_color) * 0.1  # Subtle adjustment
            image = np.clip(image + adjustment, 0, 255).astype(np.uint8)
        
        return image
    
    def _extract_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract face landmarks using MediaPipe"""
        results = self.face_mesh.process(image)
        
        if not results.multi_face_landmarks:
            return None
        
        # Get the first face
        face_landmarks = results.multi_face_landmarks[0]
        
        # Convert to numpy array
        landmarks = np.array([[lm.x, lm.y, lm.z] for lm in face_landmarks.landmark])
        
        return landmarks
    
    async def _analyze_features(self, image: np.ndarray, landmarks: np.ndarray) -> Dict[str, float]:
        """Analyze the 5 core features"""
        features = {}
        
        print("👁️ [AI ENGINE] Extracting eye region for dark circles and puffiness...")
        # Extract eye region for dark circles and puffiness
        eye_region = self._extract_eye_region(image, landmarks)
        print(f"👁️ [AI ENGINE] Eye region extracted: {eye_region.shape}")
        
        print("🌑 [AI ENGINE] Analyzing dark circles...")
        # Dark circles analysis
        features['dark_circles'] = await self._analyze_dark_circles(eye_region)
        print(f"🌑 [AI ENGINE] Dark circles score: {features['dark_circles']}")
        
        print("💧 [AI ENGINE] Analyzing puffiness...")
        # Puffiness analysis
        features['puffiness'] = await self._analyze_puffiness(eye_region, landmarks)
        print(f"💧 [AI ENGINE] Puffiness score: {features['puffiness']}")
        
        print("✨ [AI ENGINE] Analyzing brightness...")
        # Brightness analysis
        features['brightness'] = await self._analyze_brightness(image, landmarks)
        print(f"✨ [AI ENGINE] Brightness score: {features['brightness']}")
        
        print("📏 [AI ENGINE] Analyzing wrinkles...")
        # Wrinkles analysis
        features['wrinkles'] = await self._analyze_wrinkles(image, landmarks)
        print(f"📏 [AI ENGINE] Wrinkles score: {features['wrinkles']}")
        
        print("🧽 [AI ENGINE] Analyzing texture...")
        # Texture analysis
        features['texture'] = await self._analyze_texture(image, landmarks)
        print(f"🧽 [AI ENGINE] Texture score: {features['texture']}")
        
        print("🔍 [AI ENGINE] Analyzing pore size...")
        # Pore size analysis
        features['pore_size'] = await self._analyze_pore_size(image, landmarks)
        print(f"🔍 [AI ENGINE] Pore size score: {features['pore_size']}")
        
        return features
    
    def _extract_eye_region(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Extract eye region using bounding box approach"""
        h, w = image.shape[:2]
        
        # Use MediaPipe's eye landmark indices
        left_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        right_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        # Combine both eyes
        eye_indices = left_eye_indices + right_eye_indices
        
        # Filter valid indices
        valid_indices = [idx for idx in eye_indices if idx < len(landmarks)]
        if not valid_indices:
            print("⚠️ [AI ENGINE] No valid eye landmarks found, using face region")
            return self._extract_face_region(image, landmarks)
        
        # Get eye landmark points
        eye_points = landmarks[valid_indices]
        
        # Create bounding box with padding
        x_min = int(np.min(eye_points[:, 0]) * w)
        y_min = int(np.min(eye_points[:, 1]) * h)
        x_max = int(np.max(eye_points[:, 0]) * w)
        y_max = int(np.max(eye_points[:, 1]) * h)
        
        # Add padding
        padding = 15
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(w, x_max + padding)
        y_max = min(h, y_max + padding)
        
        # Ensure valid region
        if x_max <= x_min or y_max <= y_min:
            print("⚠️ [AI ENGINE] Invalid eye region, using face region")
            return self._extract_face_region(image, landmarks)
        
        eye_region = image[y_min:y_max, x_min:x_max]
        print(f"👁️ [AI ENGINE] Eye region extracted: {eye_region.shape}")
        
        return eye_region
    
    def _create_anatomical_mask(self, landmarks: np.ndarray, region_type: str, image_shape: tuple) -> np.ndarray:
        """Create anatomical mask for specific facial regions"""
        h, w = image_shape
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Define all landmark indices
        left_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246, 130, 25, 110, 24, 23, 22, 26, 112, 243, 190, 56, 28, 27, 29, 30, 56, 190, 243, 112, 26, 22, 23, 24, 110, 25, 130, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7, 33]
        right_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398, 463, 253, 339, 254, 255, 256, 252, 341, 412, 441, 285, 281, 280, 279, 278, 285, 441, 412, 341, 252, 256, 255, 254, 339, 253, 463, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382, 362]
        forehead_indices = [10, 151, 9, 8, 107, 55, 65, 52, 53, 46, 70, 63, 105, 66, 69, 67, 109, 10]
        cheek_indices = [116, 117, 118, 119, 120, 121, 126, 142, 36, 205, 206, 207, 213, 192, 147, 187, 207, 206, 205, 36, 142, 126, 121, 120, 119, 118, 117, 116]
        pore_indices = [1, 2, 5, 4, 6, 19, 20, 94, 125, 141, 235, 236, 3, 51, 48, 115, 131, 134, 102, 49, 220, 305, 281, 360, 279, 331, 294, 460, 328, 326, 2, 97, 326, 327, 293, 334, 296, 336, 9, 10, 151, 337, 299, 333, 298, 301, 368, 264, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109, 10]
        
        # Get the appropriate indices based on region type
        if region_type == 'left_eye':
            indices = left_eye_indices
        elif region_type == 'right_eye':
            indices = right_eye_indices
        elif region_type == 'forehead':
            indices = forehead_indices
        elif region_type == 'cheek':
            indices = cheek_indices
        elif region_type == 'pore_region':
            indices = pore_indices
        else:
            return mask
        
        # Validate landmark indices
        valid_indices = [idx for idx in indices if idx < len(landmarks)]
        if not valid_indices:
            return mask
        
        # Get landmark points
        points = landmarks[valid_indices]
        
        # Convert to image coordinates
        points_pixels = np.array([[int(p[0] * w), int(p[1] * h)] for p in points])
        
        # Create convex hull for better region definition
        try:
            hull = cv2.convexHull(points_pixels.astype(np.int32))
            cv2.fillPoly(mask, [hull], 255)
        except:
            # Fallback: use bounding box
            x, y, w_rect, h_rect = cv2.boundingRect(points_pixels.astype(np.int32))
            cv2.rectangle(mask, (x, y), (x + w_rect, y + h_rect), 255, -1)
        
        return mask
    
    async def _analyze_dark_circles(self, eye_region: np.ndarray) -> float:
        """Enhanced dark circles analysis with varied scoring"""
        if eye_region.size == 0:
            print("⚠️ [AI ENGINE] No eye region for dark circles analysis")
            return 50.0
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(eye_region, cv2.COLOR_RGB2GRAY)
        
        # Focus on lower eye area where dark circles appear
        h, w = gray.shape
        lower_eye = gray[int(h*0.6):, :]  # Bottom 40% of eye region
        
        if lower_eye.size == 0:
            lower_eye = gray
        
        # Analyze darkness and contrast
        mean_brightness = np.mean(lower_eye)
        brightness_std = np.std(lower_eye)
        
        # Detect dark patches (potential dark circles)
        dark_threshold = mean_brightness - brightness_std
        dark_pixels = np.sum(lower_eye < dark_threshold)
        dark_ratio = dark_pixels / lower_eye.size
        
        # Calculate texture variation (dark circles create more variation)
        texture_variance = np.var(lower_eye)
        
        # Score calculation: 0 = severe dark circles, 100 = no dark circles
        # Brightness factor (higher brightness = better)
        brightness_score = min(mean_brightness / 2.55, 100)
        
        # Dark ratio factor (lower dark ratio = better)
        dark_score = max(0, 100 - (dark_ratio * 200))
        
        # Texture factor (lower variance = smoother, better)
        texture_score = max(0, 100 - (texture_variance / 100))
        
        # Combine scores with realistic weighting
        final_score = (brightness_score * 0.5 + dark_score * 0.3 + texture_score * 0.2)
        
        # Add some natural variation based on image characteristics
        variation_factor = (mean_brightness + brightness_std + texture_variance) / 1000
        final_score += (variation_factor - 0.5) * 20  # ±10 point variation
        
        # Ensure realistic range (25-90 for most people)
        final_score = max(25, min(90, final_score))
        
        print(f"🌑 [AI ENGINE] Dark circles - brightness: {brightness_score:.1f}, dark_ratio: {dark_ratio:.3f}, texture: {texture_variance:.1f} -> {final_score:.1f}")
        
        return round(final_score, 1)
    
    
    def _detect_skin_tone_factor(self, region: np.ndarray) -> float:
        """Detect skin tone and return adjustment factor"""
        # Analyze dominant colors to determine skin tone
        hsv = cv2.cvtColor(region, cv2.COLOR_RGB2HSV)
        avg_hue = np.mean(hsv[:, :, 0])
        avg_saturation = np.mean(hsv[:, :, 1])
        
        # Adjust scoring based on skin tone
        if avg_hue < 10 and avg_saturation < 100:  # Lighter skin tones
            return 1.1  # Slightly more lenient scoring
        elif avg_hue > 15 or avg_saturation > 150:  # Darker skin tones
            return 0.9  # Slightly stricter scoring
        else:
            return 1.0  # No adjustment
    
    async def _analyze_puffiness(self, eye_region: np.ndarray, landmarks: np.ndarray) -> float:
        """Enhanced puffiness analysis with varied scoring"""
        if eye_region.size == 0:
            print("⚠️ [AI ENGINE] No eye region for puffiness analysis")
            return 50.0
        
        # Convert to grayscale
        gray = cv2.cvtColor(eye_region, cv2.COLOR_RGB2GRAY)
        
        # Focus on lower eye area where puffiness appears
        h, w = gray.shape
        lower_region = gray[int(h*0.6):, :]  # Bottom 40% of eye region
        
        if lower_region.size == 0:
            lower_region = gray
        
        # Calculate multiple texture metrics
        texture_variance = np.var(lower_region)
        texture_mean = np.mean(lower_region)
        
        # Calculate gradient magnitude (puffy areas have less gradient)
        grad_x = cv2.Sobel(lower_region, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(lower_region, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        avg_gradient = np.mean(gradient_magnitude)
        
        # Calculate smoothness using Laplacian
        laplacian = cv2.Laplacian(lower_region, cv2.CV_64F)
        laplacian_variance = np.var(laplacian)
        
        # Detect rounded areas (puffiness creates more rounded contours)
        contours, _ = cv2.findContours(cv2.Canny(lower_region, 50, 150), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        roundness_factor = 0
        if contours:
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 50:  # Filter small contours
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        roundness_factor += circularity
            roundness_factor = min(roundness_factor / len(contours), 1.0) if contours else 0
        
        # Score calculation: 0 = severe puffiness, 100 = no puffiness
        # Higher texture variance = less puffy (more definition)
        texture_score = min(texture_variance / 50, 100)
        
        # Higher gradient = less puffy (more definition)
        gradient_score = min(avg_gradient * 10, 100)
        
        # Lower Laplacian variance = more puffy (smoother)
        laplacian_score = max(0, 100 - (laplacian_variance / 10))
        
        # Higher roundness = more puffy
        roundness_score = max(0, 100 - (roundness_factor * 100))
        
        # Combine scores with realistic weighting
        final_score = (texture_score * 0.3 + gradient_score * 0.3 + laplacian_score * 0.2 + roundness_score * 0.2)
        
        # Add natural variation based on image characteristics
        variation_factor = (texture_variance + avg_gradient + laplacian_variance) / 500
        final_score += (variation_factor - 0.5) * 15  # ±7.5 point variation
        
        # Ensure realistic range (20-85 for most people)
        final_score = max(20, min(85, final_score))
        
        print(f"💧 [AI ENGINE] Puffiness - texture: {texture_variance:.1f}, gradient: {avg_gradient:.2f}, laplacian: {laplacian_variance:.1f}, roundness: {roundness_factor:.2f} -> {final_score:.1f}")
        
        return round(final_score, 1)
    
    async def _analyze_brightness(self, image: np.ndarray, landmarks: np.ndarray) -> float:
        """Enhanced brightness analysis with varied scoring"""
        face_region = self._extract_face_region(image, landmarks)
        
        if face_region.size == 0:
            print("⚠️ [AI ENGINE] No face region for brightness analysis")
            return 50.0
        
        # Convert to LAB color space for better brightness analysis
        lab = cv2.cvtColor(face_region, cv2.COLOR_RGB2LAB)
        l_channel = lab[:, :, 0]  # L channel represents lightness
        
        # Calculate multiple brightness metrics
        mean_brightness = np.mean(l_channel)
        brightness_std = np.std(l_channel)
        median_brightness = np.median(l_channel)
        
        # Calculate brightness distribution
        brightness_hist = cv2.calcHist([l_channel], [0], None, [256], [0, 256])
        brightness_peaks = len(cv2.findContours((brightness_hist > np.max(brightness_hist) * 0.1).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0])
        
        # Analyze skin tone evenness (healthy skin has more even tone)
        # Convert back to RGB for skin tone analysis
        rgb_face = cv2.cvtColor(face_region, cv2.COLOR_RGB2BGR)
        hsv_face = cv2.cvtColor(rgb_face, cv2.COLOR_BGR2HSV)
        
        # Calculate color variance (more even = better)
        h_variance = np.var(hsv_face[:, :, 0])  # Hue variance
        s_variance = np.var(hsv_face[:, :, 1])  # Saturation variance
        
        # Score calculation: 0 = very dull, 100 = very bright
        # Base brightness score
        brightness_score = min(mean_brightness / 2.55, 100)
        
        # Uniformity score (lower std = more uniform)
        uniformity_score = max(0, 100 - (brightness_std / 3))
        
        # Evenness score (lower variance = more even)
        evenness_score = max(0, 100 - ((h_variance + s_variance) / 200))
        
        # Distribution score (fewer peaks = more consistent)
        distribution_score = max(0, 100 - (brightness_peaks * 10))
        
        # Combine scores with realistic weighting
        final_score = (brightness_score * 0.5 + uniformity_score * 0.25 + evenness_score * 0.15 + distribution_score * 0.1)
        
        # Add natural variation based on image characteristics
        variation_factor = (mean_brightness + brightness_std + h_variance + s_variance) / 1000
        final_score += (variation_factor - 0.5) * 12  # ±6 point variation
        
        # Ensure realistic range (15-95 for most people)
        final_score = max(15, min(95, final_score))
        
        print(f"✨ [AI ENGINE] Brightness - mean: {mean_brightness:.1f}, std: {brightness_std:.1f}, h_var: {h_variance:.1f}, s_var: {s_variance:.1f} -> {final_score:.1f}")
        
        return round(final_score, 1)
    
    async def _analyze_wrinkles(self, image: np.ndarray, landmarks: np.ndarray) -> float:
        """Enhanced wrinkles analysis with varied scoring"""
        forehead_region = self._extract_forehead_region(image, landmarks)
        
        if forehead_region.size == 0:
            print("⚠️ [AI ENGINE] No forehead region for wrinkles analysis")
            return 50.0
        
        gray = cv2.cvtColor(forehead_region, cv2.COLOR_RGB2GRAY)
        
        # Apply slight blur to reduce noise while preserving wrinkles
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Detect fine lines using multiple edge detection methods
        edges_canny = cv2.Canny(blurred, 30, 100)
        edges_sobel = cv2.Sobel(blurred, cv2.CV_64F, 1, 1, ksize=3)
        edges_laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
        
        # Calculate edge metrics
        edge_density_canny = np.sum(edges_canny > 0) / edges_canny.size
        edge_density_sobel = np.sum(np.abs(edges_sobel) > 50) / edges_sobel.size
        edge_density_laplacian = np.sum(np.abs(edges_laplacian) > 30) / edges_laplacian.size
        
        # Calculate texture metrics
        texture_variance = np.var(gray)
        texture_mean = np.mean(gray)
        
        # Calculate gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        avg_gradient = np.mean(gradient_magnitude)
        max_gradient = np.max(gradient_magnitude)
        
        # Analyze line patterns (wrinkles create specific patterns)
        # Use morphological operations to detect line-like structures
        kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        
        horizontal_lines = cv2.morphologyEx(edges_canny, cv2.MORPH_OPEN, kernel_horizontal)
        vertical_lines = cv2.morphologyEx(edges_canny, cv2.MORPH_OPEN, kernel_vertical)
        
        horizontal_line_density = np.sum(horizontal_lines > 0) / horizontal_lines.size
        vertical_line_density = np.sum(vertical_lines > 0) / vertical_lines.size
        
        # Score calculation: 0 = severe wrinkles, 100 = no wrinkles
        # Edge-based scores (lower density = better)
        edge_score_canny = max(0, 100 - (edge_density_canny * 1000))
        edge_score_sobel = max(0, 100 - (edge_density_sobel * 500))
        edge_score_laplacian = max(0, 100 - (edge_density_laplacian * 800))
        
        # Texture score (lower variance = smoother, better)
        texture_score = max(0, 100 - (texture_variance / 80))
        
        # Gradient score (lower gradient = smoother, better)
        gradient_score = max(0, 100 - (avg_gradient / 4))
        
        # Line pattern score (fewer lines = better)
        line_score = max(0, 100 - ((horizontal_line_density + vertical_line_density) * 1000))
        
        # Combine scores with realistic weighting
        final_score = (
            edge_score_canny * 0.25 + 
            edge_score_sobel * 0.15 + 
            edge_score_laplacian * 0.15 + 
            texture_score * 0.25 + 
            gradient_score * 0.15 + 
            line_score * 0.05
        )
        
        # Add natural variation based on image characteristics
        variation_factor = (texture_variance + avg_gradient + edge_density_canny + edge_density_sobel) / 1000
        final_score += (variation_factor - 0.5) * 18  # ±9 point variation
        
        # Ensure realistic range (10-90 for most people)
        final_score = max(10, min(90, final_score))
        
        print(f"📏 [AI ENGINE] Wrinkles - canny: {edge_density_canny:.4f}, sobel: {edge_density_sobel:.4f}, texture: {texture_variance:.1f}, gradient: {avg_gradient:.2f} -> {final_score:.1f}")
        
        return round(final_score, 1)
    
    async def _analyze_texture(self, image: np.ndarray, landmarks: np.ndarray) -> float:
        """Enhanced texture analysis with varied scoring"""
        cheek_region = self._extract_cheek_region(image, landmarks)
        
        if cheek_region.size == 0:
            print("⚠️ [AI ENGINE] No cheek region for texture analysis")
            return 50.0
        
        gray = cv2.cvtColor(cheek_region, cv2.COLOR_RGB2GRAY)
        
        # Apply slight blur to reduce noise while preserving texture
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Calculate texture smoothness using multiple methods
        # 1. Gradient magnitude (smooth skin has lower gradients)
        grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        avg_gradient = np.mean(gradient_magnitude)
        max_gradient = np.max(gradient_magnitude)
        
        # 2. Laplacian variance (smooth skin has lower variance)
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
        laplacian_variance = np.var(laplacian)
        laplacian_mean = np.mean(np.abs(laplacian))
        
        # 3. Standard deviation (smooth skin has lower std)
        std_dev = np.std(gray)
        mean_intensity = np.mean(gray)
        
        # 4. Local Binary Pattern (LBP) for texture analysis
        try:
            lbp = local_binary_pattern(blurred, P=8, R=1, method='uniform')
            lbp_variance = np.var(lbp)
        except:
            lbp_variance = 0
        
        # 5. Gabor filter response for texture patterns
        try:
            # Simple Gabor-like filter using Gaussian derivatives
            gabor_kernel = cv2.getGaborKernel((21, 21), 5, 0, 10, 0.5, 0, ktype=cv2.CV_32F)
            gabor_response = cv2.filter2D(blurred, cv2.CV_8UC3, gabor_kernel)
            gabor_variance = np.var(gabor_response)
        except:
            gabor_variance = 0
        
        # Score: 0 = very rough, 100 = very smooth
        # Gradient-based scores
        gradient_score = max(0, 100 - (avg_gradient / 1.5))
        max_gradient_score = max(0, 100 - (max_gradient / 5))
        
        # Laplacian-based scores
        laplacian_score = max(0, 100 - (laplacian_variance / 80))
        laplacian_mean_score = max(0, 100 - (laplacian_mean / 3))
        
        # Standard deviation score
        std_score = max(0, 100 - (std_dev / 2))
        
        # LBP score (lower variance = smoother)
        lbp_score = max(0, 100 - (lbp_variance / 50)) if lbp_variance > 0 else 50
        
        # Gabor score (lower variance = smoother)
        gabor_score = max(0, 100 - (gabor_variance / 100)) if gabor_variance > 0 else 50
        
        # Combine scores with realistic weighting
        final_score = (
            gradient_score * 0.25 + 
            max_gradient_score * 0.15 + 
            laplacian_score * 0.2 + 
            laplacian_mean_score * 0.1 + 
            std_score * 0.2 + 
            lbp_score * 0.05 + 
            gabor_score * 0.05
        )
        
        # Add natural variation based on image characteristics
        variation_factor = (avg_gradient + laplacian_variance + std_dev + lbp_variance + gabor_variance) / 1000
        final_score += (variation_factor - 0.5) * 15  # ±7.5 point variation
        
        # Ensure realistic range (20-90 for most people)
        final_score = max(20, min(90, final_score))
        
        print(f"🧽 [AI ENGINE] Texture - gradient: {avg_gradient:.2f}, laplacian: {laplacian_variance:.1f}, std: {std_dev:.1f}, lbp: {lbp_variance:.1f}, gabor: {gabor_variance:.1f} -> {final_score:.1f}")
        
        return round(final_score, 1)
    
    async def _analyze_pore_size(self, image: np.ndarray, landmarks: np.ndarray) -> float:
        """Enhanced pore size analysis with varied scoring"""
        pore_region = self._extract_pore_region(image, landmarks)
        
        if pore_region.size == 0:
            print("⚠️ [AI ENGINE] No pore region for pore size analysis")
            return 50.0
        
        gray = cv2.cvtColor(pore_region, cv2.COLOR_RGB2GRAY)
        
        # Apply different levels of blur to detect pores at different scales
        blurred_light = cv2.GaussianBlur(gray, (3, 3), 0)
        blurred_medium = cv2.GaussianBlur(gray, (5, 5), 0)
        blurred_heavy = cv2.GaussianBlur(gray, (7, 7), 0)
        
        # Detect pores using multiple methods
        pores_small = self._detect_pores_at_scale(blurred_light, gray, scale=1)
        pores_medium = self._detect_pores_at_scale(blurred_medium, gray, scale=2)
        pores_large = self._detect_pores_at_scale(blurred_heavy, gray, scale=3)
        
        # Calculate pore metrics
        total_pores = len(pores_small) + len(pores_medium) + len(pores_large)
        avg_pore_size = np.mean(pores_small + pores_medium + pores_large) if total_pores > 0 else 0
        max_pore_size = np.max(pores_small + pores_medium + pores_large) if total_pores > 0 else 0
        
        # Calculate pore density
        region_area = pore_region.shape[0] * pore_region.shape[1]
        pore_density = total_pores / region_area * 10000  # Scale up for readability
        
        # Analyze skin smoothness (fewer pores = smoother)
        texture_variance = np.var(gray)
        gradient_magnitude = np.sqrt(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)**2 + cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)**2)
        avg_gradient = np.mean(gradient_magnitude)
        
        # Score calculation: 0 = large pores, 100 = small pores
        # Density score (lower density = better)
        density_score = max(0, 100 - (pore_density * 2))
        
        # Size score (smaller average size = better)
        size_score = max(0, 100 - (avg_pore_size * 2)) if avg_pore_size > 0 else 100
        
        # Max size score (smaller max size = better)
        max_size_score = max(0, 100 - (max_pore_size * 1.5)) if max_pore_size > 0 else 100
        
        # Texture score (smoother = better)
        texture_score = max(0, 100 - (texture_variance / 60))
        
        # Gradient score (lower gradient = smoother = better)
        gradient_score = max(0, 100 - (avg_gradient / 2))
        
        # Combine scores with realistic weighting
        final_score = (
            density_score * 0.3 + 
            size_score * 0.25 + 
            max_size_score * 0.2 + 
            texture_score * 0.15 + 
            gradient_score * 0.1
        )
        
        # Add natural variation based on image characteristics
        variation_factor = (pore_density + avg_pore_size + texture_variance + avg_gradient) / 1000
        final_score += (variation_factor - 0.5) * 12  # ±6 point variation
        
        # Ensure realistic range (15-85 for most people)
        final_score = max(15, min(85, final_score))
        
        print(f"🔍 [AI ENGINE] Pore size - total: {total_pores}, avg_size: {avg_pore_size:.1f}, density: {pore_density:.1f}, texture: {texture_variance:.1f} -> {final_score:.1f}")
        
        return round(final_score, 1)
    
    def _detect_pores_at_scale(self, blurred: np.ndarray, original: np.ndarray, scale: int) -> List[float]:
        """Detect pores at a specific scale"""
        # Find dark spots that could be pores
        kernel_size = 2 * scale + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        opened = cv2.morphologyEx(blurred, cv2.MORPH_OPEN, kernel)
        pore_mask = blurred - opened
        
        # Adaptive thresholding based on local statistics
        mean_val = np.mean(pore_mask)
        std_val = np.std(pore_mask)
        threshold = mean_val - 0.5 * std_val
        
        _, pore_binary = cv2.threshold(pore_mask, max(threshold, 10), 255, cv2.THRESH_BINARY)
        
        # Find contours of pore-like structures
        contours, _ = cv2.findContours(pore_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter by size and circularity
        valid_pores = []
        min_area = 2 * scale
        max_area = 50 * scale
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.2:  # Reasonably circular
                        valid_pores.append(area)
        
        return valid_pores
    
    def _calculate_feature_confidence(self, feature_value: float, analysis_quality: dict) -> float:
        """Calculate confidence for individual features"""
        base_confidence = analysis_quality.get('overall_confidence', 0.8)
        
        # Adjust based on feature-specific factors
        if abs(feature_value) > 80:  # Extreme values are less reliable
            base_confidence *= 0.8
        
        return base_confidence
    
    def _apply_temporal_filtering(self, current_features: dict, previous_features: dict = None) -> dict:
        """Smooth features across time to reduce noise"""
        if not previous_features:
            return current_features
        
        filtered_features = {}
        for feature_name, current_value in current_features.items():
            if feature_name in previous_features:
                # Apply exponential smoothing
                alpha = 0.7  # Weight for current measurement
                filtered_value = alpha * current_value + (1 - alpha) * previous_features[feature_name]
                filtered_features[feature_name] = filtered_value
            else:
                filtered_features[feature_name] = current_value
        
        return filtered_features
    
    def _extract_face_region(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Extract face region from image"""
        h, w = image.shape[:2]
        
        # Get face bounding box
        x_min = int(np.min(landmarks[:, 0]) * w)
        y_min = int(np.min(landmarks[:, 1]) * h)
        x_max = int(np.max(landmarks[:, 0]) * w)
        y_max = int(np.max(landmarks[:, 1]) * h)
        
        # Add padding
        padding = 20
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(w, x_max + padding)
        y_max = min(h, y_max + padding)
        
        return image[y_min:y_max, x_min:x_max]
    
    def _extract_forehead_region(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Extract forehead region from image"""
        h, w = image.shape[:2]
        
        # Forehead landmark indices (simplified)
        forehead_indices = [10, 151, 9, 8, 107, 55, 65, 52, 53, 46]
        
        forehead_points = landmarks[forehead_indices]
        
        x_min = int(np.min(forehead_points[:, 0]) * w)
        y_min = int(np.min(forehead_points[:, 1]) * h)
        x_max = int(np.max(forehead_points[:, 0]) * w)
        y_max = int(np.max(forehead_points[:, 1]) * h)
        
        return image[y_min:y_max, x_min:x_max]
    
    def _extract_cheek_region(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Extract cheek region from image"""
        h, w = image.shape[:2]
        
        # Cheek landmark indices (simplified)
        cheek_indices = [116, 117, 118, 119, 120, 121, 126, 142, 36, 205, 206, 207, 213, 192, 147, 187, 207, 213, 192, 147, 187, 207, 213, 192, 147, 187]
        
        cheek_points = landmarks[cheek_indices]
        
        x_min = int(np.min(cheek_points[:, 0]) * w)
        y_min = int(np.min(cheek_points[:, 1]) * h)
        x_max = int(np.max(cheek_points[:, 0]) * w)
        y_max = int(np.max(cheek_points[:, 1]) * h)
        
        return image[y_min:y_max, x_min:x_max]
    
    def _extract_pore_region(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Extract nose and cheek region where pores are most visible"""
        h, w = image.shape[:2]
        
        # Nose and cheek landmark indices (where pores are most visible)
        pore_indices = [116, 117, 118, 119, 120, 121, 126, 142, 36, 205, 206, 207, 213, 192, 147, 187, 168, 8, 9, 10, 151, 107, 55, 65, 52, 53, 46]
        
        pore_points = landmarks[pore_indices]
        
        x_min = int(np.min(pore_points[:, 0]) * w)
        y_min = int(np.min(pore_points[:, 1]) * h)
        x_max = int(np.max(pore_points[:, 0]) * w)
        y_max = int(np.max(pore_points[:, 1]) * h)
        
        return image[y_min:y_max, x_min:x_max]
    
    def _calculate_sleep_score(self, features: Dict[str, float], routine: Dict[str, Any]) -> int:
        """Simplified sleep score calculation - direct average of sleep-related features"""
        print("😴 [AI ENGINE] Calculating sleep score...")
        
        # Simple weighted average of sleep-related features (0-100 scale: higher = better)
        base_score = (
            features['dark_circles'] * 0.4 +         # 40% - dark circles (main sleep indicator)
            features['puffiness'] * 0.3 +            # 30% - puffiness (sleep quality)
            features['brightness'] * 0.3             # 30% - brightness (rested appearance)
        )
        
        print(f"😴 [AI ENGINE] Base score: {base_score:.1f}")
        
        # Small lifestyle bonus (max +10 points)
        lifestyle_bonus = min(10, self._calculate_enhanced_lifestyle_bonus(routine, 'sleep') * 0.1)
        
        # Final score with small lifestyle adjustment
        final_score = int(np.clip(base_score + lifestyle_bonus, 0, 100))
        
        print(f"😴 [AI ENGINE] Enhanced sleep score: {final_score}")
        return final_score
    
    def _calculate_skin_health_score(self, features: Dict[str, float], routine: Dict[str, Any]) -> int:
        """Simplified skin health score calculation - direct average of feature scores"""
        print("✨ [AI ENGINE] Calculating skin health score...")
        
        # Simple weighted average of feature scores (0-100 scale: higher = better)
        # All features contribute equally to skin health
        base_score = (
            features['brightness'] * 0.2 +          # 20% - skin brightness
            features['wrinkles'] * 0.2 +             # 20% - wrinkle reduction
            features['texture'] * 0.2 +              # 20% - skin smoothness
            features['pore_size'] * 0.2 +            # 20% - pore size
            features['puffiness'] * 0.1 +            # 10% - puffiness
            features['dark_circles'] * 0.1           # 10% - dark circles
        )
        
        print(f"✨ [AI ENGINE] Base score: {base_score:.1f}")
        
        # Small lifestyle bonus (max +10 points)
        lifestyle_bonus = min(10, self._calculate_enhanced_lifestyle_bonus(routine, 'skin') * 0.1)
        
        # Final score with small lifestyle adjustment
        final_score = int(np.clip(base_score + lifestyle_bonus, 0, 100))
        
        print(f"✨ [AI ENGINE] Final skin health score: {final_score}")
        return final_score
    
    def _calculate_enhanced_lifestyle_bonus(self, routine: Dict[str, Any], score_type: str) -> float:
        """Enhanced lifestyle factor calculation"""
        bonus = 0
        
        # Enhanced sleep hours logic
        sleep_hours = routine.get('sleep_hours', 0)
        if sleep_hours > 0:
            # Non-linear sleep scoring curve
            if sleep_hours >= 8.5:
                bonus += 25  # Optimal sleep
            elif sleep_hours >= 8:
                bonus += 20  # Excellent sleep
            elif sleep_hours >= 7.5:
                bonus += 15  # Very good sleep
            elif sleep_hours >= 7:
                bonus += 10  # Good sleep
            elif sleep_hours >= 6.5:
                bonus += 5   # Adequate sleep
            elif sleep_hours >= 6:
                bonus += 0   # Minimal adequate
            elif sleep_hours >= 5:
                bonus -= 15  # Poor sleep
            else:
                bonus -= 25  # Very poor sleep
        
        # Enhanced water intake scoring
        water_intake = routine.get('water_intake', 0)
        if water_intake > 0:
            # Optimal hydration curve (diminishing returns)
            if water_intake >= 10:
                bonus += 20  # Excellent hydration
            elif water_intake >= 8:
                bonus += 15  # Very good hydration
            elif water_intake >= 6:
                bonus += 10  # Good hydration
            elif water_intake >= 4:
                bonus += 5   # Adequate hydration
            else:
                bonus -= 10  # Poor hydration
        
        # Enhanced skincare product scoring (for skin health)
        if score_type == 'skin':
            skincare_products = routine.get('skincare_products', [])
            product_used_text = routine.get('product_used', '').lower()
            
            skincare_bonus = 0
            processed_ingredients = set()  # Avoid double counting
            
            # Process skincare_products array
            if skincare_products:
                for product_id in skincare_products:
                    product_lower = product_id.lower()
                    
                    # High-impact ingredients
                    if ('retinol' in product_lower or 'tretinoin' in product_lower) and 'retinol' not in processed_ingredients:
                        skincare_bonus += 20
                        processed_ingredients.add('retinol')
                    elif ('vitamin_c' in product_lower or 'vitamin c' in product_lower or 'ascorbic' in product_lower) and 'vitamin_c' not in processed_ingredients:
                        skincare_bonus += 15
                        processed_ingredients.add('vitamin_c')
                    elif 'sunscreen' in product_lower and 'sunscreen' not in processed_ingredients:
                        skincare_bonus += 15
                        processed_ingredients.add('sunscreen')
                    
                    # Medium-impact ingredients
                    elif ('hyaluronic' in product_lower or 'ha_serum' in product_lower) and 'hyaluronic' not in processed_ingredients:
                        skincare_bonus += 12
                        processed_ingredients.add('hyaluronic')
                    elif ('niacinamide' in product_lower or 'nicotinamide' in product_lower) and 'niacinamide' not in processed_ingredients:
                        skincare_bonus += 10
                        processed_ingredients.add('niacinamide')
                    elif ('peptide' in product_lower or 'copper_peptide' in product_lower) and 'peptide' not in processed_ingredients:
                        skincare_bonus += 10
                        processed_ingredients.add('peptide')
                    
                    # Chemical exfoliants
                    elif ('aha' in product_lower or 'alpha_hydroxy' in product_lower or 'glycolic' in product_lower or 'lactic' in product_lower) and 'aha' not in processed_ingredients:
                        skincare_bonus += 8
                        processed_ingredients.add('aha')
                    elif ('bha' in product_lower or 'beta_hydroxy' in product_lower or 'salicylic' in product_lower) and 'bha' not in processed_ingredients:
                        skincare_bonus += 8
                        processed_ingredients.add('bha')
                    elif 'azelaic' in product_lower and 'azelaic' not in processed_ingredients:
                        skincare_bonus += 8
                        processed_ingredients.add('azelaic')
                    
                    # Basic care
                    elif 'moisturizer' in product_lower and 'moisturizer' not in processed_ingredients:
                        skincare_bonus += 6
                        processed_ingredients.add('moisturizer')
                    elif 'serum' in product_lower and len(processed_ingredients) < 3:  # Generic serum bonus if not many specific ingredients
                        skincare_bonus += 4
                    elif 'cleanser' in product_lower and 'cleanser' not in processed_ingredients:
                        skincare_bonus += 3
                        processed_ingredients.add('cleanser')
                    elif 'toner' in product_lower and 'toner' not in processed_ingredients:
                        skincare_bonus += 4
                        processed_ingredients.add('toner')
                    elif 'mask' in product_lower and 'mask' not in processed_ingredients:
                        skincare_bonus += 5
                        processed_ingredients.add('mask')
            
            # Process legacy product_used text (for backward compatibility)
            if product_used_text:
                if 'vitamin c' in product_used_text and 'vitamin_c' not in processed_ingredients:
                    skincare_bonus += 15
                if 'retinol' in product_used_text and 'retinol' not in processed_ingredients:
                    skincare_bonus += 20
                if 'sunscreen' in product_used_text and 'sunscreen' not in processed_ingredients:
                    skincare_bonus += 15
                if 'moisturizer' in product_used_text and 'moisturizer' not in processed_ingredients:
                    skincare_bonus += 6
                if 'serum' in product_used_text and len(processed_ingredients) < 3:
                    skincare_bonus += 4
            
            bonus += min(skincare_bonus, 30)  # Cap at 30 points for skincare
        
        # NEW: Additional lifestyle factors
        if routine.get('screen_time_before_bed', 0) > 60:
            bonus -= 10  # Penalize excessive screen time
        
        if routine.get('alcohol_consumed', False):
            bonus -= 15  # Penalize alcohol consumption
        
        if routine.get('exercise_today', False):
            bonus += 8   # Reward exercise
        
        if routine.get('stress_level', 5) > 7:  # Assuming 1-10 scale
            bonus -= 12  # Penalize high stress
        elif routine.get('stress_level', 5) < 3:
            bonus += 8   # Reward low stress
        
        return bonus
    
    def _calculate_feature_correlation_bonus(self, features: Dict[str, float], score_type: str) -> float:
        """Bonus based on feature correlation patterns"""
        if score_type == 'sleep':
            # Sleep-related features should correlate (0-100 scale: higher = better)
            sleep_indicators = [features['dark_circles'], features['puffiness'], features['brightness']]
            
            # All high sleep indicators (good sleep)
            if all(score > 70 for score in sleep_indicators):
                return 15  # Strong positive correlation
            elif all(score > 50 for score in sleep_indicators):
                return 8   # Mild positive correlation
            # All low sleep indicators (consistent poor sleep)
            elif all(score < 30 for score in sleep_indicators):
                return -15  # Consistent poor sleep (negative but realistic)
            elif all(score < 50 for score in sleep_indicators):
                return -8   # Mild poor sleep correlation
            
        elif score_type == 'skin':
            # Skin health features should correlate (0-100 scale: higher = better)
            skin_indicators = [features['brightness'], features['wrinkles'], features['texture'], features['pore_size']]
            
            # All high skin indicators (excellent skin)
            if all(score > 70 for score in skin_indicators):
                return 15  # Excellent skin across all metrics
            elif all(score > 50 for score in skin_indicators):
                return 8   # Good skin across all metrics
            # All low skin indicators (poor skin)
            elif all(score < 30 for score in skin_indicators):
                return -15  # Poor skin across all metrics
            elif all(score < 50 for score in skin_indicators):
                return -8   # Mild skin concerns across metrics
        
        return 0  # No clear correlation pattern
    
    def _generate_fun_label(self, sleep_score: int, skin_health_score: int) -> str:
        """Generate status label based on scores - frontend will map to custom icons"""
        avg_score = (sleep_score + skin_health_score) / 2
        
        if avg_score >= 80:
            return "excellent"
        elif avg_score >= 70:
            return "good"
        elif avg_score >= 50:
            return "fair"
        elif avg_score >= 30:
            return "needs_care"
        else:
            return "poor"
    
    async def generate_daily_summary(self, today_data: Optional[Dict], yesterday_data: Optional[Dict]) -> DailySummary:
        """Enhanced daily summary with better recommendations for all 6 features"""
        if not today_data:
            return DailySummary(
                daily_summary="No data available for today.",
                key_insights=[],
                recommendations=[]
            )
        
        # Existing summary logic (maintain)
        today_sleep = today_data.get('sleep_score', 0)
        today_skin = today_data.get('skin_health_score', 0)
        
        if yesterday_data:
            yesterday_sleep = yesterday_data.get('sleep_score', 0)
            yesterday_skin = yesterday_data.get('skin_health_score', 0)
            sleep_change = today_sleep - yesterday_sleep
            skin_change = today_skin - yesterday_skin
            summary = f"Your Sleep Score is {today_sleep} ({sleep_change:+d} from yesterday). "
            summary += f"Skin Health Score is {today_skin} ({skin_change:+d} from yesterday)."
        else:
            summary = f"Your Sleep Score is {today_sleep} and Skin Health Score is {today_skin}."
        
        # Enhanced insights and recommendations
        insights = self._generate_enhanced_insights(today_data)
        recommendations = self._generate_enhanced_recommendations(today_data)
        
        return DailySummary(
            daily_summary=summary,
            sleep_score_change=today_sleep - yesterday_data.get('sleep_score', 0) if yesterday_data else None,
            skin_health_change=today_skin - yesterday_data.get('skin_health_score', 0) if yesterday_data else None,
            key_insights=insights,
            recommendations=recommendations
        )
    
    def _generate_enhanced_insights(self, data: Dict) -> List[str]:
        """Generate more specific and actionable insights for ALL 6 features"""
        insights = []
        features = data.get('features', {})
        
        # Dark Circles Analysis
        dark_circles = features.get('dark_circles', 0)
        if dark_circles < -60:
            insights.append("Severe dark circles detected - this suggests significant sleep debt or dehydration")
        elif dark_circles < -30:
            insights.append("Moderate dark circles visible - consider earlier bedtime and eye care routine")
        elif dark_circles > 30:
            insights.append("Eyes look bright and rested - your sleep routine is working well!")
        
        # Puffiness Analysis
        puffiness = features.get('puffiness', 0)
        if puffiness < -60:
            insights.append("Significant eye puffiness detected - try sleeping with head elevated and reduce salt intake")
        elif puffiness < -30:
            insights.append("Mild puffiness around eyes - consider cold compress and better hydration")
        elif puffiness > 30:
            insights.append("Your eyes show excellent definition - great circulation and rest!")
        
        # Brightness Analysis
        brightness = features.get('brightness', 0)
        if brightness < -60:
            insights.append("Skin appears very dull - increase water intake and consider vitamin C serum")
        elif brightness < -30:
            insights.append("Skin could use more radiance - try gentle exfoliation and hydrating mask")
        elif brightness > 40:
            insights.append("Your skin has a beautiful, healthy glow today!")
        
        # Wrinkles Analysis
        wrinkles = features.get('wrinkles', 0)
        if wrinkles < -60:
            insights.append("Fine lines are quite visible - consider retinol treatment and better moisturizing")
        elif wrinkles < -30:
            insights.append("Some fine lines detected - maintain hydration and consider anti-aging skincare")
        elif wrinkles > 40:
            insights.append("Your skin looks remarkably smooth and youthful!")
        
        # Texture Analysis
        texture = features.get('texture', 0)
        if texture < -60:
            insights.append("Skin texture appears rough - try gentle exfoliation and intensive moisturizing")
        elif texture < -30:
            insights.append("Skin texture could be smoother - focus on hydration and gentle care")
        elif texture > 40:
            insights.append("Your skin texture is beautifully smooth and even!")
        
        # Pore Size Analysis
        pore_size = features.get('pore_size', 0)
        if pore_size < -60:
            insights.append("Pores appear enlarged - try salicylic acid and pore-minimizing treatments")
        elif pore_size < -30:
            insights.append("Pores are somewhat visible - consider regular exfoliation and clay masks")
        elif pore_size > 40:
            insights.append("Your pores look beautifully refined and minimal!")
        
        # Cross-feature Pattern Analysis
        sleep_indicators = [dark_circles, puffiness, brightness]
        if all(score < -40 for score in sleep_indicators):
            insights.append("Multiple indicators suggest poor sleep quality - prioritize sleep hygiene tonight")
        
        skin_indicators = [brightness, wrinkles, texture, pore_size]
        if all(score > 30 for score in skin_indicators):
            insights.append("All skin health indicators are excellent - your routine is working perfectly!")
        elif all(score < -30 for score in skin_indicators):
            insights.append("Multiple skin concerns detected - consider comprehensive skincare routine overhaul")
        
        return insights
    
    def _generate_enhanced_recommendations(self, data: Dict) -> List[str]:
        """Generate prioritized, specific recommendations for ALL features"""
        recommendations = []
        features = data.get('features', {})
        routine = data.get('routine', {})
        
        # Prioritized recommendation system for all 6 features
        urgent_recs = self._get_urgent_recommendations_all_features(features)
        daily_recs = self._get_daily_recommendations_all_features(features, routine)
        preventive_recs = self._get_preventive_recommendations_all_features(features, routine)
        
        # Combine and prioritize
        all_recs = urgent_recs + daily_recs + preventive_recs
        return all_recs[:8]  # Limit to top 8 most relevant
    
    def _get_urgent_recommendations_all_features(self, features: Dict) -> List[str]:
        """Immediate action recommendations for all features"""
        urgent = []
        
        # Dark Circles
        if features.get('dark_circles', 0) < -60:
            urgent.append("URGENT: Apply cold eye compress for 10 minutes to reduce severe dark circles")
        
        # Puffiness
        if features.get('puffiness', 0) < -60:
            urgent.append("URGENT: Elevate your head while sleeping tonight to reduce severe puffiness")
        
        # Brightness
        if features.get('brightness', 0) < -60:
            urgent.append("URGENT: Drink 2 glasses of water now and apply hydrating serum for dull skin")
        
        # Wrinkles
        if features.get('wrinkles', 0) < -60:
            urgent.append("URGENT: Apply intensive moisturizer and consider retinol treatment tonight")
        
        # Texture
        if features.get('texture', 0) < -60:
            urgent.append("URGENT: Use gentle exfoliating mask tonight and intensive moisturizer")
        
        # Pore Size
        if features.get('pore_size', 0) < -60:
            urgent.append("URGENT: Apply clay mask this evening to address enlarged pores")
        
        return urgent
    
    def _get_daily_recommendations_all_features(self, features: Dict, routine: Dict) -> List[str]:
        """Daily routine recommendations for all features"""
        daily = []
        
        # Dark Circles recommendations
        dark_circles = features.get('dark_circles', 0)
        if dark_circles < -30:
            daily.append("Use caffeine eye cream morning and night")
            if routine.get('sleep_hours', 8) < 7:
                daily.append("Aim for 7-8 hours of sleep tonight for dark circle recovery")
        
        # Puffiness recommendations
        puffiness = features.get('puffiness', 0)
        if puffiness < -30:
            daily.append("Sleep with an extra pillow to keep head elevated")
            daily.append("Reduce sodium intake today to minimize puffiness")
        
        # Brightness recommendations
        brightness = features.get('brightness', 0)
        if brightness < -30:
            daily.append("Apply vitamin C serum this morning for skin radiance")
            daily.append("Use a hydrating face mask tonight")
            if routine.get('water_intake', 8) < 6:
                daily.append("Increase water intake to 8+ glasses today")
        
        # Wrinkles recommendations
        wrinkles = features.get('wrinkles', 0)
        if wrinkles < -30:
            daily.append("Apply anti-aging serum with peptides or retinol")
            daily.append("Use a rich moisturizer morning and night")
        
        # Texture recommendations
        texture = features.get('texture', 0)
        if texture < -30:
            daily.append("Gentle exfoliation 2-3 times this week")
            daily.append("Use hyaluronic acid serum for smoother texture")
        
        # Pore size recommendations
        pore_size = features.get('pore_size', 0)
        if pore_size < -30:
            daily.append("Use salicylic acid cleanser to minimize pore appearance")
            daily.append("Apply niacinamide serum to refine pores")
        
        return daily
    
    def _get_preventive_recommendations_all_features(self, features: Dict, routine: Dict) -> List[str]:
        """Preventive care recommendations for all features"""
        preventive = []
        
        # General preventive care based on overall scores
        avg_score = np.mean([features.get(f, 0) for f in ['dark_circles', 'puffiness', 'brightness', 'wrinkles', 'texture', 'pore_size']])
        
        if avg_score < -20:
            preventive.append("Consider comprehensive skincare routine review")
            preventive.append("Schedule earlier bedtime for overall skin recovery")
        
        # Feature-specific preventive care
        if features.get('brightness', 0) > 20 and features.get('texture', 0) > 20:
            preventive.append("Maintain current excellent routine - your skin looks great!")
        
        if features.get('wrinkles', 0) > 20:
            preventive.append("Continue current anti-aging routine - it's working well")
        
        if features.get('pore_size', 0) > 20:
            preventive.append("Keep up the pore care routine - pores look refined")
        
        # Lifestyle preventive recommendations
        if routine.get('skincare_products'):
            products = routine.get('skincare_products', [])
            if 'sunscreen' not in str(products).lower():
                preventive.append("Add daily sunscreen to prevent future skin damage")
        
        return preventive
    
    async def generate_weekly_summary(self, week_data: List[Dict]) -> WeeklySummary:
        """Generate weekly summary"""
        if not week_data:
            return WeeklySummary(
                weekly_summary="No data available for this week.",
                average_sleep_score=0,
                average_skin_health_score=0,
                score_trend="stable"
            )
        
        # Calculate averages
        sleep_scores = [day.get('sleep_score', 0) for day in week_data]
        skin_scores = [day.get('skin_health_score', 0) for day in week_data]
        
        avg_sleep = np.mean(sleep_scores)
        avg_skin = np.mean(skin_scores)
        
        # Calculate trend
        if len(sleep_scores) >= 2:
            trend = "improving" if sleep_scores[-1] > sleep_scores[0] else "declining" if sleep_scores[-1] < sleep_scores[0] else "stable"
        else:
            trend = "stable"
        
        # Generate summary
        summary = f"This week your average Sleep Score was {avg_sleep:.1f} and Skin Health Score was {avg_skin:.1f}. "
        summary += f"Your scores are {trend} this week."
        
        # Add lifestyle insights
        lifestyle_insights = []
        if avg_sleep > 70:
            lifestyle_insights.append("Great sleep habits this week!")
        if avg_skin > 70:
            lifestyle_insights.append("Your skin care routine is working well")
        
        return WeeklySummary(
            weekly_summary=summary,
            average_sleep_score=avg_sleep,
            average_skin_health_score=avg_skin,
            score_trend=trend,
            lifestyle_insights=lifestyle_insights,
            routine_effectiveness=[]
        )
