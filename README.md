# 🧊 Rubik's Cube Recorder

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Streamlit application for tracking your Rubik's cube solving progress, recording times, and organizing your algorithm library.

## 🚀 Live Demo

**Try it now:** [Coming Soon - Deploy to see your app URL here!]

## Features

### 👤 Player Profile
- Set your player name for personalized tracking
- All solve records include player identification
- Filter and view statistics by player
- Support for multiple players using the same app
- Welcome message with player greeting

### ⏱️ Solve Recording
- **Built-in Stopwatch Timer** with Start/Stop/Reset controls
- Real-time timer display with live updates
- Automatic time transfer to solve record
- Manual time entry option
- Support for multiple cube types (3x3, 2x2, 4x4, 5x5, Pyraminx, Megaminx, Skewb, Square-1)
- Save scramble sequences for each solve
- Add notes and observations for each solve
- Automatic timestamp tracking
- Player name saved with each solve

### 📊 Statistics & Analysis
- Filter statistics by player name
- Personal best times for each cube type
- Average times and medians
- Ao5 (Average of 5), Ao12, and Ao100 calculations
- Time progression charts with moving averages
- Distribution analysis
- Improvement trends over time
- Session statistics
- Player-specific performance tracking

### 📋 Solve History
- View all your recorded solves
- Filter by player name and cube type
- Sort by time, date, cube type, or player name
- View player information for each solve
- Delete unwanted records
- Export data to CSV

### 🧩 Algorithm Library
- Save and organize your favorite algorithms
- Categorize by pattern type (PLL, OLL, F2L, CMLL, ZBLL, etc.)
- Add execution notes and finger trick tips
- Search and filter algorithms
- Quick reference during practice

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/BartonChenTW/Rubik-s-cube-recorder.git
cd Rubik-s-cube-recorder
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The app will automatically open in your default web browser at `http://localhost:8501`.

### Setting Up Your Player Profile

1. **Enter Your Name** in the sidebar under "👤 Player Profile"
2. Your name will be displayed with a welcome message
3. Your name will be automatically saved with each solve record
4. You can change your name at any time

**Note:** If you don't enter a name, solves will be saved as "Anonymous"

### Recording Your First Solve

#### Using the Stopwatch Timer:
1. Navigate to the "Record New Solve" page
2. Click "▶️ Start" when you begin solving
3. Click "⏹️ Stop" when you finish
4. The time automatically fills into the input field
5. Click "🔄 Reset" to clear the timer for your next solve

#### Manual Entry:
1. Navigate to the "Record New Solve" page
2. Enter your solve time manually in seconds
3. Select your cube type
4. (Optional) Add the scramble sequence and notes
5. Click "💾 Save Solve"

### Viewing Statistics

1. Navigate to the "Statistics" page
2. Select a player (or view "All" players)
3. Select a specific cube type or view all
4. Explore various charts and metrics:
   - Personal bests
   - Average times
   - Time progression
   - Distribution analysis

### Filtering Records by Player

1. Navigate to the "View Records" page
2. Use the "Filter by Player" dropdown to select one or more players
3. View solve records filtered by your selection
4. All statistics update based on your filters

### Managing Algorithms

1. Navigate to the "Algorithms" page
2. Click "➕ Add New Algorithm"
3. Fill in the pattern name, algorithm notation, category, and notes
4. Click "💾 Save Algorithm"
5. Browse your algorithm library with category filters

### GitHub Data Sync (Cloud Persistence)

**Keep your data safe with automatic GitHub backup!**

1. **Enable Auto-Sync** in the sidebar under "💾 Data Backup"
2. Toggle "Auto-sync to GitHub" ON
3. Every time you save a solve, it automatically commits and pushes to GitHub
4. Your data persists even when the app restarts or redeploys!

**Manual Sync:**
- Click "🔄 Sync Now" button to manually backup your data
- Status indicator shows if you have unsaved changes

