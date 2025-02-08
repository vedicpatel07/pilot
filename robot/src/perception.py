import pyrealsense2 as rs
import numpy as np
import cv2
import torch
from transformers import DetrImageProcessor, DetrForObjectDetection
from typing import List, Dict, Tuple, Optional
from PIL import Image

class CameraInterface:
    """Handles RealSense camera operations following Single Responsibility Principle"""
    def __init__(self, width: int = 640, height: int = 480, fps: int = 30):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
        self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        self.profile = self.pipeline.start(self.config)
        self.depth_scale = self.profile.get_device().first_depth_sensor().get_depth_scale()
        
        # Get camera intrinsics
        color_stream = self.profile.get_stream(rs.stream.color)
        self.intrinsics = color_stream.as_video_stream_profile().get_intrinsics()
        self.fx = self.intrinsics.fx
        self.fy = self.intrinsics.fy
        self.cx = self.intrinsics.ppx
        self.cy = self.intrinsics.ppy

    def get_frames(self) -> Tuple[np.ndarray, np.ndarray]:
        """Captures and returns the current color and depth frames"""
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        
        if not depth_frame or not color_frame:
            raise RuntimeError("Failed to capture frames from RealSense camera")
            
        return (
            np.asanyarray(color_frame.get_data()),
            np.asanyarray(depth_frame.get_data())
        )

    def calculate_3d_position(self, x: int, y: int, depth: float) -> Tuple[float, float, float]:
        """Converts 2D pixel coordinates and depth to 3D world coordinates"""
        Z = depth * self.depth_scale
        X = (x - self.cx) * Z / self.fx
        Y = (y - self.cy) * Z / self.fy
        return (X, Y, Z)

    def stop(self):
        """Stops the camera pipeline"""
        self.pipeline.stop()


