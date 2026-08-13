from core.base_exercise import BaseExercise

class LungeDetector(BaseExercise):
    DOWN_THRESHOLD=90
    UP_THRESHOLD=160
    MIN_VISIBILITY=0.7
    HIP_SAG_TOLERANCE=0.1
    BALANCE_TOLERANCE=0.1

    LEFT_SHOULDER=11
    LEFT_ELBOW=13
    LEFT_WRIST=15
    RIGHT_SHOULDER=12
    RIGHT_ELBOW=14
    RIGHT_WRIST=16
    LEFT_HIP=23
    RIGHT_HIP=24
    LEFT_ANKLE=27
    RIGHT_ANKLE=28

    def __init__(self):
        super().__init__()

    def reset(self) -> None:
        self.reps=0
        self.stage=None

    def process(self,landmarks) -> dict:

        left_hip = self.get_point(landmarks, self.LEFT_HIP)
        left_knee = self.get_point(landmarks, self.LEFT_KNEE)
        left_ankle = self.get_point(landmarks, self.LEFT_ANKLE)
        left_knee_angle=self.calculate_angle(
            left_hip,
            left_knee,
            left_ankle
        )

        right_knee_angle=self.calculate_angle(
            self.get_point(landmarks,self.RIGHT_HIP),
            self.get_point(landmarks,self.RIGHT_KNEE),
            self.get_point(landmarks,self.RIGHT_ANKLE)
        )

        if left_knee_angle <= right_knee_angle:
            front_knee_angle = left_knee_angle
            front_knee_idx = self.LEFT_KNEE
            front_hip_idx = self.LEFT_HIP
            front_ankle_idx = self.LEFT_ANKLE
            shoulder_idx_for_torso=self.LEFT_SHOULDER
        else:
            front_knee_angle = right_knee_angle
            front_knee_idx = self.RIGHT_KNEE
            front_hip_idx = self.RIGHT_HIP
            front_ankle_idx = self.RIGHT_ANKLE
            shoulder_idx_for_torso=self.RIGHT_SHOULDER

        key_landmarks_visibility=landmarks[front_hip_idx].visibility > self.MIN_VISIBILITY and landmarks[front_knee_idx].visibility > self.MIN_VISIBILITY and landmarks[front_ankle_idx].visibility > self.MIN_VISIBILITY


        if key_landmarks_visibility:
            if front_knee_angle < self.DOWN_THRESHOLD:
                self.stage="DOWN"

            if front_knee_angle > self. UP_THRESHOLD and self.stage=="DOWN":
                self.stage="UP"
                self.reps+=1


        torso_angle=self.calculate_angle(
            self.get_point(landmarks,shoulder_idx_for_torso),
            self.get_point(landmarks,front_hip_idx),
            self.get_point(landmarks,front_ankle_idx)
        )
        shoulder_mid_x =(landmarks[self.LEFT_SHOULDER].x + landmarks[self.RIGHT_SHOULDER].x) / 2
        hip_mid_x=(landmarks[self.LEFT_HIP].x + landmarks[self.RIGHT_HIP].x) / 2
        lateral_offset =abs(shoulder_mid_x-hip_mid_x)

        if lateral_offset <= self.BALANCE_TOLERANCE:
            balance_status="BALANCED"
        else:
            balance_status="UNBALANCED"


        return {
            "reps": self.reps,
            
            "front_knee_angle": int(front_knee_angle),
            "torso_angle": int(torso_angle),
            "balance_status": balance_status
        }


