# 📊 ZL Watch — Discord Stats Bot

<a href="https://kappa.lol/QICOtK" target="_blank" style="float: right;">
  <img src="https://kappa.lol/QICOtK" width="100" height="100" alt="ZL Watch Logo" align="right" />
</a>

**ZL Watch** is a powerful Discord bot built with `discord.py`, designed to track messages, voice channel activity, and give you deep insight into your server engagement — all while keeping **full control** of your data.
No external APIs. No telemetry. Just stats.

## ❓ Why?

*Statbot wanted $2.99 for data older than 30 days. I wanted freedom. So I made ZL Watch.*


## ✨ Features

- 📈 Track **message counts** per user and per channel  
- 🕒 Monitor **voice time** per user and per channel  
- 🏆 See server-wide top users  
- 💾 Store everything in a local **SQLite database**  
- 🛠 Import your old **Statbot** data with a one-time CSV migration ()
- ✅ Supports **slash commands** (`/stats`, `/top`, `/statsall`, `/help`)  
- 💡 Lightweight, clean, and self-hosted  


## 🚀 Quickstart

1. **Clone the repo:**
   ```bash
   git clone https://github.com/zzackllack/ZL-Watch.git
   cd ZL-Watch
   ```

2. **Create a virtual environment (optional):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your token:**
   Add your Discord token in `bot.py` or via `.env`

5. **Run the bot:**
   ```bash
   python bot.py
   ```

6. (Optional) **Migrate from Statbot:**
   ```bash
   python import_statbot_data.py
   ```

## 🧩 Slash Commands

| Command        | Description                              |
|----------------|------------------------------------------|
| `/stats`       | View your personal stats                 |
| `/top`         | See the top users by messages/voice time |
| `/statsall`    | Get server-wide stats overview           |
| `/help`        | Setup instructions and troubleshooting   |
| `/license`     | View license and usage terms             |


## 🧠 Project Structure

```
ZL-Watch/
├── bot.py                   # Bot entry point
├── database.py              # SQLite logic
├── import_statbot_data.py   # One-time Statbot migration
├── stats.db                 # Generated DB
├── cogs/
│   ├── stats.py
│   ├── top.py
│   ├── statsall.py
│   ├── help.py
│   └── license.py
```

## 👤 Author

ZL Watch is developed by **[Zacklack](https://github.com/zzackllack)**.


## 📄 License

Licensed under the **BSD 3-Clause License**  
[View Full License](https://opensource.org/licenses/BSD-3-Clause)

> You're free to use, modify, and distribute this project with attribution.
