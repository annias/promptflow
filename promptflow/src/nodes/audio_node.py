from abc import ABC
from typing import Optional
import customtkinter
import openai
import wave
import numpy as np
import sounddevice as sd
from promptflow.src.flowchart import Flowchart
from promptflow.src.nodes.node_base import NodeBase


class AudioInputInterface(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Audio Input")
        self.recording = False
        self.audio_data = []
        self.filename = "out.wav"

        self.start_button = customtkinter.CTkButton(
            self, text="Start", command=self.start
        )
        self.start_button.pack()

        self.stop_button = customtkinter.CTkButton(self, text="Stop", command=self.stop)
        self.stop_button.pack()

        self.playback_button = customtkinter.CTkButton(
            self, text="Playback", command=self.playback
        )
        self.playback_button.pack()

    def start(self):
        if not self.recording:
            self.recording = True
            self.audio_data = []
            self.start_button.configure(text="Recording...")
            self.record()

    def record(self):
        if self.recording:
            duration = 1  # Record in 1-second chunks
            sample_rate = 44100
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=2,
                dtype="int16",
                blocking=True,
            )
            sd.wait()
            self.audio_data.append(recording)

            # Continue recording until stopped
            self.master.after(1, self.record)

    def stop(self):
        if self.recording:
            self.recording = False
            self.start_button.configure(text="Start")

            # Save the audio data to a file
            with wave.open(self.filename, "wb") as wf:
                sample_rate = 44100
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(np.concatenate(self.audio_data).tobytes())

    def playback(self):
        if not self.recording:
            with wave.open(self.filename, "rb") as wf:
                sample_rate = wf.getframerate()
                audio_data = np.frombuffer(
                    wf.readframes(wf.getnframes()), dtype="int32"
                )
                sd.play(audio_data, samplerate=sample_rate, blocking=True)


class AudioNode(NodeBase, ABC):
    pass


class AudioInputNode(AudioNode, ABC):
    audio_input_interface: Optional[AudioInputInterface] = None
    data: Optional[list[float]] = None

    def run_subclass(self, state) -> str:
        # show audio input interface
        self.audio_input_interface = AudioInputInterface(self.flowchart.canvas)
        self.canvas.wait_window(self.audio_input_interface)
        self.data = self.audio_input_interface.audio_data


class AudioOutputNode(AudioNode, ABC):
    pass


class WhispersNode(AudioInputNode):
    def run_subclass(self, state) -> str:
        super().run_subclass(state)
        transcript = openai.Audio.translate(
            "whisper-1", open(self.audio_input_interface.filename, "rb")
        )
        return transcript["text"]
