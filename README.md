# Project Name: Mediscript

## Description

An application for managing, transcribing and summarizing appointments.
This application is meant to be a mobile application, but for the purposes of prototyping will be a web app that uses responsive design and developer tools to simulate a mobile experience.

## Prerequisites

Before running the application, your professor will need:

Python installation (3.10 or newer)
Required Python packages
AssemblyAI API key (for transcription services)

### Setup Instructions

1. : Install Python (if not installed)
   Windows:

Download Python from python.org
Run the installer, ensuring to check "Add Python to PATH"
Verify installation by opening Command Prompt and typing: python --version

macOS:

Download Python from python.org
Run the installer
Verify installation by opening Terminal and typing: python3 --version

## Installation

1.  **Extract the archive:** Extract the contents of the zip file to a directory on your computer.
2.  **Navigate to the project directory:** Open your terminal or command prompt and navigate to the directory where you extracted the files (e.g., `cd your_project_name`).
    On MacOS you can right-click and open New Terminal at Folder. On Windows, you can hold shift+right-click and open Powershell in the folder.
    For Windows you may need to use this command as Administrator:

powershell -ExecutionPolicy Bypass -Command ".\venv\Scripts\Activate.ps1

2.  **Create a virtual environment:**

Windows:
py -3 -m venv venv on Windows
venv\Scripts\activate

For Windows you may need to use this command as Administrator:
(powershell -ExecutionPolicy Bypass -Command ".\venv\Scripts\Activate.ps1)

MacOS:
python3 -m venv venv
source venv/bin/activate

3.  **Install dependencies:**

    pip install Flask flask-socketio "assemblyai[extras]"

## Running the Application

1.  **Run the Flask application:**

    python app.py

    or

    python3 app.py

2.  **Access the application in your web browser:**

    Open your browser and go to `http://127.0.0.1:6069`.

## Notes

- I have tested these instructions on both Windows & MacOS using the zip file without issue.
- Ensure your microphone is working for the transcription features.
- The application uses my AssemblyAI API key. This is a private and paid for key with $1.65136 in use.
- Each transcription depending on length is between $0.05-$0.15 so feel free to test multiple transcriptions, I don't expect you'd need more than $0.50-1.00 in use. The remaining credit will be used in assignment 5 evaluation.

## Using Mediscript

When you first open the application on `http://127.0.0.1:6069`, open up the Developer tools using Cmd + Option + I (Mac) or Ctrl + Shift + I or F12 (Windows) or use the menu in the upper right corner, navigate to "More Tools" then "Developer tools"

With the Developer tools open, select "Responsive Design Mode" (Firefox) / "Toggle Device Toolbar" (Chrome) and from the dropdown select any mobile phone.

Now we are ready to use Mediscript.

You will be at a login screen with a prepopulated login and password. Simply click login.
This was done to get users into the application and use the actual functionality as most everyone is familiar with logging into an application.

Once "logged in", you will be brought to the home screen. This is designed exactly as in the low fidelity prototype.

There are a couple mock appointments and a mock transcript.

To trial transcription, I've included a few brief appointment scenarios within the application folder in "scenarios"
Press the record button to record your own transcript and read through one of the scenarios.

Once finished, press the pause button and then the save button. You will see a "saving" screen as the application processess the transcript to be summarized.

When the summarization is complete you will be brought to the "Archive" page, which shows past transcripts, most recent first.

Select the transcript you just recorded to view the summary. You can toggle between the summary and the original.

Select the back button to view the list of archived transcripts, or select the back button again to go back to the homescreen.

Lets try the Search functionality. Click the search button and search the word "Iron" (use mouse clicks to simulate using a mobile phone instead of pressing "Enter")

One of the past transcripts should appear. If we click on it we'll be taken to its view.

Press the back button to go back into Archive and press again to the home screen.

Lets check out the Appointments functionality by selecting the Appointments button.

Here we can view a mock appointment in April and one in May. We can click on them to edit or delete them.

Going back to the main appointments screen, we can click the "+" button at the bottom to add a new appointment.

Once we've added a new appointment we can press the back button to go back to the home screen.

The last piece of functionality to check out is settings.

Right now we only have light and dark mode. We can select to toggle between the two and save.
More settings will be explored during assignment 5 as users evaluate the application and detail what settings they might like to see within the application.

This concludes the functinality of the high fidelity prototype of Mediscript.
