from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.model import ModelInfo

import numpy as np
import threading
import soundcard
import json
import vosk


class SubtitleGenerator(threading.Thread):
    def __init__(
        self,
        model_path: str,
        model_info: ModelInfo,
        blocksize: int = 1024,
    ) -> None:
        super().__init__(name="SubtitleGenerator")

        self.model_info = model_info
        self.blocksize = blocksize

        self.text = []
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)

        self.error = None
        self.running = False

    def __process_audio(self, data) -> tuple[bool | None, str | None]:
        audio_int16 = (data * 32767).astype(np.int16).tobytes()

        if self.recognizer.AcceptWaveform(audio_int16):
            return False, json.loads(self.recognizer.Result())["text"]
        else:
            partial = json.loads(self.recognizer.PartialResult())
            if partial.get("partial"):
                return True, partial["partial"]
        return None, None

    def run(self) -> None:
        self.running = True

        speaker = soundcard.default_speaker()

        with soundcard.get_microphone(
            id=str(speaker.name), include_loopback=True
        ).recorder(samplerate=16000, channels=1) as fake_microphone:
            while self.running:
                is_partial, current_text = self.__process_audio(
                    fake_microphone.record(numframes=self.blocksize)
                )
                if is_partial == None:
                    continue

                if len(self.text) == 0:
                    self.text.append("")
                self.text[-1] = current_text
                if not is_partial:
                    self.text.append("")

    @property
    def display_text(self) -> str:
        return "\n".join(self.text)

    def stop(self) -> None:
        self.running = False
