# Tottenham Summer Squad Builder 2026

**Never coded in your life? You can still get this running in a few minutes.** You don't need to understand programming or edit any game files — just follow the step-by-step guide below: install Python, download the project, open Terminal in the folder, and run one command. That's it.

**COYS!** After a dreadful 2025/26 season, Roberto de Zerbi needs *your* help building Tottenham's squad for summer 2026.

```
  <o)
   /(
   ||
  (  )
   --
 SPURS
```

Sell players. Sign stars. Loan out fringe players. Build your 4-3-3 depth chart. When you're done, screenshot your final squad!

---

## What You Need

- A Mac or Windows computer
- Python 3.8 or newer (free)
- A terminal window (fullscreen recommended for the best experience)

**No extra downloads or pip installs** — this game uses only built-in Python.

---

## Step 1: Install Python

### On Mac

1. Open your web browser and go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Click the yellow **Download Python 3.x.x** button
3. Open the downloaded `.pkg` file and follow the installer (click Continue → Install)
4. Open **Terminal**:
   - Press `Cmd + Space`, type `Terminal`, press Enter
   - Or go to **Applications → Utilities → Terminal**
5. Check Python installed correctly:
   ```bash
   python3 --version
   ```
   You should see something like `Python 3.12.3`

### On Windows

1. Open your web browser and go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Click **Download Python 3.x.x**
3. Run the installer
4. **IMPORTANT:** On the first screen, check the box that says **"Add python.exe to PATH"**
5. Click **Install Now**
6. Open **Command Prompt**:
   - Press `Win + R`, type `cmd`, press Enter
   - Or search "Command Prompt" in the Start menu
7. Check Python installed correctly:
   ```cmd
   python --version
   ```
   You should see something like `Python 3.12.3`

---

## Step 2: Get This Project on Your Computer

Open the project on GitHub in your browser. Click the green **Code** dropdown (near the top right of the file list).

You have two options:

### Option A: Download ZIP (easiest — no Git required)

1. In the **Code** dropdown, click **Download ZIP**
2. Open your **Downloads** folder and double-click the ZIP to unzip it
3. You should get a folder named something like `tottenham-s26-destiny-main` or `tottenham-s26-destiny`
4. **Optional:** Drag that folder anywhere you like (Desktop, Documents, etc.) — the game works the same; only the path you type in Terminal changes (see Step 3)

Inside the folder you should see `main.py`, `config.json`, an `assets` folder, and a `data` folder.

### Option B: Clone with Git (if you already use Git)

1. In the **Code** dropdown, copy the HTTPS or SSH URL
2. Open Terminal (Mac) or Command Prompt (Windows) and run:
   ```bash
   git clone PASTE_THE_URL_HERE
   ```
3. A `tottenham-s26-destiny` folder will be created in whatever directory you ran that command from (often your home folder or Desktop)

---

## Step 3: Open Terminal in the Project Folder

Before you can run the game, Terminal needs to be **inside** the project folder. The command for that is `cd` (“change directory”). The path depends on where you put the folder.

### If you used Download ZIP and left it in Downloads (default)

**Mac:**
```bash
cd ~/Downloads/tottenham-s26-destiny
```
If the unzipped folder has a different name (e.g. `tottenham-s26-destiny-main`), use that name instead:
```bash
cd ~/Downloads/tottenham-s26-destiny-main
```

**Windows:**
```cmd
cd C:\Users\YourName\Downloads\tottenham-s26-destiny
```
Replace `YourName` with your Windows username. If the folder name after unzipping is different, use that name instead.

### If you moved the folder somewhere else

You need the **full path** to the folder, then:
```bash
cd FULL/PATH/TO/tottenham-s26-destiny
```

**Mac — easy way to get the path:**
1. Open Terminal
2. Type `cd ` (with a space after it)
3. Drag the project folder from Finder into the Terminal window — the path fills in automatically
4. Press Enter

**Mac — copy path from Finder:**
1. Right-click the folder (or Control-click)
2. Hold **Option** — **Copy … as Pathname** appears
3. In Terminal: `cd ` then paste (Cmd + V) and press Enter

**Windows — easy way:**
1. Open Command Prompt
2. Type `cd ` then drag the folder into the window, or paste the path you copied from File Explorer
3. Press Enter

**Windows — copy path from File Explorer:**
1. Open the folder in File Explorer
2. Click the address bar at the top — the full path is selected
3. Copy it (Ctrl + C)
4. In Command Prompt: `cd ` paste the path (Ctrl + V) and press Enter

