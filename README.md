# Fish Audio Studio

A Gradio web app for Fish Audio text-to-speech, emotion tags, and voice cloning.

## Run locally

Use Python 3.11.9 or later, then install the dependencies and start the app:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export FISH_API_KEY="your-fish-audio-api-key"  # Windows PowerShell: $env:FISH_API_KEY="your-fish-audio-api-key"
python app.py
```

Open <http://localhost:7860>. You can also enter the Fish Audio API key directly in the app instead of setting `FISH_API_KEY`.

## Deploy to Render

### Web Service

1. Push this repository to GitHub and create a new **Web Service** in Render connected to it.
2. Select **Python** as the runtime and a CPU instance (Starter or another suitable plan).
3. Set the build command to `pip install --upgrade pip && pip install -r requirements.txt` and the start command to `python app.py`.
4. Add `PYTHON_VERSION` with value `3.11.9`. Optionally add `FISH_API_KEY` as a secret environment variable.
5. Deploy. Render supplies the `PORT` value, and the app binds to `0.0.0.0`.

### Blueprint

Alternatively, in Render choose **New → Blueprint**, select this repository, and apply the configuration in `render.yaml`. Enter `FISH_API_KEY` in the Blueprint environment prompt if you want to configure the server-side key; users can otherwise provide a key in the UI.
