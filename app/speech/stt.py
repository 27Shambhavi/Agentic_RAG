from __future__ import annotations

import os
import wave
import tempfile
from pathlib import Path

import av
import numpy as np

from faster_whisper import WhisperModel


# =========================================================
# CONFIG
# =========================================================

MODEL_SIZE = "base"

TARGET_SAMPLE_RATE = 16000

TARGET_CHANNELS = 1

MIN_AUDIO_SECONDS = 0.2

SILENCE_RMS_THRESHOLD = 0.0005


# =========================================================
# LOAD MODEL
# =========================================================

print(
    "\n================================================="
)

print(
    "[STT] Loading Faster-Whisper model..."
)

print(
    "[STT] Model:",
    MODEL_SIZE,
)

print(
    "[STT] Device: CPU"
)

print(
    "[STT] Compute type: int8"
)


whisper_model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8",
)


print(
    "[STT] Faster-Whisper model loaded."
)

print(
    "=================================================\n"
)


# =========================================================
# AUDIO DIAGNOSTICS
# =========================================================

def inspect_audio(
    audio_path: str,
) -> dict:

    path = Path(
        audio_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    try:

        container = av.open(
            str(path)
        )

        audio_stream = None

        for stream in container.streams:

            if stream.type == "audio":

                audio_stream = stream

                break

        if audio_stream is None:

            container.close()

            raise ValueError(
                "No audio stream found."
            )

        sample_rate = (
            audio_stream.codec_context.sample_rate
        )

        channels = (
            audio_stream.codec_context.channels
        )

        duration = (
            float(audio_stream.duration)
            * float(audio_stream.time_base)
            if audio_stream.duration
            else 0.0
        )

        container.close()

        return {
            "sample_rate": sample_rate,
            "channels": channels,
            "duration": duration,
        }

    except Exception as error:

        print(
            "[STT] Audio inspection warning:",
            repr(error),
        )

        return {
            "sample_rate": None,
            "channels": None,
            "duration": 0.0,
        }


# =========================================================
# DECODE AUDIO
# =========================================================

def decode_audio(
    audio_path: str,
) -> np.ndarray:

    print(
        "[STT] Decoding audio..."
    )

    container = av.open(
        audio_path
    )

    audio_stream = None

    for stream in container.streams:

        if stream.type == "audio":

            audio_stream = stream

            break

    if audio_stream is None:

        container.close()

        raise ValueError(
            "No audio stream found in recording."
        )

    # -----------------------------------------------------
    # Resample to:
    #
    # 16 kHz
    # Mono
    # Float32
    # -----------------------------------------------------

    resampler = av.audio.resampler.AudioResampler(
        format="flt",
        layout="mono",
        rate=TARGET_SAMPLE_RATE,
    )

    chunks = []

    try:

        for frame in container.decode(
            audio_stream
        ):

            resampled_frames = resampler.resample(
                frame
            )

            if not isinstance(
                resampled_frames,
                list,
            ):

                resampled_frames = [
                    resampled_frames
                ]

            for resampled in resampled_frames:

                if resampled is None:

                    continue

                array = resampled.to_ndarray()

                array = np.asarray(
                    array,
                    dtype=np.float32,
                )

                # -------------------------------------------------
                # Mono audio should be:
                #
                # (1, samples)
                #
                # Convert to:
                #
                # (samples,)
                # -------------------------------------------------

                if array.ndim == 2:

                    array = array[0]

                array = array.reshape(
                    -1
                )

                chunks.append(
                    array
                )

    finally:

        container.close()

    # -----------------------------------------------------
    # Flush resampler
    # -----------------------------------------------------

    try:

        flushed = resampler.resample(
            None
        )

        if flushed:

            if not isinstance(
                flushed,
                list,
            ):

                flushed = [
                    flushed
                ]

            for frame in flushed:

                if frame is None:

                    continue

                array = frame.to_ndarray()

                array = np.asarray(
                    array,
                    dtype=np.float32,
                )

                if array.ndim == 2:

                    array = array[0]

                array = array.reshape(
                    -1
                )

                chunks.append(
                    array
                )

    except Exception:

        pass

    if not chunks:

        raise ValueError(
            "No audio samples could be decoded."
        )

    audio = np.concatenate(
        chunks
    )

    # -----------------------------------------------------
    # Remove NaN / infinity
    # -----------------------------------------------------

    audio = np.nan_to_num(
        audio,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    # -----------------------------------------------------
    # Normalize if necessary
    # -----------------------------------------------------

    peak = float(
        np.max(
            np.abs(audio)
        )
    )

    print(
        "[STT] Peak amplitude:",
        round(peak, 6),
    )

    if peak > 0:

        # Don't amplify normal audio.
        #
        # Only boost very quiet recordings.
        #

        if peak < 0.05:

            gain = min(
                8.0,
                0.25 / peak,
            )

            print(
                "[STT] Quiet recording detected."
            )

            print(
                "[STT] Applying gain:",
                round(gain, 2),
            )

            audio = (
                audio
                * gain
            )

            audio = np.clip(
                audio,
                -1.0,
                1.0,
            )

    # -----------------------------------------------------
    # RMS
    # -----------------------------------------------------

    rms = float(
        np.sqrt(
            np.mean(
                np.square(audio)
            )
        )
    )

    duration = (
        len(audio)
        / TARGET_SAMPLE_RATE
    )

    print(
        "[STT] Samples:",
        len(audio),
    )

    print(
        "[STT] Duration:",
        round(duration, 2),
        "seconds",
    )

    print(
        "[STT] RMS:",
        round(rms, 6),
    )

    # -----------------------------------------------------
    # Silence check
    # -----------------------------------------------------

    if duration < MIN_AUDIO_SECONDS:

        raise ValueError(
            "Recording is too short."
        )

    if rms < SILENCE_RMS_THRESHOLD:

        raise ValueError(
            "Recording contains almost no audible "
            "signal. Please check your microphone."
        )

    return audio


# =========================================================
# SAVE NORMALIZED WAV
# =========================================================

def save_normalized_wav(
    audio: np.ndarray,
) -> str:

    temporary_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav",
    )

    output_path = (
        temporary_file.name
    )

    temporary_file.close()

    # -----------------------------------------------------
    # Convert float [-1, 1]
    # to signed 16-bit PCM
    # -----------------------------------------------------

    audio = np.clip(
        audio,
        -1.0,
        1.0,
    )

    pcm = (
        audio
        * 32767
    ).astype(
        np.int16
    )

    with wave.open(
        output_path,
        "wb",
    ) as wav_file:

        wav_file.setnchannels(
            1
        )

        wav_file.setsampwidth(
            2
        )

        wav_file.setframerate(
            TARGET_SAMPLE_RATE
        )

        wav_file.writeframes(
            pcm.tobytes()
        )

    print(
        "[STT] Normalized WAV:",
        output_path,
    )

    print(
        "[STT] WAV size:",
        os.path.getsize(
            output_path
        ),
        "bytes",
    )

    return output_path


# =========================================================
# TRANSCRIBE
# =========================================================

def transcribe_audio(
    audio_path: str,
) -> str:

    path = Path(
        audio_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    print(
        "\n================================================="
    )

    print(
        "[STT] START TRANSCRIPTION"
    )

    print(
        "[STT] Input:",
        path,
    )

    print(
        "[STT] Input size:",
        path.stat().st_size,
        "bytes",
    )

    print(
        "================================================="
    )

    normalized_path = None

    try:

        # =================================================
        # INSPECT ORIGINAL AUDIO
        # =================================================

        info = inspect_audio(
            str(path)
        )

        print(
            "[STT] Original sample rate:",
            info.get(
                "sample_rate"
            ),
        )

        print(
            "[STT] Original channels:",
            info.get(
                "channels"
            ),
        )

        print(
            "[STT] Original duration:",
            round(
                info.get(
                    "duration",
                    0.0,
                ),
                2,
            ),
            "seconds",
        )

        # =================================================
        # DECODE + NORMALIZE
        # =================================================

        audio = decode_audio(
            str(path)
        )

        # =================================================
        # SAVE CLEAN WAV
        # =================================================

        normalized_path = save_normalized_wav(
            audio
        )

        # =================================================
        # WHISPER
        # =================================================

        print(
            "\n[STT] Sending normalized audio to Whisper..."
        )

        segments, whisper_info = (
            whisper_model.transcribe(

                normalized_path,

                beam_size=5,

                best_of=5,

                temperature=0,

                # IMPORTANT:
                # Do NOT enable VAD here.
                #
                # The audio has already been inspected
                # and normalized.
                #
                vad_filter=False,

                condition_on_previous_text=False,

                compression_ratio_threshold=2.4,

                log_prob_threshold=-1.0,

                no_speech_threshold=0.6,
            )
        )

        print(
            "[STT] Detected language:",
            getattr(
                whisper_info,
                "language",
                None,
            ),
        )

        print(
            "[STT] Language probability:",
            getattr(
                whisper_info,
                "language_probability",
                None,
            ),
        )

        # =================================================
        # COLLECT SEGMENTS
        # =================================================

        text_parts = []

        for segment in segments:

            segment_text = (
                segment.text
                or ""
            ).strip()

            print(
                "[STT] Segment:",
                repr(segment_text),
            )

            if segment_text:

                text_parts.append(
                    segment_text
                )

        # =================================================
        # FINAL TEXT
        # =================================================

        result = " ".join(
            text_parts
        ).strip()

        print(
            "\n[STT] FINAL TEXT:"
        )

        print(
            repr(result)
        )

        print(
            "=================================================\n"
        )

        return result

    finally:

        # =================================================
        # CLEAN TEMP WAV
        # =================================================

        if normalized_path:

            try:

                normalized = Path(
                    normalized_path
                )

                if normalized.exists():

                    normalized.unlink()

                    print(
                        "[STT] Temporary normalized WAV deleted."
                    )

            except Exception as error:

                print(
                    "[STT] Cleanup warning:",
                    repr(error),
                )