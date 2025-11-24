## Inspiration 🐻

We all see the same pattern in young children: a need to guide pronunciation and expansion of vocabulary for young, developing minds. In today's world every solution involves more screen time. 

This creates a frustrating paradox for parents who want to support language development while limiting device exposure. The stakes are real. Ages 3-8 represent a critical window for speech development. Children's brains are incredibly plastic during this period, forming neural pathways for language at a rate they'll never experience again. Pronunciation habits formed now stick with them. But this is also exactly when we should be minimizing screens, not adding more. Parents want to help, but they're not speech therapists. They don't always know if pronunciations are correct or how to guide improvement. Even with good intentions, tracking consistent progress is hard when juggling everything else. We wanted to create something that gives kids the immediate feedback of educational technology, but in a form they already love and seek comfort in: a teddy bear.

## What It Does

Bear With Me is a screenless pronunciation learning system built around a physical teddy bear companion. A child speaks a target word to the teddy bear. The bear listens, processes the pronunciation, and responds with encouraging feedback through its speaker in a warm, natural voice. "Great job with 'butterfly'!" or "Let's try 'Banana' one more time together." All iterations of practice flow to a parent dashboard where parents can view their child's learning journey. Which words are they mastering? Which sounds need work? How many days have they practiced? All those questions are answered in the visibility of an app, but the child’s learning happens entirely offline with a cuddly companion.

## How We Built It 🛠️

**Hardware:** Raspberry Pi connected to a sound sensor that detects when a child starts speaking. A Logitech webcam microphone captures surrounding audio and a speaker connected to the Pi outputs the bear's prompts and associated feedback. 

**Backend:** Python Flask server receives audio from the Pi and calls ElevenLabs and Azure's Pronunciation Assessment API. This provides accuracy scores and phoneme-level feedback on which specific sounds the child struggled with. We convert feedback to natural speech using ElevenLabs' voice synthesis to create a consistent, warm teddy bear voice.

**Frontend:** React dashboard with local storage. Parents see quick overview metrics (streak, words mastered, today's practice) then can drill into detailed analytics such as practice heatmaps, accuracy trends over time, and words needing attention.
