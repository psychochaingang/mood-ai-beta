from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse, PushMatrix, PopMatrix, Rotate
import cv2
import mediapipe as mp
from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions, RunningMode
from mediapipe.tasks.python import BaseOptions
import numpy as np
import json
import os
import time
import random
import math
import threading

# --- CONFIG ---
TRIAL_FILE = "app_trial.json"
MAX_TRIALS = 5

def get_trial():
    if os.path.exists(TRIAL_FILE):
        with open(TRIAL_FILE) as f: return json.load(f)
    return {"uses":0,"purchased":False,"calibrated":False,"age_mode":"kid","stickers":[]}

def save_trial(d):
    with open(TRIAL_FILE,"w") as f: json.dump(d,f)

trial_data = get_trial()

# MediaPipe setup
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="face_landmarker.task"),
    running_mode=RunningMode.VIDEO,
    output_face_blendshapes=True)
face_landmarker = FaceLandmarker.create_from_options(options)

# Load calibration
calib = {}
if trial_data.get("calibrated") and os.path.exists("mood_calib.json"):
    with open("mood_calib.json") as f: calib = json.load(f)

# Mood data
mood_names = {"Neutral":"Chillin","Happy":"Happy!","Sad":"Sad","Angry":"Angry!",
    "Surprised":"Whoa!","Disgusted":"Eww!","Fearful":"Scared!","Tired":"Zzz"}
mood_emojis = {"Neutral":"(-_-)","Happy":"(^-^)","Sad":"(;_;)","Angry":">_<",
    "Surprised":"(O_O)","Disgusted":"(-_-#)","Fearful":"(D_D)","Tired":"(u_u)"}

kid_jokes = {"Neutral":["Hey there!","Thinking?"],"Happy":["Great smile!","You're glowing!"],
    "Sad":["Aww, hug?","Feel better cutie!"],"Angry":["Take a breath!","Calm down buddy!"],
    "Surprised":["Whoa!","Woah!"],"Disgusted":["Eww!","Yucky!"],
    "Fearful":["It's ok!","I'm here!"],"Tired":["Nap time!","So sleepy!"]}
adult_jokes = {"Neutral":["Default settings","Buffering?"],"Happy":["You got away with it","That smile means trouble"],
    "Sad":["Life's rough huh","Tax bill?"],"Angry":["Rage quit?","Step on Lego?"],
    "Surprised":["Code compiled?","Forgot password?"],"Disgusted":["Microtransactions","This is fine?"],
    "Fearful":["Boss behind you?","DB deleted?"],"Tired":["Coffee hasn't hit","Up all night?"]}

def compare_face(cur, ref):
    score=0; w=0
    cues={"mouthSmileLeft":1,"mouthSmileRight":1,"mouthFrownLeft":1.5,"mouthFrownRight":1.5,
        "browDownLeft":2,"browDownRight":2,"browInnerUp":1.5,"jawOpen":1.5,
        "eyeWideLeft":1,"eyeWideRight":1,"noseWrinkleLeft":3,"noseWrinkleRight":3,
        "lipPress":2.5,"lipUpperUp":2,"lipLowerDown":1.5,"cheekSquintLeft":1,"cheekSquintRight":1,"jawForward":2.5}
    for cue, wgt in cues.items():
        cv=cur.get(cue,0); rv=ref.get(cue,0)
        score+=(1.0-abs(cv-rv))*wgt; w+=wgt
    return score/max(w,1)

