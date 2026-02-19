"""
Procedural music generator for My Kingdom.
Creates relaxing medieval/fantasy ambient music.
"""

import numpy as np
import wave
import struct
from pathlib import Path
from src.core.logger import logger


class MusicGenerator:
    """Generate relaxing medieval fantasy music procedurally."""

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def generate_sine_wave(self, frequency, duration, amplitude=0.3):
        """Generate a sine wave."""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        wave = amplitude * np.sin(2 * np.pi * frequency * t)
        return wave

    def apply_envelope(self, wave, attack=0.1, decay=0.1, sustain=0.7, release=0.2):
        """Apply ADSR envelope to a wave."""
        total_duration = len(wave) / self.sample_rate
        samples = len(wave)

        attack_samples = int(attack * total_duration * self.sample_rate)
        decay_samples = int(decay * total_duration * self.sample_rate)
        release_samples = int(release * total_duration * self.sample_rate)
        sustain_samples = samples - attack_samples - decay_samples - release_samples

        envelope = np.ones(samples)

        # Attack
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay
        decay_end = attack_samples + decay_samples
        envelope[attack_samples:decay_end] = np.linspace(1, sustain, decay_samples)

        # Sustain
        sustain_end = decay_end + sustain_samples
        envelope[decay_end:sustain_end] = sustain

        # Release
        envelope[sustain_end:] = np.linspace(sustain, 0, release_samples)

        return wave * envelope

    def generate_chord(self, base_freq, duration, chord_type='major'):
        """Generate a chord (multiple notes)."""
        # Define chord intervals
        if chord_type == 'major':
            intervals = [1.0, 1.25, 1.5]  # Root, major third, perfect fifth
        elif chord_type == 'minor':
            intervals = [1.0, 1.2, 1.5]  # Root, minor third, perfect fifth
        else:
            intervals = [1.0, 1.5]  # Power chord (root and fifth)

        chord = np.zeros(int(duration * self.sample_rate))
        for interval in intervals:
            note = self.generate_sine_wave(base_freq * interval, duration, amplitude=0.15)
            note = self.apply_envelope(note)
            chord += note

        return chord

    def add_reverb(self, wave, delay=0.05, decay=0.3):
        """Add simple reverb effect."""
        delay_samples = int(delay * self.sample_rate)
        reverb = np.zeros(len(wave) + delay_samples)
        reverb[:len(wave)] = wave
        reverb[delay_samples:] += wave * decay
        return reverb[:len(wave)]

    def generate_menu_music(self, duration=120):
        """
        Generate upbeat menu music with shorter notes.
        Think: Stardew Valley, Minecraft - cheerful medieval fantasy.
        """
        logger.info(f"Generating menu music ({duration}s)...")

        # Use pentatonic scale for a cheerful, medieval sound
        # C major pentatonic: C, D, E, G, A
        pentatonic = [
            261.63,  # C4
            293.66,  # D4
            329.63,  # E4
            392.00,  # G4
            440.00,  # A4
            523.25,  # C5
            587.33,  # D5
        ]

        total_samples = int(duration * self.sample_rate)
        music = np.zeros(total_samples)

        # Faster chord progression (2 seconds per chord)
        chord_duration = 2.0
        num_chords = int(duration / chord_duration)

        # Upbeat chord progression
        chord_progression = [
            (pentatonic[0], 'major'),   # C major
            (pentatonic[3], 'major'),   # G major
            (pentatonic[4], 'minor'),   # A minor
            (pentatonic[3], 'major'),   # G major
        ]

        current_sample = 0

        # Create melody patterns (shorter notes - 0.25 to 0.5 seconds)
        melody_pattern = [
            (0, 0.3), (2, 0.3), (4, 0.4), (3, 0.3), (1, 0.3), (2, 0.4),
            (4, 0.3), (5, 0.3), (4, 0.4), (2, 0.3), (0, 0.5),
        ]
        melody_idx = 0

        for i in range(num_chords):
            chord_idx = i % len(chord_progression)
            base_freq, chord_type = chord_progression[chord_idx]

            # Generate chord (background)
            chord = self.generate_chord(base_freq * 0.5, chord_duration, chord_type)

            # Add melody with shorter notes
            melody = np.zeros(int(chord_duration * self.sample_rate))
            time_offset = 0

            while time_offset < chord_duration:
                note_idx, note_duration = melody_pattern[melody_idx % len(melody_pattern)]
                melody_idx += 1

                if time_offset + note_duration > chord_duration:
                    break

                melody_freq = pentatonic[note_idx]
                note = self.generate_sine_wave(melody_freq, note_duration, amplitude=0.12)
                note = self.apply_envelope(note, attack=0.05, decay=0.1, sustain=0.7, release=0.15)

                start_sample = int(time_offset * self.sample_rate)
                end_sample = min(start_sample + len(note), len(melody))
                melody[start_sample:end_sample] += note[:end_sample - start_sample]

                time_offset += note_duration

            # Combine
            combined = chord + melody
            combined = self.add_reverb(combined, delay=0.03, decay=0.2)

            # Add to music
            end_sample = min(current_sample + len(combined), total_samples)
            samples_to_add = end_sample - current_sample
            music[current_sample:end_sample] += combined[:samples_to_add]

            current_sample = end_sample
            if current_sample >= total_samples:
                break

        # Normalize
        max_amplitude = np.max(np.abs(music))
        if max_amplitude > 0:
            music = music / max_amplitude * 0.6

        logger.info("Menu music generated successfully")
        return music

    def generate_game_music(self, duration=180):
        """
        Generate upbeat gameplay music with melody.
        More active and engaging, but still relaxing.
        """
        logger.info(f"Generating gameplay music ({duration}s)...")

        # Pentatonic scale for gameplay
        pentatonic = [
            196.00,  # G3
            220.00,  # A3
            246.94,  # B3
            293.66,  # D4
            329.63,  # E4
            392.00,  # G4
            440.00,  # A4
        ]

        total_samples = int(duration * self.sample_rate)
        music = np.zeros(total_samples)

        # Medium tempo chord progression (3 seconds per chord)
        chord_duration = 3.0
        num_chords = int(duration / chord_duration)

        # Gameplay chord progression
        chord_progression = [
            (pentatonic[0], 'major'),   # G major
            (pentatonic[3], 'major'),   # D major
            (pentatonic[1], 'minor'),   # A minor
            (pentatonic[4], 'minor'),   # E minor
        ]

        current_sample = 0

        # Longer melody pattern for gameplay (0.4 to 0.8 seconds)
        melody_pattern = [
            (3, 0.5), (4, 0.5), (5, 0.6), (4, 0.4), (3, 0.5), (1, 0.8),
            (0, 0.6), (1, 0.5), (3, 0.5), (4, 0.6), (3, 0.5), (1, 0.7),
            (4, 0.5), (5, 0.5), (6, 0.6), (5, 0.5), (4, 0.6), (3, 0.8),
        ]
        melody_idx = 0

        for i in range(num_chords):
            chord_idx = i % len(chord_progression)
            base_freq, chord_type = chord_progression[chord_idx]

            # Generate chord (background)
            chord = self.generate_chord(base_freq * 0.5, chord_duration, chord_type)

            # Add melody with medium-length notes
            melody = np.zeros(int(chord_duration * self.sample_rate))
            time_offset = 0

            while time_offset < chord_duration:
                note_idx, note_duration = melody_pattern[melody_idx % len(melody_pattern)]
                melody_idx += 1

                if time_offset + note_duration > chord_duration:
                    break

                melody_freq = pentatonic[note_idx]
                note = self.generate_sine_wave(melody_freq, note_duration, amplitude=0.1)
                note = self.apply_envelope(note, attack=0.08, decay=0.12, sustain=0.65, release=0.2)

                start_sample = int(time_offset * self.sample_rate)
                end_sample = min(start_sample + len(note), len(melody))
                melody[start_sample:end_sample] += note[:end_sample - start_sample]

                time_offset += note_duration

            # Add bass note for depth
            bass = self.generate_sine_wave(base_freq * 0.25, chord_duration, amplitude=0.08)
            bass = self.apply_envelope(bass, attack=0.1, release=0.3)

            # Combine
            combined = chord + melody + bass
            combined = self.add_reverb(combined, delay=0.05, decay=0.25)

            # Add to music
            end_sample = min(current_sample + len(combined), total_samples)
            samples_to_add = end_sample - current_sample
            music[current_sample:end_sample] += combined[:samples_to_add]

            current_sample = end_sample
            if current_sample >= total_samples:
                break

        # Normalize
        max_amplitude = np.max(np.abs(music))
        if max_amplitude > 0:
            music = music / max_amplitude * 0.55

        logger.info("Gameplay music generated successfully")
        return music

    def save_wav(self, audio_data, filename):
        """Save audio data as WAV file."""
        # Convert to 16-bit PCM
        audio_data = np.clip(audio_data, -1.0, 1.0)
        audio_data = (audio_data * 32767).astype(np.int16)

        # Write WAV file
        with wave.open(str(filename), 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())

        logger.info(f"Saved audio to {filename}")


def generate_all_music():
    """Generate all music tracks for the game."""
    music_dir = Path(__file__).parent.parent.parent / "assets" / "audio" / "music"
    music_dir.mkdir(parents=True, exist_ok=True)

    generator = MusicGenerator()

    # Generate menu music (2 minutes, will loop)
    menu_music = generator.generate_menu_music(duration=120)
    generator.save_wav(menu_music, music_dir / "menu_theme.wav")

    # Generate gameplay music (3 minutes, will loop)
    game_music = generator.generate_game_music(duration=180)
    generator.save_wav(game_music, music_dir / "gameplay_theme.wav")

    logger.info("All music tracks generated!")


if __name__ == "__main__":
    generate_all_music()