**How it works:**
- Data files (`data/solves.csv` and `data/algorithms.json`) are stored in your GitHub repo
- Changes are committed with descriptive messages
- Automatic push to GitHub ensures cloud backup
- Works on both local and Streamlit Cloud deployments

## Project Structure

```
Rubik-s-cube-recorder/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
├── data/                       # Data storage directory
│   ├── solves.csv             # Solve records (auto-generated)
│   └── algorithms.json        # Algorithm library (auto-generated)
└── utils/                      # Utility modules
    ├── data_manager.py        # Data management functions
    ├── visualizations.py      # Chart and visualization functions
    └── github_storage.py      # GitHub sync functionality
```

## Data Storage

**Local Storage:**
- **Solve records** are stored in `data/solves.csv`
- **Algorithms** are stored in `data/algorithms.json`
- Data files are automatically created on first run

**Cloud Persistence (GitHub Sync):**
- Enable "Auto-sync to GitHub" for automatic backup
- Data commits to your GitHub repository
- Survives app restarts and redeployments
- No additional database needed!
- All data is stored locally on your machine

## Features in Detail

### Statistics Calculations

- **Ao5 (Average of 5)**: Average of your last 5 solves, excluding the best and worst times
- **Ao12 (Average of 12)**: Average of your last 12 solves, excluding the best and worst times
- **Ao100 (Average of 100)**: Average of your last 100 solves, excluding the best and worst times

### Multi-Player Support

The app supports multiple players:
- Each player can set their own name in the sidebar
- All solve records include the player name
- Filter statistics and records by specific players
- Compare performance between different players
- Great for families, clubs, or competitions

### Supported Cube Types

- 2x2 (Pocket Cube)
- 3x3 (Standard Rubik's Cube)
- 4x4 (Rubik's Revenge)
- 5x5 (Professor's Cube)
- Pyraminx
- Megaminx
- Skewb
- Square-1

### Algorithm Categories

- PLL (Permutation of the Last Layer)
- OLL (Orientation of the Last Layer)
- F2L (First Two Layers)
- CMLL (Corners of the Last Layer)
- ZBLL (Zborowski-Bruchem Last Layer)
- Winter Variation
- Other (custom categories)

## Tips for Best Results

1. **Set Your Name**: Always enter your player name for accurate tracking
2. **Consistency**: Record all your solves to get accurate statistics
3. **Use the Stopwatch**: The built-in timer makes recording faster and more accurate
4. **Scrambles**: Save scrambles to review difficult cases later
5. **Notes**: Add notes about what went well or what needs improvement
6. **Regular Practice**: Track your progress over time with the statistics page
7. **Algorithm Practice**: Use the algorithm library to practice specific cases
8. **Multi-Player**: Each player should set their name before recording solves

## Customization

You can customize the app by modifying:
- **Cube types**: Edit the cube type list in `app.py`
- **Algorithm categories**: Modify the category list in `app.py`
- **Chart colors**: Adjust color schemes in `utils/visualizations.py`
- **Statistics**: Add new metrics in `utils/data_manager.py`

## Troubleshooting

### App won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Data not saving
- Ensure the `data/` directory exists and is writable
- Check file permissions

### Charts not displaying
- Verify Plotly is installed: `pip install plotly`
- Clear browser cache and refresh

## Future Enhancements
## 🚀 Deployment

Want to deploy your own version? Check out [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to Streamlit Cloud.

**Quick Deploy:**
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub account
4. Select this repository and click "Deploy!"

Your app will be live at `https://your-app-name.streamlit.app`

## 🔮 Future Enhancements

Potential features for future versions:
- ✅ ~~Timer integration for live solve recording~~ (Already implemented!)
- Import/export functionality for solve data
- Comparison with other cubers
- Video recording integration
- Mobile app version
- Cloud sync across devices
- Competition mode with multiple timers

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Data visualization powered by [Plotly](https://plotly.com/)
- Data handling with [Pandas](https://pandas.pydata.org/)

## Contact

For questions or suggestions, please open an issue on GitHub.

---

**Happy Cubing! 🧊🎯**
