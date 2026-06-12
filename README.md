# Bugs Hunt 🐛

A fast-paced bug-shooting game built with Pygame. Survive 3 minutes, rack up points, and don't shoot the wrong bugs.

## Running from Source

**Requirements:** Python 3.12+

```bash
pip install -r requirements.txt
python main.py
```

## Downloads

Pre-built executables for Windows, Linux, and macOS are available on the [Releases](../../releases) page.

## Controls

| Input | Action |
|---|---|
| G | Start the game |
| Esc | Quit |
| Left Click | Fire |
| Right Click | Reload |
| Scroll Up | Switch to pistol |
| Scroll Down | Switch to shotgun |
| F | Flashbang |
| P | Flashbang (no sound) |
| H | Reset score |
| M | Toggle display mode |
| N | Set timer to 00:00 |
| F11 | Toggle fullscreen |

## Scoring

Each bug has different point values — some are worth shooting, others will cost you.

| Bug | Points |
|---|---|
| Devil Ant | +10 / +20 (triggers flashbang!) |
| Jump Bug | +3 |
| Green Bug | +3 |
| Red Ant | +2 |
| Mosquito | +2 |
| Bee | +2 |
| Butterfly | −2 |
| Black Bug | −3 |
| Dragonfly | −3 |

Score cannot go below 0.

## Weapons

Switch weapons with the scroll wheel (unlocked after 30 seconds).

**Pistol** — 6 rounds, precise single shot, 2s reload

**Shotgun** — 2 rounds, wide spread, 1.5s reload
