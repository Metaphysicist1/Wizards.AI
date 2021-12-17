import librosa
import soundfile as sf

audio, sr = librosa.load("/home/edgar/Documents/API/maybe-next-time.wav", mono=True)

sf.write('stereo_file.wav', audio, sr, 'PCM_16')


