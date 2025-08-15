from pyaudio import PyAudio


class PlayWavAudio:
    def __init__(self, audio_measurement):
        self.pyaudio = PyAudio()
        self.audio_data = audio_measurement.audio
        self.stream = self.pyaudio.open(
            format=self.pyaudio.get_format_from_width(self.audio_data.depth / 8),
            channels=self.audio_data.channels,
            rate=self.audio_data.sampling_rate,
            output=True,
        )

    def play(self):
        self.stream.write(self.audio_data.data)

    def close(self):
        self.stream.close()
        self.pyaudio.terminate()


def play_audio(audio_measurement):
    play = PlayWavAudio(audio_measurement)
    play.play()
    play.close()
