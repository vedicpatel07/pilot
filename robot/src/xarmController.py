from typing import List, Tuple, Optional, Dict, Any
from xarm.wrapper import XArmAPI
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("XArmController")

class XArmController:
    """
    Controller class for xArm robot, providing high-level interface for common operations.
    """
    def __init__(self, ip: str, is_radian: bool = False):
        """
        Initialize xArm controller.
        
        Args:
            ip: IP address of the xArm
            is_radian: Whether to use radians (True) or degrees (False) for angles
        """
        self.arm = XArmAPI(ip, is_radian=is_radian)
        self.is_radian = is_radian
        self._setup_robot()
    
    def _set_custom_home(self) -> None:
        """Set custom home position for the robot."""
        joint_angles = [35.6, -27.5, -21.7, 50.9, 0.0]
        ret = self.arm.set_servo_angle(angle=joint_angles, wait=True)
        if ret == 0:
            logger.info("Custom home position set successfully")
        else:
            logger.error(f"Failed to set custom home position, error code: {ret}")
            
    def _setup_robot(self) -> None:
        """Initial robot setup and configuration."""
        self.arm.clean_warn()
        self.arm.clean_error()
        self.arm.motion_enable(True)
        self.arm.set_mode(0)  # Position control mode
        self.arm.set_state(state=0)  # Start state
        
        # Move to our defined "home" position
        self._set_custom_home()
        logger.info("Robot initialized and moved to home position")
    
    def connect(self) -> bool:
        """
        Connect to the robot.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.arm.connect()
            if self.arm.connected:
                logger.info("Successfully connected to xArm")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to connect to xArm: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the robot."""
        try:
            self.arm.disconnect()
            logger.info("Disconnected from xArm")
        except Exception as e:
            logger.error(f"Error disconnecting from xArm: {str(e)}")

    def get_position(self) -> Tuple[int, List[float]]:
        """
        Get current position of the robot.
        
        Returns:
            Tuple[int, List[float]]: (code, [x, y, z, roll, pitch, yaw])
        """
        return self.arm.get_position()

    def get_joint_angles(self) -> Tuple[int, List[float]]:
        """
        Get current joint angles.
        
        Returns:
            Tuple[int, List[float]]: (code, [angle1, angle2, ...])
        """
        return self.arm.get_servo_angle()

    def move_to_position(self, 
                        x: Optional[float] = None,
                        y: Optional[float] = None,
                        z: Optional[float] = None,
                        roll: Optional[float] = None,
                        pitch: Optional[float] = None,
                        yaw: Optional[float] = None,
                        speed: Optional[float] = None,
                        wait: bool = True,
                        timeout: Optional[float] = None) -> int:
        """
        Move robot to specified position.
        
        Args:
            x: X coordinate (mm)
            y: Y coordinate (mm)
            z: Z coordinate (mm)
            roll: Roll angle
            pitch: Pitch angle
            yaw: Yaw angle
            speed: Movement speed (mm/s)
            wait: Whether to wait for movement completion
            timeout: Maximum waiting time in seconds
            
        Returns:
            int: Error code
        """
        return self.arm.set_position(x=x, y=y, z=z,
                                   roll=roll, pitch=pitch, yaw=yaw,
                                   speed=speed, wait=wait, timeout=timeout)

    def move_joints(self, 
                   angles: List[float],
                   speed: Optional[float] = None,
                   wait: bool = True,
                   timeout: Optional[float] = None) -> int:
        """
        Move robot joints to specified angles.
        
        Args:
            angles: List of joint angles
            speed: Movement speed
            wait: Whether to wait for movement completion
            timeout: Maximum waiting time in seconds
            
        Returns:
            int: Error code
        """
        return self.arm.set_servo_angle(angle=angles, speed=speed, wait=wait, timeout=timeout)

    def emergency_stop(self) -> None:
        """Trigger emergency stop."""
        self.arm.emergency_stop()
        logger.warning("Emergency stop triggered")

    def check_errors(self) -> Tuple[int, list]:
        """
        Check for robot errors.
        
        Returns:
            Tuple[int, list]: (code, [error_code, warn_code])
        """
        return self.arm.get_err_warn_code()
    
    def clear_errors(self) -> None:
        """Clear robot errors and warnings."""
        self.arm.clean_error()
        self.arm.clean_warn()
        logger.info("Cleared errors and warnings")

    def home(self, speed: Optional[float] = None, wait: bool = True) -> int:
        """
        Move robot to home position.
        
        Args:
            speed: Movement speed
            wait: Whether to wait for movement completion
            
        Returns:
            int: Error code
        """
        return self.arm.move_gohome(speed=speed, wait=wait)

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive robot status.
        
        Returns:
            Dict containing robot state information
        """
        return {
            "position": self.arm.position,
            "connected": self.arm.connected,
            "state": self.arm.state,
            "mode": self.arm.mode,
            "angles": self.arm.angles,
            "error_code": self.arm.error_code,
            "warn_code": self.arm.warn_code,
        }

if __name__ == "__main__":
    # Example usage
    robot = XArmController("192.168.1.197", is_radian=False)
    if robot.connect():
        try:
            # Move to a position
            robot.move_to_position(x=300, y=0, z=150, roll=180, pitch=0, yaw=0, wait=True)
            
            # Get current position
            code, pos = robot.get_position()
            print(f"Current position: {pos}")
            
            # Move home
            robot.home(wait=True)
            
        finally:
            robot.disconnect()