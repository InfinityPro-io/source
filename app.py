import os
import tempfile

import gradio as gr
from fishaudio import FishAudio
from fishaudio.types import Prosody, ReferenceAudio, TTSConfig


def synthesize_speech(
    api_key,
    text,
    model_choice,
    reference_id,
    ref_audio_path,
    ref_transcript,
    speed,
    temperature,
    top_p,
):
    effective_key = (api_key or "").strip() or os.environ.get("FISH_API_KEY", "").strip()
    if not effective_key:
        raise gr.Error("Please enter your Fish Audio API key or configure FISH_API_KEY on the server.")
    if not text or not text.strip():
        raise gr.Error("Please enter text to synthesize.")

    client = FishAudio(api_key=effective_key)

    # Prepare optional zero-shot voice cloning reference.
    references = []
    if ref_audio_path:
        with open(ref_audio_path, "rb") as audio_file:
            references.append(
                ReferenceAudio(
                    audio=audio_file.read(),
                    text=ref_transcript.strip() if ref_transcript else "",
                )
            )

    config = TTSConfig(
        prosody=Prosody(speed=float(speed)),
        temperature=float(temperature),
        top_p=float(top_p),
        format="mp3",
    )

    kwargs = {
        "text": text,
        "model": model_choice,
        "config": config,
    }
    if references:
        kwargs["references"] = references
    elif reference_id and reference_id.strip():
        kwargs["reference_id"] = reference_id.strip()

    audio_bytes = client.tts.convert(**kwargs)

    # Save output to a temporary MP3 file for the frontend player.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        for chunk in ([audio_bytes] if isinstance(audio_bytes, bytes) else audio_bytes):
            temp_file.write(chunk)
    return temp_file.name


def append_tag(current_text, tag):
    return f"{current_text} {tag} ".lstrip()


custom_css = """
.gradio-container { max-width: 1050px !important; margin: auto; }
.header-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    padding: 24px;
    border-radius: 12px;
    color: white;
    margin-bottom: 16px;
}
"""

with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="indigo"),
    css=custom_css,
    title="Fish Audio Studio",
) as demo:
    gr.HTML(
        """
        <div class="header-box">
            <h1 style="margin: 0; font-size: 26px; color: #fff;">🐟 Fish Audio Studio Frontend</h1>
            <p style="margin: 6px 0 0 0; color: #94a3b8;">
                Multilingual Text-to-Speech, Inline Emotion Tags & Instant Zero-Shot Voice Cloning
            </p>
        </div>
        """
    )

    with gr.Row():
        api_key_input = gr.Textbox(
            label="Fish Audio API Key",
            placeholder="Paste your API key from https://fish.audio/app/api-keys/ (or configure it on the server)",
            type="password",
            scale=3,
        )
        model_selector = gr.Dropdown(
            choices=["s2.1-pro-free", "s2-pro", "drama-3"],
            value="s2.1-pro-free",
            label="Model Engine (s2.1-pro-free requires no paid credits)",
            scale=2,
        )

    with gr.Row():
        with gr.Column(scale=6):
            text_input = gr.Textbox(
                label="Script",
                placeholder="Type your text here... Use inline emotion tags like [laugh] or [whisper] for expressive control.",
                lines=6,
                value="Welcome to Fish Audio Studio! [laugh] You can clone any voice in seconds right from the browser.",
            )

            gr.Markdown("**Quick Emotion & Expression Tags**")
            with gr.Row():
                btn_laugh = gr.Button("[laugh]", size="sm")
                btn_whisper = gr.Button("[whisper]", size="sm")
                btn_sigh = gr.Button("[sigh]", size="sm")
                btn_excited = gr.Button("[excited]", size="sm")
                btn_sad = gr.Button("[sad]", size="sm")

            with gr.Tabs():
                with gr.TabItem("🎙️ Instant Voice Clone (Upload Sample)"):
                    ref_audio = gr.Audio(
                        label="Reference Voice Sample (10–30s clean audio)",
                        type="filepath",
                    )
                    ref_text = gr.Textbox(
                        label="Reference Audio Transcript (Optional but improves accuracy)",
                        placeholder="Exact words spoken in the reference audio...",
                    )
                with gr.TabItem("🆔 Voice Library ID"):
                    ref_id = gr.Textbox(
                        label="Fish Audio Reference Voice ID",
                        placeholder="e.g., 9a9cf47702da476aa4629e2506d4a857 (Leave blank for default voice)",
                    )

        with gr.Column(scale=5):
            with gr.Group():
                gr.Markdown("### 🎛️ Prosody & Sampling Controls")
                speed_slider = gr.Slider(0.5, 2.0, value=1.0, step=0.05, label="Speaking Speed")
                temp_slider = gr.Slider(0.1, 1.0, value=0.7, step=0.05, label="Temperature (Expressiveness)")
                top_p_slider = gr.Slider(0.1, 1.0, value=0.7, step=0.05, label="Top-P (Stability)")

            generate_btn = gr.Button("🚀 Generate Speech", variant="primary", size="lg")
            audio_output = gr.Audio(
                label="Generated Speech Output",
                type="filepath",
                interactive=False,
            )

    btn_laugh.click(append_tag, [text_input, gr.State("[laugh]")], text_input)
    btn_whisper.click(append_tag, [text_input, gr.State("[whisper]")], text_input)
    btn_sigh.click(append_tag, [text_input, gr.State("[sigh]")], text_input)
    btn_excited.click(append_tag, [text_input, gr.State("[excited]")], text_input)
    btn_sad.click(append_tag, [text_input, gr.State("[sad]")], text_input)

    generate_btn.click(
        fn=synthesize_speech,
        inputs=[
            api_key_input,
            text_input,
            model_selector,
            ref_id,
            ref_audio,
            ref_text,
            speed_slider,
            temp_slider,
            top_p_slider,
        ],
        outputs=audio_output,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.queue().launch(server_name="0.0.0.0", server_port=port, share=False)
