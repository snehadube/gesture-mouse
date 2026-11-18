# Gesture Mouse – UML Diagrams (OOAD)

Ye diagrams Mermaid mein bane hain, GitHub par automatically render hote hain.

---

## 1. Use Case Diagram

```mermaid
flowchart LR
    U([User])
    subgraph SYS[Gesture Mouse System]
        UC1((Move Cursor))
        UC2((Left Click))
        UC3((Right Click))
        UC4((Scroll Down))
        UC5((Open Chrome))
        UC6((Open Notepad))
        UC7((Open Music Player))
        UC8((Close Window))
        UC9((View Instructions))
        UC10((Exit with ESC))
        UC11((Log Action))
    end
    U --- UC1
    U --- UC2
    U --- UC3
    U --- UC4
    U --- UC5
    U --- UC6
    U --- UC7
    U --- UC8
    U --- UC9
    U --- UC10
    UC2 -. include .-> UC11
    UC3 -. include .-> UC11
    UC4 -. include .-> UC11
    UC5 -. include .-> UC11
    UC6 -. include .-> UC11
    UC7 -. include .-> UC11
    UC8 -. include .-> UC11
```

---

## 2. Class Diagram

```mermaid
classDiagram
    class Config {
        +float COOLDOWN_TIME
        +int CLICK_DISTANCE_THRESHOLD
        +int SMOOTHENING
        +str LOG_FILE
    }
    class GestureMouseApp {
        -bool running
        +main()
        +run()
        +shutdown()
    }
    class InstructionsPopup {
        +show_instructions()
    }
    class HandTracker {
        -Hands hands
        +process(frame) landmarks
        +draw(frame, landmarks)
    }
    class GestureRecognizer {
        -float last_left_click
        -float last_right_click
        -float last_scroll
        +detect(landmarks) Gesture
        -is_pinch(p1, p2) bool
        -cooldown_ok(last) bool
    }
    class MouseController {
        -float prev_x
        -float prev_y
        +move(x, y)
        +left_click()
        +right_click()
        +scroll_down()
    }
    class VoiceCommandListener {
        -Recognizer recognizer
        -Microphone mic
        -TTSEngine engine
        +listen_voice()
        -execute(command)
    }
    class ActionLogger {
        +log_action(action)
    }

    GestureMouseApp --> InstructionsPopup : shows
    GestureMouseApp *-- HandTracker
    GestureMouseApp *-- GestureRecognizer
    GestureMouseApp *-- MouseController
    GestureMouseApp *-- VoiceCommandListener : runs in thread
    GestureRecognizer ..> Config : uses
    MouseController ..> Config : uses
    GestureRecognizer --> MouseController : triggers
    GestureRecognizer --> ActionLogger : logs
    VoiceCommandListener --> ActionLogger : logs
    ActionLogger ..> Config : LOG_FILE
```

---

## 3. Object Diagram

```mermaid
classDiagram
    class app["app : GestureMouseApp"] {
        running = true
    }
    class tracker["tracker : HandTracker"] {
        max_num_hands = 1
        min_detection_confidence = 0.7
    }
    class recognizer["recognizer : GestureRecognizer"] {
        last_left_click = 1731900000.2
        last_right_click = 0.0
        last_scroll = 0.0
    }
    class mouse["mouse : MouseController"] {
        prev_x = 640.0
        prev_y = 360.0
    }
    class voice["voice : VoiceCommandListener"] {
        language = en-IN
    }
    class logger["logger : ActionLogger"] {
        file = log.txt
    }
    app --> tracker
    app --> recognizer
    app --> mouse
    app --> voice
    recognizer --> logger
    voice --> logger
```

---

## 4. Sequence Diagram (Left Click via Gesture)

```mermaid
sequenceDiagram
    actor User
    participant Cam as Webcam
    participant App as GestureMouseApp
    participant HT as HandTracker
    participant GR as GestureRecognizer
    participant MC as MouseController
    participant LG as ActionLogger

    User->>Cam: Hand dikhata hai
    loop har frame
        App->>Cam: read frame
        Cam-->>App: image
        App->>HT: process(image)
        HT-->>App: hand landmarks
        App->>MC: move(index_finger_x, y)
        App->>GR: detect(landmarks)
        alt Index + Thumb distance < threshold AND cooldown ok
            GR->>MC: left_click()
            GR->>LG: log_action("Left click")
        end
        App->>App: imshow, check ESC
    end
    User->>App: ESC press
    App->>LG: log_action("Program exited")
    App->>Cam: release()
```

