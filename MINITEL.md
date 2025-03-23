# Minitel "La Radiotechnique" (1985)

This is some experiments I've done to understand how to interface with my Minitel terminal. I've found some interesting control codes and symbols that I'll document here.

Leter I found the minitel-radiotechnique.pdf document that confirm some of my findings and probably contains more information (I've read some of it but not all make sense / works yet).

#### 1. Standard ASCII Control Codes (\x00 - \x1F)
Some of these codes follow standard ASCII behavior, while others have Minitel-specific effects.

\x07 → 🔊 Beep (BELL)
\x08 → ⬅️ Move cursor left (backspace without deleting)
\x09 → ➡️ Move cursor right (tab of 1 space)
\x0A → ⬇️ Move cursor down (Line Feed)
\x0B → ⬆️ Move cursor up
\x0C → 🧹 Clear screen (Form Feed, alternative to ESC =)
\x0D → ⬅️ Move cursor to the beginning of the current line (Carriage Return)
\x0E → 🎨 Possibly activates graphics mode (needs more testing)
\x0F → ❌ No effect found
\x10 → ❌ No effect found
\x11 → ✨ Enable blinking cursor (needs confirmation)
\x12 → 🔁 Repeat last character N times (A=1, B=2, etc.)
\x13 → ❓ Unknown effect but something happens
\x14 → ✨ Disable blinking cursor (needs confirmation)


#### 2. ESC (\x1B) Text Style Commands
We discovered a system for text opacity and formatting.

🔹 Text Opacity (or color but this minitel is black/white)
\x1BA → 25% opacity
\x1BB → 50% opacity
\x1BC → 100% opacity (normal text)
\x1BD → 10% opacity (almost invisible)
\x1BE → 30% opacity
\x1BF → 95% opacity
🔹 Blinking Text
\x1BH → ✨ Enable text blinking
\x1BI → ❌ Disable text blinking
🔹 Text Size
\x1BL → 🔤 Reset to normal size
\x1BM → 🔠 Increase height of text
\x1BN → 🔡 Increase width of text
\x1BO → 🔠🔡 Increase both width & height (double size)
🔹 Background Color
\x1B] → ⚪ Switch background to white
\x1B\ → ⚫ Reset background to normal

#### 3. ESC (\xFF) Symbols
\xFB → Left vertical line (used for drawing boxes)
\xFC → Center vertical line (used for drawing boxes)
\xFD → Right vertical line (used for drawing boxes)
\xFD → Top horizontal line (used for drawing boxes)
\xFF → 📦 Box symbol (used for drawing boxes)

#### 4. Positioning
\x1FAB A=1 (row) B=2 (col) → Move cursor to position (A, B)