**Tip:** You only need to `cd` into the folder once per Terminal session. If you close Terminal, run `cd` again next time before `python3 main.py` or `python main.py`.

---

## Step 4: Run the Game

### On Mac

```bash
python3 main.py
```

### On Windows

```cmd
python main.py
```

**Tip:** Make your terminal fullscreen for the best experience:
- Mac Terminal: View → Enter Full Screen (or `Cmd + Ctrl + F`)
- Windows Command Prompt: Alt + Enter (or maximize the window)

---

## How to Play

Roberto de Zerbi will greet you and explain the rules (you can skip the intro after 5 seconds). Then you'll see:

- **Centre:** A 4-3-3 pitch with 3 player slots per position (`a` = starter, `b` = backup, `c` = third choice)
- **Left panel:** Injured → Loan returns → Academy
- **Right panel:** Sold → Loaned out, with Roberto standing below
- **Header:** Budget, squad size, non-homegrown count, sales used, wage bill, and any issues that still need resolving

### Commands

| Key | Action |
|-----|--------|
| **P** | Pick a player — sell, loan, move, buy back, recall, or place on pitch |
| **B** | Buy from the transfer market |
| **I** | View player info — full squad table or transfer market (great for finding homegrown players) |
| **F** | Finish — final squad summary to screenshot (only if all rules pass) |
| **E** | Exit to main menu (progress auto-saved) |

### Picking a Player

When you pick a player, you'll see context-specific options — for example:

- **On the pitch:** Move to another position, return to sidebar (if from injured/loan/academy), sell, or loan out
- **Injured / loan return / academy:** Place on pitch, sell, or loan out
- **Sold:** Place on pitch (buy back)
- **Loaned out:** Place on pitch (recall)

To place someone on the pitch, pick a **position number** (1 = GK, 2 = RB, … 11 = LW) and a **slot** (`a`, `b`, or `c`). If a slot is already filled, you'll be prompted to pick an open slot or handle the player currently there first.

### Roberto Reactions

After successful moves, Roberto may pop up (~20% chance) with a short comment — after the confirmation message, not before. Different quips play for lineup changes (promotions, demotions, new signings, etc.), sales, and loans.

### Rules

- **Starting budget:** 100M (editable in `config.json`)
- **Max squad size:** 25 players
- **Max non-homegrown:** 17 players
- **Max sales from current squad/injured:** 8 players
- **Loan returns:** Sell as many as you want — doesn't count toward the 8
- **Buy back:** Re-sign a sold Tottenham player — doesn't use a permanent sale slot
- **Loan out:** Saves wages per player (see `loan_wage_savings_m` in `config.json`)
- You can go over budget or squad limits while playing — warnings show in the header — but you can't **Finish** until everything is resolved
- All **injured** and **loan return** players must be sold, loaned, or placed on the pitch before finishing

### Position Key

| # | Code | Role |
|---|------|------|
| 1 | GK | Goalkeeper |
| 2 | RB | Right back |
| 3 | LB | Left back |
| 4 | RCB | Right centre back |
| 5 | LCB | Left centre back |
| 6 | LCM | Left centre mid |
| 7 | RW | Right winger |
| 8 | RCM | Right centre mid |
| 9 | ST | Striker |
| 10 | CAM | Attacking mid |
| 11 | LW | Left winger |

---

## Customising the Game (No Coding Required)

### Edit Player Lists

Open the CSV files in `data/` with Excel, Google Sheets, or any spreadsheet app:

| File | What's in it |
|------|-------------|
| `data/squad.csv` | Current first-team squad |
| `data/loan_returns.csv` | Players returning from loan |
| `data/injured.csv` | Injured players to resolve |
| `data/academy.csv` | Youth/academy players |
| `data/transfer_market.csv` | Players available to buy |

**CSV columns:**

```
id,name,nationality,position,age,sale_price_m,buy_price_m,contract_years,wages_per_week,homegrown
```

- `id` — unique ID like `son-12` (no spaces)
- `position` — GK, LB, LCB, RCB, RB, LCM, CAM, RCM, LW, ST, RW
- `homegrown` — `yes` or `no`
- `sale_price_m` / `buy_price_m` — millions of pounds (whole numbers in-game display)
- `wages_per_week` — weekly wage in **pounds** (e.g. `67308` for ~£67k/week)