class VLModel:
    """Handles visual language model operations using DETR"""
    def __init__(self, device: str = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
        # Initialize DETR model and processor
        self.processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        self.model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50").to(self.device)
        
        # Load COCO class mappings
        self.id2label = self.model.config.id2label
        self.score_threshold = 0.7

    def detect_objects(self, image: np.ndarray, text_prompt: str = None) -> List[Dict]:
        """
        Detects objects in the image using DETR
        
        Args:
            image: BGR image from camera
            text_prompt: Optional text prompt to filter detections (matches partial strings)
            
        Returns:
            List of detections with boxes and labels
        """
        # Convert BGR to RGB and then to PIL Image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Prepare image for model
        inputs = self.processor(images=pil_image, return_tensors="pt").to(self.device)
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Convert outputs to COCO API
        target_sizes = torch.tensor([pil_image.size[::-1]]).to(self.device)
        results = self.processor.post_process_object_detection(
            outputs, 
            target_sizes=target_sizes, 
            threshold=self.score_threshold
        )[0]
        
        # Process detections
        detections = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            box = box.cpu().numpy()
            label_str = self.id2label[label.item()]
            
            # Filter by text prompt if provided
            if text_prompt and text_prompt.lower() not in label_str.lower():
                continue
                
            detections.append({
                'label': label_str,
                'score': score.item(),
                'box': {
                    'xmin': float(box[0]),
                    'ymin': float(box[1]),
                    'xmax': float(box[2]),
                    'ymax': float(box[3])
                }
            })
            
        return detections


class ScenePerception:
    """Main class that combines camera and VLM functionality"""
    def __init__(self, enable_visualization: bool = False):
        self.camera = CameraInterface()
        self.vlm = VLModel()
        self.enable_visualization = enable_visualization
        self.current_objects = []

    def get_scene_objects(self, text_prompt: str = None) -> List[Dict]:
        """Returns all detected objects in the current scene"""
        color_image, depth_image = self.camera.get_frames()
        
        # Get detections
        detections = self.vlm.detect_objects(color_image, text_prompt)
        
        # Process detections
        objects = []
        for det in detections:
            box = det['box']
            x1, y1 = int(box['xmin']), int(box['ymin'])
            x2, y2 = int(box['xmax']), int(box['ymax'])
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Get 3D position
            position = self.camera.calculate_3d_position(
                center_x, center_y, depth_image[center_y, center_x]
            )
            
            objects.append({
                'label': det['label'],
                'score': det['score'],
                'position': position,
                'box': [x1, y1, x2, y2]
            })
        
        self.current_objects = objects
        
        if self.enable_visualization:
            self._visualize(color_image, depth_image, objects)
            
        return objects

    def find_object(self, target_label: str) -> Optional[Dict]:
        """Finds a specific object in the scene"""
        objects = self.get_scene_objects(text_prompt=target_label)
        if objects:
            # Return the highest confidence detection
            return max(objects, key=lambda x: x['score'])
        return None

    def _visualize(self, color_image: np.ndarray, depth_image: np.ndarray, 
                  objects: List[Dict]):
        """Visualizes detections and depth map"""
        # Create copies for visualization
        bbox_vis = color_image.copy()
        
        # Generate random colors for each object
        colors = [(np.random.randint(0, 255), 
                  np.random.randint(0, 255), 
                  np.random.randint(0, 255)) for _ in objects]
        
        for obj, color in zip(objects, colors):
            x1, y1, x2, y2 = map(int, obj['box'])
            
            # Draw bounding box
            cv2.rectangle(bbox_vis, (x1, y1), (x2, y2), color, 2)
            
            # Add labels
            label = f"{obj['label']} ({obj['score']:.2f})"
            pos = obj['position']
            coords = f"X:{pos[0]:.2f} Y:{pos[1]:.2f} Z:{pos[2]:.2f}"
            
            cv2.putText(bbox_vis, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.putText(bbox_vis, coords, (x1, y1 + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Create depth visualization with dots
        MIN_DEPTH = 0.3 * 1000  # 0.3 meters in mm
        MAX_DEPTH = 3.0 * 1000  # 3 meters in mm
        DOT_SPACING = 8  # Space between dots in pixels
        
        # Create black background
        h, w = depth_image.shape
        depth_vis = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Create dot mask
        y_coords, x_coords = np.meshgrid(range(h), range(w), indexing='ij')
        dot_mask = (y_coords % DOT_SPACING == 0) & (x_coords % DOT_SPACING == 0)
        
        # Get depth values at dot positions
        depths = np.clip(depth_image, MIN_DEPTH, MAX_DEPTH)
        
        # Create color mapping for valid depths
        for y in range(0, h, DOT_SPACING):
            for x in range(0, w, DOT_SPACING):
                if dot_mask[y, x]:
                    depth = depths[y, x]
                    # Normalize depth to 0-1 range
                    norm_depth = (depth - MIN_DEPTH) / (MAX_DEPTH - MIN_DEPTH)
                    
                    # Create color gradient: red (warm) to blue (cold)
                    if norm_depth < 0.5:
                        # Warm colors (red to yellow)
                        r = 255
                        g = int(norm_depth * 2 * 255)
                        b = 0
                    else:
                        # Cold colors (yellow to blue)
                        r = int((1 - norm_depth) * 2 * 255)
                        g = int((1 - norm_depth) * 2 * 255)
                        b = int((norm_depth - 0.5) * 2 * 255)
                    
                    # Draw colored dot
                    cv2.circle(depth_vis, (x, y), 1, (b, g, r), -1)
        
        # Show visualizations
        cv2.imshow("Object Detection", bbox_vis)
        cv2.imshow("Depth Map", depth_vis)
        cv2.waitKey(1)

    def stop(self):
        """Cleanup resources"""
        self.camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    perception = ScenePerception(enable_visualization=True)
    try:
        while True:
            objects = perception.get_scene_objects()
            if objects:
                print(f"Detected {len(objects)} objects:")
                for obj in objects:
                    print(f"- {obj['label']} (confidence: {obj['score']:.2f})")
            
    except KeyboardInterrupt:
        perception.stop()