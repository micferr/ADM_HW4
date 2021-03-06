# The utilities in the provided helper notebook, in a simple Python file for simplicity.

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile
import subprocess
import librosa
import librosa.display
import IPython.display as ipd

from pathlib import Path, PurePath
from tqdm.notebook import tqdm

N_TRACKS = 1413
HOP_SIZE = 512
OFFSET = 1.0
DURATION = 10
THRESHOLD = 0
data_folder = Path("datasets/mp3s-32k/")
mp3_tracks = data_folder.glob("*/*/*.mp3")
tracks = data_folder.glob("*/*/*.wav")


ECHONEST_PATH = Path("datasets/ex2/echonest.csv")
FEATURES_PATH = Path("datasets/ex2/features.csv")
TRACKS_PATH = Path("datasets/ex2/tracks.csv")
MERGED_DATASET_PATH = Path("merged_dataset.csv")

def convert_mp3_to_wav(audio: str) -> str:
    """Convert an input MP3 audio track into a WAV file.

    Args:
        audio (str): An input audio track.

    Returns:
        [str]: WAV filename.
    """
    if audio[-3:] == "mp3":
        wav_audio = audio[:-3] + "wav"
        if not Path(wav_audio).exists():
            subprocess.check_output(f"ffmpeg -i {audio} {wav_audio}", shell=True)
        return wav_audio

    return audio


def plot_spectrogram_and_peaks(track: np.ndarray, sr: int, peaks: np.ndarray, onset_env: np.ndarray) -> None:
    """Plots the spectrogram and peaks

    Args:
        track (np.ndarray): A track.
        sr (int): Aampling rate.
        peaks (np.ndarray): Indices of peaks in the track.
        onset_env (np.ndarray): Vector containing the onset strength envelope.
    """
    times = librosa.frames_to_time(np.arange(len(onset_env)),
                                   sr=sr, hop_length=HOP_SIZE)

    plt.figure()
    ax = plt.subplot(2, 1, 2)
    D = librosa.stft(track)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(D), ref=np.max),
                             y_axis='log', x_axis='time')
    plt.subplot(2, 1, 1, sharex=ax)
    plt.plot(times, onset_env, alpha=0.8, label='Onset strength')
    plt.vlines(times[peaks], 0,
               onset_env.max(), color='r', alpha=0.8,
               label='Selected peaks')
    plt.legend(frameon=True, framealpha=0.8)
    plt.axis('tight')
    plt.tight_layout()
    plt.show()


def load_audio_peaks(audio, offset, duration, hop_size):
    """Load the tracks and peaks of an audio.

    Args:
        audio (string, int, pathlib.Path or file-like object): [description]
        offset (float): start reading after this time (in seconds)
        duration (float): only load up to this much audio (in seconds)
        hop_size (int): the hop_length

    Returns:
        tuple: Returns the audio time series (track) and sampling rate (sr), a vector containing the onset strength envelope
        (onset_env), and the indices of peaks in track (peaks).
    """
    try:
        track, sr = librosa.load(audio, offset=offset, duration=duration)
        onset_env = librosa.onset.onset_strength(track, sr=sr, hop_length=hop_size)
        peaks = librosa.util.peak_pick(onset_env, 10, 10, 10, 10, 0.5, 0.5)
    except Exception as e:
        print('An error occurred processing ', str(audio))
        print(e)

    return track, sr, onset_env, peaks


def convert_all_mp3s():
    for track in tqdm(mp3_tracks, total=N_TRACKS):
        convert_mp3_to_wav(str(track))
    print('Done!')


def plot_tracks():
    for idx, audio in enumerate(tracks):
        if idx >= 2:
            break
        track, sr, onset_env, peaks = load_audio_peaks(audio, OFFSET, DURATION, HOP_SIZE)
        plot_spectrogram_and_peaks(track, sr, peaks, onset_env)