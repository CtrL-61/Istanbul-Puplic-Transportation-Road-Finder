# Metro Pulse
Metro Pulse is a modern, bilingual (TR/EN) web application that helps users find the fastest route in complex metro networks.
It currently serves Istanbul's metro networks.

## Features
-  Shortest Route Calculation: The fastest route between stops is calculated using the Dijkstra algorithm with the NetworkX library.
- Dual Language Support: Easy switching between Turkish and English languages.
- Dark/Light Mode: Easy switching between dark and light modes for modern design options that are easy on the eyes.
- PWA Support: The app can be installed on your phone like a real app by selecting "Add to Home Screen". 
- Transfer Information: Clearly displays route changes and estimated travel times. 
- Share via WhatsApp: The route you find can be shared on WhatsApp. 

## Technologies Used
- Backend: Python, Flask
- Algorithm/Graph: NetworkX
- Frontend: Jinja2, Bootstrap 5, CSS3, JavaScript
- PWA: Manifest.json
- Deployment: Vercel

## Installation and Running
To run the project on your local computer, follow these steps:

### ​1. Prerequisites
​Make sure you have Python 3.8+ installed on your system. You can check your version by running:
```bash
   python --version
```
Clone the project from GitHub and navigate into the project folder:
```bash
   git clone [https://github.com/CtrL-61/Istanbul-Puplic-Transportation-Road-Finder]
   cd metro-pulse
```

### 2. Create a Virtual Environment (Recommended)
​It is best practice to use a virtual environment to keep dependencies organized:
# For Windows
```bash
   python -m venv venv
   venv\Scripts\activate
```

# For macOS/Linux
```bash
   python3 -m venv venv
   source venv/bin/activate
```

### 3. Install Dependencies
​Install all the necessary Python libraries using the requirements.txt file:
```bash
  pip install -r requirements.txt
```

### 4. Run the Application
​Start the Flask development server:
```bash
python app.py
```

After running the command, open your browser and go to:
```bash
http://127.0.0.1:5000
```
​## Project Structure
​app.py: The main Flask server and routing logic. 
​templates/: HTML files (index, result, error pages).
static/: CSS styles, JavaScript, and manifest files.
vercel.json: Configuration for cloud deployment.

## NOTE: This project was developed entirely on an Android phone. The project is currently in the design and testing phase. If you encounter any errors or have new ideas to add, please let us know. Thank you. 


