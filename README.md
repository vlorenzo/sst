# Simultaneous Speech Translator (SST)

This application provides real-time speech translation using AI-powered tools. By default, it translates from Italian to English, but you can specify different input and output languages.

## Prerequisites

- macOS (10.15 Catalina or later recommended)
- Python 3.8 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Install Python (if not already installed)

macOS comes with Python pre-installed, but it's recommended to use a more recent version. You can download the latest version from the official Python website or use Homebrew:

```bash
brew install python
```

### 2. Create a Virtual Environment

It's best practice to create a virtual environment for Python projects. This keeps dependencies required by different projects separate.

Navigate to your project directory and run:

```bash
python3 -m venv sst-env
```

### 3. Activate the Virtual Environment

Activate the virtual environment:

```bash
source sst-env/bin/activate
```

Your command prompt should now show "(sst-env)".

### 4. Install Required Packages

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Ensure your virtual environment is activated:

```bash
source sst-env/bin/activate
```

2. Run the Flask application:

```bash
python sst.py
```

By default, this will set up the application to translate from Italian to English.

3. To specify different input and output languages, use the following optional parameters:

```bash
python sst.py --input_lang [INPUT_LANG_CODE] --output_lang [OUTPUT_LANG_CODE]
```

For example, to translate from French to Spanish:

```bash
python sst.py --input_lang fr --output_lang es
```
Note: Make sure to use valid language codes supported by the Whisper model and Google Translate.

4. Open a web browser and navigate to `http://127.0.0.1:5000/`

5. You should now see the application interface. Follow the on-screen instructions to start translating speech.

## Troubleshooting

- If you encounter any issues with audio input, ensure your microphone is properly connected and has necessary permissions.
- For any package installation issues, ensure you're using the latest pip version: `pip install --upgrade pip`
- If you face any other issues, please check the console output for error messages and refer to the project documentation or raise an issue on the project's GitHub page.

## Contributing

Contributions to improve the application are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