# --- CAMERA PROCESSING ---
class CameraProcessor:
    def __init__(self):
        self.cap = None
        self.frame = None
        self.running = False
        self.ts = 0
    
    def start(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.running = True
    
    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def get_processed(self):
        if not self.running or self.cap is None:
            return None, None
        ret, frame = self.cap.read()
        if not ret: return None, None
        self.ts += 1
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = face_landmarker.detect_for_video(mp_img, self.ts)
        
        mood = "Neutral"; scores = {}
        if result.face_blendshapes and calib:
            cur = {c.category_name: c.score for c in result.face_blendshapes[0]}
            scores = {e: compare_face(cur, ref) for e, ref in calib.items()}
            mood = max(scores, key=scores.get)
        
        # Draw on frame
        if result.face_landmarks:
            lm = result.face_landmarks[0]
            h, w = frame.shape[:2]
            for i in [1,4,5,6,7,8,9,10]:
                x = int(lm[i].x * w)
                y = int(lm[i].y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)
        
        mood_history = getattr(self, "mood_history", None)
        if mood_history is None:
            self.mood_history = ["Neutral"]*10
            mood_history = self.mood_history
        mood_history.append(mood)
        mood_history.pop(0)
        mood = max(set(mood_history), key=mood_history.count)
        
        return frame, (mood, scores)

# --- SCREENS ---
cam_proc = CameraProcessor()

class CamScreen(Screen):
    def on_enter(self):
        cam_proc.start()
        Clock.schedule_interval(self.update, 1/30)
    
    def on_leave(self):
        Clock.unschedule(self.update)
    
    def update(self, dt):
        pass  # Override in subclasses

class PermScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_widget(Label(text="[b]CAMERA REQUIRED[/b]\n\nMood AI needs camera\nto read your expressions",
            markup=True, font_size=22, halign="center", pos_hint={"center_x":0.5,"center_y":0.65}))
        btn = Button(text="ALLOW", size_hint=(0.5,0.1), pos_hint={"center_x":0.5,"center_y":0.35},
                    background_color=(0.2,0.8,0.2,1))
        btn.bind(on_press=lambda x: setattr(self.manager, "current", "age"))
        self.add_widget(btn)

class AgeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_widget(Label(text="[b]WELCOME![/b]\nEnter your age:",markup=True,
            font_size=22,pos_hint={"center_x":0.5,"center_y":0.7}))
        self.input = TextInput(hint_text="Your age", multiline=False, input_filter="int",
            size_hint=(0.5,0.08), pos_hint={"center_x":0.5,"center_y":0.5})
        self.add_widget(self.input)
        btn = Button(text="GO", size_hint=(0.3,0.08), pos_hint={"center_x":0.5,"center_y":0.35},
                    background_color=(1,0.8,0.2,1), color=(0,0,0,1))
        btn.bind(on_press=self.confirm)
        self.add_widget(btn)
    
    def confirm(self, btn):
        if self.input.text:
            age = int(self.input.text)
            trial_data["age_mode"] = "kid" if age < 18 else "adult"
            save_trial(trial_data)
            if trial_data.get("calibrated"):
                self.manager.current = "main"
            else:
                self.manager.current = "calibrate"

class CalibrateScreen(CamScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.expressions = ["Neutral","Happy","Sad","Angry","Disgusted","Surprised","Tired"]
        self.current_expr = 0; self.captured = {}; self.samples = []
        self.capture_count = 0; self.capturing = False; self.countdown = 0
        self.img = Image()
        self.add_widget(self.img)
        self.lbl = Label(text="", font_size=18, pos_hint={"center_x":0.5,"center_y":0.9})
        self.add_widget(self.lbl)
        self.prog = Label(text="", font_size=14, pos_hint={"center_x":0.5,"center_y":0.05})
        self.add_widget(self.prog)
    
    def update(self, dt):
        frame, mood_data = cam_proc.get_processed()
        if frame is None: return
        buf = cv2.flip(frame, 0).tobytes()
        tex = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        tex.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img.texture = tex
        
        expr = self.expressions[self.current_expr]
        done = len([e for e in self.expressions if e in self.captured])
        self.prog.text = f"{' | '.join(['OK' if e in self.captured else e.upper() if e==expr else e for e in self.expressions])}"
        
        if self.capturing:
            self.countdown -= 1
            if self.countdown <= 0 and cam_proc.ts > 0:
                result = face_landmarker.detect_for_video(
                    mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)),
                    cam_proc.ts)
                if result.face_blendshapes:
                    data = {c.category_name: c.score for c in result.face_blendshapes[0]}
                    self.samples.append(data)
                    # Simplified - need proper data collection
                    self.capture_count += 1
                    self.countdown = 15
                    if self.capture_count >= 10:
                        self.captured[expr] = {"done":True}
                        self.capturing = False; self.capture_count = 0; self.samples = []
                        if self.current_expr < len(self.expressions)-1:
                            self.current_expr += 1
                        else:
                            json.dump(self.captured, open("mood_calib.json","w"))
                            trial_data["calibrated"] = True; save_trial(trial_data)
                            self.manager.current = "main"
            self.lbl.text = f"Hold '{expr}'... {self.capture_count+1}/10"
        else:
            self.lbl.text = f"Make '{expr}' face\nTap screen"

    def on_touch_down(self, touch):
        if not self.capturing:
            self.capturing = True; self.countdown = 30; self.capture_count = 0; self.samples = []

class MainScreen(CamScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.img = Image()
        self.add_widget(self.img)
        self.mood_lbl = Label(text="", font_size=18, pos_hint={"center_x":0.5,"center_y":0.85})
        self.add_widget(self.mood_lbl)
        self.joke_lbl = Label(text="", font_size=14, pos_hint={"center_x":0.5,"center_y":0.08})
        self.add_widget(self.joke_lbl)
        self.last_mood = "Neutral"
        self.uses = trial_data["uses"]
    
    def update(self, dt):
        if trial_data["uses"] >= MAX_TRIALS and not trial_data["purchased"]:
            self.manager.current = "paywall"
            return
        
        frame, mood_data = cam_proc.get_processed()
        if frame is None: return
        buf = cv2.flip(frame, 0).tobytes()
        tex = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        tex.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img.texture = tex
        
        if mood_data:
            mood, scores = mood_data
            if mood != self.last_mood:
                self.last_mood = mood
                jokes = kid_jokes if trial_data["age_mode"]=="kid" else adult_jokes
                self.joke_lbl.text = random.choice(jokes.get(mood,[""]))
                trial_data["uses"] += 1; save_trial(trial_data)
            
            emoji = mood_emojis.get(mood,"(-_-)")
            self.mood_lbl.text = f"{emoji}  {mood_names.get(mood,mood)}"

class PaywallScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_widget(Label(text="[b]TRIAL OVER[/b]\n\nThanks for playing!\n\nUnlock Mood AI for $2",
            markup=True, font_size=20, pos_hint={"center_x":0.5,"center_y":0.6}))
        btn = Button(text="UNLOCK - $2", size_hint=(0.5,0.1), pos_hint={"center_x":0.5,"center_y":0.35},
                    background_color=(1,0.8,0.2,1), color=(0,0,0,1))
        btn.bind(on_press=lambda x: unlock())
        self.add_widget(btn)
        self.add_widget(Label(text="Coming to Google Play Store", font_size=12,
            pos_hint={"center_x":0.5,"center_y":0.15}))

def unlock():
    trial_data["purchased"] = True; save_trial(trial_data)

class MoodAIApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PermScreen(name="perm"))
        sm.add_widget(AgeScreen(name="age"))
        sm.add_widget(CalibrateScreen(name="calibrate"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(PaywallScreen(name="paywall"))
        return sm
    
    def on_stop(self):
        cam_proc.stop()

if __name__ == "__main__":
    MoodAIApp().run()