### Edit Game Settings

Open `config.json` in any text editor (Notepad, TextEdit, VS Code):

```json
{
  "starting_budget_m": 100,
  "loan_wage_savings_m": 2,
  "max_squad_size": 25,
  "max_non_homegrown": 17,
  "max_tottenham_sales": 8
}
```

Change any value, save the file, and run the game again.

### Saved Squads

Every squad build is saved automatically as you play. Each one gets its own file in `data/saves/`.

When you launch the game:
- **No saved squads yet** → you'll go straight into creating your first one (with the full Roberto intro)
- **Saved squads exist** → you'll see the **main menu** where you can:
  - **Edit an existing squad** — pick up where you left off (no intro, just a quick welcome back)
  - **Create a new squad** — name it and get the full De Zerbi intro
  - **Delete a saved squad** — remove one you no longer want

Use **E** (Exit to menu) anytime during a session. Your progress is auto-saved after every move.

When you **Finish** and pass all checks, your squad is marked **Complete** — but you can still go back and edit it later from the main menu.

### Reset / Delete Saves

Delete individual squad files from `data/saves/`, or delete the whole `data/saves/` folder to wipe all saved squads and start over from the CSV files.

---

## Troubleshooting

### "python: command not found" or "python3: command not found"

Python isn't installed or isn't on your PATH.
- Reinstall from [python.org](https://www.python.org/downloads/)
- On Windows, make sure you checked **"Add python.exe to PATH"**

### "No such file or directory"

You're not in the right folder. See **Step 3** — use `cd` with the full path to your project folder, then run the game again.

### On Mac, try `python3` instead of `python`

```bash
python3 main.py
```

### The display looks squished

Make your terminal window wider and taller, or go fullscreen. The pitch layout needs roughly 150+ columns for sidebars and Roberto on the right.

### I want to start over

Delete files in `data/saves/` and relaunch the game.

---

## Testing It Yourself (Quick Guide)

Open Terminal (Mac) or Command Prompt (Windows), then:

### 1. Go to the project folder

See **Step 3** above — use the `cd` command that matches where you saved the folder (Downloads by default, or your own path).

### 2. Start with a clean slate (optional)

```bash
rm -rf data/saves
```

On Windows: `rmdir /s /q data\saves`

### 3. Run the game

**Mac:**
```bash
python3 main.py
```

**Windows:**
```cmd
python main.py
```

### 4. First launch (no saved squads)

1. Press **Enter** at the welcome screen
2. Type a squad name like `Test Build A` and press Enter
3. Watch Roberto explain the rules (or skip after 5 seconds)
4. You're in! Try these to verify things work:
   - **P** → pick a player → sell someone → check budget goes up in the header
   - **I** → view player info → scan the homegrown column
   - **B** → buy from the transfer market
   - **E** → return to main menu

### 5. Second launch (saved squads exist)

1. Run `python3 main.py` again
2. Press Enter → you should see the **main menu** with your saved squad listed
3. **1** → edit existing → welcome back message (no full intro)
4. **2** → create a new squad → full Roberto intro again
5. **3** → delete a squad if you want to clean up

### 6. Test finishing a squad

To get the final screenshot summary you must:
- Resolve all **loan returns** (left panel) — sell, loan, or place on pitch
- Resolve all **injured** players (left panel)
- Stay within budget, 25 players, and 17 non-homegrown

Then press **F** to finish. You'll get the celebration screen, then return to the main menu with the squad marked **Complete**. You can still pick **1** to edit it again.

### 7. Where saves live

Your squads are stored as JSON files in `data/saves/` — one file per named build.

---

## Project Structure

```
tottenham-s26-destiny/
├── main.py              ← Run this to play
├── config.json          ← Game settings
├── README.md            ← You are here
├── assets/
│   ├── logo.txt         ← Spurs cockerel (headers & menus)
│   ├── roberto_face.txt ← De Zerbi face (speech bubbles)
│   └── roberto_standing.txt ← Roberto beside the pitch
├── data/
│   ├── squad.csv
│   ├── loan_returns.csv
│   ├── injured.csv
│   ├── academy.csv
│   ├── transfer_market.csv
│   └── saves/           ← Your saved squad builds (auto-created)
└── game/                ← Game code (don't need to touch this)
```

---

## COYS!

Build the squad. Make De Zerbi proud. Screenshot your final XI and share it.

*"We play brave football."* — Roberto de Zerbi
