# Prompt
I want a simple webpage to show a piano keyboard with 3 octaves worth
of keys. The keys should be represented by dom elements. DO NOT USE CANVAS.
Below the keyboard add a log of all keys that have been pressed.
When a key is pressed play the note on an occilosope. When the user releases the key stop playing the sound.

Separate the html and javascript into separate files.

## index.html
```html
<!DOCTYPE html>
<html>
  <head>
    <title>Piano Keyboard</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <div id="keyboard">
      <div class="white-key" data-note="C3"></div>
      <div class="black-key" data-note="C#3"></div>
      <div class="white-key" data-note="D3"></div>
      <div class="black-key" data-note="D#3"></div>
      <div class="white-key" data-note="E3"></div>
      <div class="white-key" data-note="F3"></div>
      <div class="black-key" data-note="F#3"></div>
      <div class="white-key" data-note="G3"></div>
      <div class="black-key" data-note="G#3"></div>
      <div class="white-key" data-note="A3"></div>
      <div class="black-key" data-note="A#3"></div>
      <div class="white-key" data-note="B3"></div>
      <div class="white-key" data-note="C4"></div>
      <div class="black-key" data-note="C#4"></div>
      <div class="white-key" data-note="D4"></div>
      <div class="black-key" data-note="D#4"></div>
      <div class="white-key" data-note="E4"></div>
      <div class="white-key" data-note="F4"></div>
      <div class="black-key" data-note="F#4"></div>
      <div class="white-key" data-note="G4"></div>
      <div class="black-key" data-note="G#4"></div>
      <div class="white-key" data-note="A4"></div>
      <div class="black-key" data-note="A#4"></div>
      <div class="white-key" data-note="B4"></div>
      <div class="white-key" data-note="C5"></div>
      <div class="black-key" data-note="C#5"></div>
      <div class="white-key" data-note="D5"></div>
      <div class="black-key" data-note="D#5"></div>
      <div class="white-key" data-note="E5"></div>
      <div class="white-key" data-note="F5"></div>
      <div class="black-key" data-note="F#5"></div>
      <div class="white-key" data-note="G5"></div>
      <div class="black-key" data-note="G#5"></div>
      <div class="white-key" data-note="A5"></div>
      <div class="black-key" data-note="A#5"></div>
      <div class="white-key" data-note="B5"></div>
    </div>
    <div id="log"></div>
    <script src="script.js"></script>
  </body>
</html>
```

## style.css
```css
#keyboard {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 120px;
  background-color: #eee;
}

.white-key {
  width: 30px;
  height: 120px;
  border: 1px solid #000;
  background-color: #fff;
  margin-right: 2px;
}

.black-key {
  width: 20px;
  height: 80px;
  border: 1px solid #000;
  background-color: #000;
  margin-right: -10px;
  margin-left: -10px;
  z-index: 1;
}

#log {
  margin-top: 20px;
}
```

## app.js
```javascript
const keyboard = document.getElementById('keyboard');
const log = document.getElementById('log');
const audioCtx = new AudioContext();

const notes = {
  'C3': 130.81,
  'C#3': 138.59,
  'D3': 146.83,
  'D#3': 155.56,
  'E3': 164.81,
  'F3': 174.61,
  'F#3': 185.00,
  'G3': 196.00,
  'G#3': 207.65,
  'A3': 220.00,
  'A#3': 233.08,
  'B3': 246.94,
  'C4': 261.63,
  'C#4': 277.18,
  'D4': 293.66,
  'D#4': 311.13,
  'E4': 329.63,
  'F4': 349.23,
  'F#4': 369.99,
  'G4': 392.00,
  'G#4': 415.30,
  'A4': 440.00,
  'A#4': 466.16,
  'B4': 493.88,
  'C5': 523.25,
  'C#5': 554.37,
  'D5': 587.33,
  'D#5': 622.25,
  'E5': 659.25,
  'F5': 698.46,
  'F#5': 739.99,
  'G5': 783.99,
  'G#5': 830.61,
  'A5': 880.00,
  'A#5': 932.33,
  'B5': 987.77
};

const playNote = (note) => {
  const osc = audioCtx.createOscillator();
  osc.type = 'sine';
  osc.frequency.value = notes[note];
  osc.connect(audioCtx.destination);
  osc.start();
  return osc;
};

const stopNote = (osc) => {
  osc.stop();
  osc.disconnect();
};

const handleKeyDown = (event) => {
  const key = event.target;
  const note = key.dataset.note;
  const osc = playNote(note);
  key.classList.add('active');
  log.innerHTML += `${note} `;
  document.addEventListener('mouseup', () => {
    stopNote(osc);
    key.classList.remove('active');
  }, { once: true });
};

keyboard.addEventListener('mousedown', handleKeyDown);
```
