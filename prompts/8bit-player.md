# Prompt

I want to create 8-bit music using HTML Audio API.
The music should be fed in as a single string.
Each track of sound is represented on its own line.
Tracks are played in parallel.
An example sequence for Twinkle Twinkle Little Star would be.

```text
C C G G | A A G> F F E E D D C>
C . G . | . . C> F . E . D . C>
```

Notes are separated by whitespace.
Greater than means hold the note an extra beat.
Bar characters should be ignored from the input.
for the user to edit the file.

Each lines should be considered a unique instrument.

Can you make a javascript function that can interpret this data format and play audio
through an occiloscope?

## index.html
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>8-bit Music Generator</title>
  </head>
  <body>
    <script src="app2.js"></script>
    <button onclick="play()">Play</button>
  </body>
</html>
```

## app.js
```javascript
const NOTES = {
    'C': 261.63,
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88
};

function play8BitMusic(musicString) {
    const context = new AudioContext();
    const gainNode = context.createGain();
    gainNode.connect(context.destination);

    const tracks = musicString
        .trim()                       // remove whitespace
        .replaceAll(/\s*\|\s*/g," ")  // remove barlines
        .split('\n');                 // split into tracks

    tracks.forEach((track, _) => {
        const oscillator = context.createOscillator();
        oscillator.type = 'square';
        oscillator.frequency.value = 0;

        const gain = context.createGain();
        gain.gain.value = 0;

        let time = context.currentTime;

        track.split(' ').forEach(note => {
            const duration = note.includes('>') ? 2 : 1;
            const pitch = NOTES[note.replace(/[.>]/g, '')];
            const hold = note.includes('>') ? 1 : 0;

            console.log(note, duration, pitch, hold);

            oscillator.frequency.setValueAtTime(pitch, time);
            gain.gain.setValueAtTime(1, time);
            oscillator.frequency.setValueAtTime(0, time + duration - hold);
            gain.gain.setValueAtTime(0, time + duration - hold);

            time += duration;
            setTimeout(() => {
                oscillator.frequency.setValueAtTime(pitch, context.currentTime);
                gain.gain.setValueAtTime(1, context.currentTime);
                oscillator.frequency.setValueAtTime(0, context.currentTime + hold);
                gain.gain.setValueAtTime(0, context.currentTime + hold);
            }, time * 1000 - context.currentTime * 1000);
        });

        oscillator.connect(gain);
        gain.connect(gainNode);
        oscillator.start();
    });
}

function play() {
    play8BitMusic(
`C C G G | A A G> | F F E E | D D C>
 C . G . | . . C> | F . E . | D . C>`);
}
```
