<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/badge/Zero_Deps-✅-success?style=for-the-badge" alt="Zero Deps"/>
  <img src="https://img.shields.io/badge/Terminal-🎮-informational?style=for-the-badge" alt="Terminal Game"/>
</p>

<h1 align="center">🦕 dino</h1>

<p align="center">
  <strong>The Chrome Dinosaur Game, reborn in your terminal.</strong>
</p>

<p align="center">
  Jump over cacti. Duck under pterodactyls. Chase your high score.<br/>
  Pure Python. Zero dependencies. Just <code>python dino.py</code> and play.
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-install">Install</a> •
  <a href="#-controls">Controls</a> •
  <a href="#-how-it-works">How it works</a> •
  <a href="#-license">License</a>
</p>

---

## ✨ Features

- 🦕 **Classic T-Rex gameplay** — Jump, duck, and dodge obstacles just like the Chrome offline game
- 🌵 **Multiple obstacle types** — Small cacti, large cacti, double cacti, and flying pterodactyls
- 🌗 **Day/night cycle** — The world transitions between day and night every 700 points
- ⚡ **Progressive difficulty** — Speed increases over time, obstacles spawn more frequently
- ☁️ **Parallax effects** — Clouds scroll at different speeds for depth
- ⭐ **Starfield** — Stars appear during nighttime with smooth transitions
- 🏆 **High score tracking** — Your best score persists during the session
- 🎨 **Animated sprites** — Running, jumping, ducking, and death animations
- 📊 **Speed indicator** — Watch your speed climb in real time
- 💯 **Milestone flash** — Score blinks every 100 points, just like the original
- 🪶 **Zero dependencies** — Uses only Python standard library (`curses`)

## 📦 Install

```bash
# Clone and play immediately
git clone https://github.com/nadonghuang/dino.git
cd dino
python dino.py
```

Or install with pip:

```bash
pip install .
dino-run
```

### Requirements

- Python 3.8+
- Terminal with Unicode support
- Terminal size ≥ 50×16 (most terminals qualify)

## 🎮 Controls

| Key | Action |
|-----|--------|
| `SPACE` / `↑` | Jump |
| `↓` | Duck |
| `Q` / `ESC` | Quit |
| Any key | Restart (after game over) |

## 🚀 Usage

```bash
# Quick play
python dino.py

# Via pip install
dino-run

# Make it executable
chmod +x dino.py
./dino.py
```

## 🔧 How It Works

```
dino/
├── dino.py           # Complete game (single file, ~550 lines)
├── bin/dino          # CLI entry point
├── pyproject.toml    # Package config
├── LICENSE           # MIT
└── README.md         # You are here
```

The entire game lives in **one Python file** using only the standard library:

- **`curses`** — Terminal rendering, colors, and non-blocking keyboard input
- **Physics engine** — Gravity-based jump mechanics with velocity tracking
- **Sprite system** — Multi-frame ASCII sprites with collision hitbox detection
- **World generation** — Procedural obstacle spawning with difficulty scaling
- **Parallax rendering** — Clouds, ground, and stars at different scroll speeds

### Game Mechanics

- **Jump**: Velocity-based arc with configurable gravity (`0.6`) and jump force (`2.8`)
- **Duck**: Reduces hitbox height to slide under pterodactyls
- **Speed**: Starts at 8 chars/sec, increments by 0.002/frame, caps at 25
- **Pterodactyls**: Only appear after score 300, fly at varying heights
- **Collision**: Shrunk hitboxes with padding for forgiving gameplay

## 📁 Project Structure

```
dino.py          ← Everything is here
├── Constants    — Physics, speed, display config
├── Sprites      — ASCII art for dino, cacti, pteros, clouds
├── Player       — Dino physics, animation, hitbox
├── Obstacle     — Cacti & pterodactyls with movement
├── Cloud/Star   — Decorative parallax elements
├── Game         — Main loop: input → update → render
└── main()       — Entry point with size check
```

## 🤝 Contributing

Ideas welcome:

- Sound effects (terminal bell on jump)
- New obstacle types
- Difficulty presets (easy/medium/hard)
- Obstacle pattern generator
- Color theme customization

Fork, branch, PR. Keep it zero-dep.

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with 🦕 by <a href="https://github.com/nadonghuang">nadonghuang</a>
  <br/>
  <sub>If you survived past 1000, you're a legend. ⭐ this repo!</sub>
</p>
