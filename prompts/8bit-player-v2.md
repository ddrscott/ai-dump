# Prompt

I need a javascript function that can set an Audio API oscilloscope to a musical note.
The note is represented by a string.
An example of some notes are: C4, A4, G#5.

The parameters of the function should have a signature: (track, oscilloscope, bpm, audioContext)

I need a single html file for the response:

AI:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>8-bit Player</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <textarea id="notes" rows="10" cols="50">C D E F G A B C</textarea>
    <br>
    <button id="playButton">Play</button>
    <label for="pauseCheckbox">Pause</label>
    <input type="checkbox" id="pauseCheckbox">
    <script>

const playButton = document.getElementById('playButton');
const notesTextarea = document.getElementById('notes');
const pauseCheckbox = document.getElementById('pauseCheckbox');

playButton.addEventListener('click', () => {
  const audioContext = new AudioContext();
  const oscilloscope = audioContext.createOscillator();
  oscilloscope.connect(audioContext.destination);
  
  const bpm = 120;
  const parts = notesTextarea.value
      .trim()                       // remove whitespace
      .replaceAll(/\s*\|\s*/g," ")  // remove barlines
      .split('\n');                 // split into tracks
  
  const tracks = parts.map(track => {

    
    const duration = countGreaterThanSigns(note) + 1;
    const name = note.replace(/[^A-G0-8]/ig, '');
    
    return {note: name, duration: parseFloat(duration), decibel: 0.5};
  });
  
  console.log("notes:", notes);

  pauseCheckbox.addEventListener('change', () => {
    paused = !paused;
  });

  playTrack(notes, oscilloscope, bpm, audioContext);
});  

const NOTE_FREQUENCIES = {
  'C': 261.63,
  'C#': 277.18,
  'D': 293.66,
  'D#': 311.13,
  'E': 329.63,
  'F': 349.23,
  'F#': 369.99,
  'G': 392.00,
  'G#': 415.30,
  'A': 440.00,
  'A#': 466.16,
  'B': 493.88
};

let paused = false;

function playTrack(track, oscilloscope, bpm, audioContext) {
  const beatDuration = 60 / bpm;
  let currentTime = audioContext.currentTime;

  track.forEach(({note, duration, decibel}) => {
    const octave = parseInt(note[note.length - 1]);
    const noteName = note.slice(0, -1);
    console.log("noteName:", noteName);
    const frequency = NOTE_FREQUENCIES[noteName] * Math.pow(2, octave - 4);

    oscilloscope.frequency.value = frequency;
    oscilloscope.gain.value = decibel;

    if (!paused) {
      oscilloscope.start(currentTime);
      oscilloscope.stop(currentTime + beatDuration);
    } else {
      oscilloscope.stop(currentTime);
    }

    currentTime += beatDuration * (duration / beatDuration);
  });
}

function togglePause() {
  paused = !paused;
}

function countGreaterThanSigns(str) {
  const regex = />/g;
  const matches = str.match(regex);
  return matches ? matches.length : 0;
}  
    </script>
  </body>
</html>

```

```css
  body {
    margin: 0;
    padding: 0;
    background: #555;
    color: #CCC;
  }
```