### Sequence Diagram (Voice Command)

```mermaid
sequenceDiagram
    actor User
    participant VL as VoiceCommandListener
    participant GAPI as Google Speech API
    participant OS as Operating System
    participant TTS as pyttsx3
    participant LG as ActionLogger

    User->>VL: "notepad" bolta hai
    VL->>GAPI: recognize_google(audio)
    GAPI-->>VL: "notepad"
    VL->>OS: Popen("notepad.exe")
    VL->>TTS: say("Opening Notepad")
    VL->>LG: log_action("Opened Notepad via voice")
```

---

## 5. Activity Diagram

```mermaid
flowchart TD
    A([Start]) --> B[Instructions popup dikhao 4 sec]
    B --> C[Voice thread start]
    B --> D[Webcam open karo]
    D --> E{Camera open?}
    E -- No --> X([Error + Exit])
    E -- Yes --> F[Frame read + flip]
    F --> G[MediaPipe se hand detect]
    G --> H{Hand mila?}
    H -- No --> N
    H -- Yes --> I[Index finger se cursor move - smoothing]
    I --> J{Index+Thumb pinch?}
    J -- Yes --> J1[Left click + log]
    J -- No --> K
    J1 --> K{Middle+Thumb pinch?}
    K -- Yes --> K1[Right click + log]
    K -- No --> L
    K1 --> L{Ring+Thumb pinch?}
    L -- Yes --> L1[Scroll down + log]
    L -- No --> N
    L1 --> N[Frame screen par dikhao]
    N --> O{ESC pressed?}
    O -- No --> F
    O -- Yes --> P[Log exit, camera release]
    P --> Q([End])

    C --> V1[Mic se suno]
    V1 --> V2{Command match?}
    V2 -- chrome/notepad/music/close --> V3[Action + voice reply + log]
    V2 -- no --> V1
    V3 --> V1
```

---

## 6. State Diagram (Gesture cooldown)

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Tracking : hand detected
    Tracking --> Idle : hand lost
    Tracking --> Clicked : pinch + cooldown ok
    Clicked --> Cooldown : action fired and logged
    Cooldown --> Tracking : 0.5 sec complete
    Tracking --> [*] : ESC
```

---

## 7. Component Diagram

```mermaid
flowchart LR
    subgraph APP[gesture_mouse.py]
        MAIN[Main Loop]
        GEST[Gesture Logic]
        VOICE[Voice Thread]
        LOG[Logger]
        GUI[Instructions Popup]
    end
    CV[OpenCV]
    MP[MediaPipe Hands]
    PAG[PyAutoGUI]
    SR[SpeechRecognition]
    TTS[pyttsx3]
    TK[Tkinter]
    NP[NumPy]
    FILE[(log.txt)]
    CAM[[Webcam]]
    MIC[[Microphone]]
    OS[[Windows OS]]

    CAM --> CV --> MAIN
    MAIN --> MP --> GEST
    GEST --> NP
    GEST --> PAG --> OS
    MIC --> SR --> VOICE
    VOICE --> TTS
    VOICE --> PAG
    VOICE --> OS
    GEST --> LOG
    VOICE --> LOG
    LOG --> FILE
    GUI --> TK
```

---

## 8. Deployment Diagram

```mermaid
flowchart TB
    subgraph PC[User's Windows PC]
        PY[Python 3.9-3.11 Runtime]
        SCRIPT[gesture_mouse.py]
        LOGF[(log.txt)]
        CAM[Webcam]
        MIC[Microphone]
        PY --- SCRIPT
        SCRIPT --> LOGF
        CAM --> SCRIPT
        MIC --> SCRIPT
    end
    CLOUD[(Google Speech API)]
    SCRIPT -- HTTPS --> CLOUD
```
