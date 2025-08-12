# Text-to-Speech Interface

This project provides a simple Text-to-Speech (TTS) interface that allows users to input text and have it spoken aloud. The interface is built using Python and utilizes the `pyttsx3` library for TTS functionality.

## Features

- Input text through the command line.
- Speak the input text when Enter is pressed.
- Handle exit commands to gracefully terminate the program.
- Error handling for input interruptions.

## Requirements

To run this project, you need to have Python installed on your machine. Additionally, you will need to install the required dependencies listed in `requirements.txt`.

## Installation

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Install the required dependencies using pip:

   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the main script:

   ```
   python src/tts.py
   ```

2. Type the text you want to be spoken and press Enter.
3. To exit the program, type 'sair', 'exit', or 'quit' and press Enter.

## Future Improvements

- Add more voices and customization options.
- Implement a graphical user interface (GUI) for easier interaction.
- Include additional utility functions in the `src/utils/__init__.py` file.