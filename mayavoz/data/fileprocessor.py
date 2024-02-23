import glob
import os

import numpy as np
from scipy.io import wavfile

MATCHING_FNS = ("one_to_one", "one_to_many")


class ProcessorFunctions:
    """
    Preprocessing methods for different types of speech enhacement datasets.
    """

    @staticmethod
    def one_to_one(clean_path, noisy_path):
        """
        One clean audio can have only one noisy audio file
        """

        matching_wavfiles = list()
        clean_filenames = [
            os.path.split(file)[-1]
            for file in glob.glob(os.path.join(clean_path, "*.wav"))
        ]
        noisy_filenames = [
            os.path.split(file)[-1]
            for file in glob.glob(os.path.join(noisy_path, "*.wav"))
        ]

        common_filenames = np.intersect1d(noisy_filenames, clean_filenames)

        for file_name in common_filenames:

            sr_clean, clean_file = wavfile.read(
                os.path.join(clean_path, file_name)
            )
            sr_noisy, noisy_file = wavfile.read(
                os.path.join(noisy_path, file_name)
            )

            if (clean_file.shape[-1] == noisy_file.shape[-1]) and (
                sr_clean == sr_noisy
            ):
                matching_wavfiles.append(
                    {
                        "clean": os.path.join(clean_path, file_name),
                        "noisy": os.path.join(noisy_path, file_name),
                        "duration": clean_file.shape[-1] / sr_clean,
                    }
                )
        return matching_wavfiles

    @staticmethod
    def one_to_many(clean_path, noisy_path):
        """
        One clean audio have multiple noisy audio files
        """

        matching_wavfiles = list()
        clean_filenames = [
            os.path.split(file)[-1]
            for file in glob.glob(os.path.join(clean_path, "*.wav"))
        ]
        for clean_file in clean_filenames:
            noisy_filenames = glob.glob(
                os.path.join(noisy_path, f"*_{clean_file}")
            )
            for noisy_file in noisy_filenames:

                sr_clean, clean_wav = wavfile.read(
                    os.path.join(clean_path, clean_file)
                )
                sr_noisy, noisy_wav = wavfile.read(noisy_file)
                if (clean_wav.shape[-1] == noisy_wav.shape[-1]) and (
                    sr_clean == sr_noisy
                ):
                    matching_wavfiles.append(
                        {
                            "clean": os.path.join(clean_path, clean_file),
                            "noisy": noisy_file,
                            "duration": clean_wav.shape[-1] / sr_clean,
                        }
                    )
        return matching_wavfiles


class Fileprocessor:
    def __init__(self, clean_dir, noisy_dir, matching_function=None):
        self.clean_dir = clean_dir
        self.noisy_dir = noisy_dir
        self.matching_function = matching_function

    @classmethod
    def from_name(cls, name: str, clean_dir, noisy_dir, matching_function=None):

        if matching_function is None:
            if name.lower() in ("vctk", "valentini"):
                return cls(clean_dir, noisy_dir, ProcessorFunctions.one_to_one)
            elif name.lower() == "ms-snsd":
                return cls(clean_dir, noisy_dir, ProcessorFunctions.one_to_many)
            else:
                raise ValueError(
                    f"Invalid matching function, Please use valid matching function from {MATCHING_FNS}"
                )
        else:
            if matching_function not in MATCHING_FNS:
                raise ValueError(
                    f"Invalid matching function! Avaialble options are {MATCHING_FNS}"
                )
            else:
                return cls(
                    clean_dir,
                    noisy_dir,
                    getattr(ProcessorFunctions, matching_function),
                )

    def prepare_matching_dict(self):

        if self.matching_function is None:
            raise ValueError("Not a valid matching function")

        return self.matching_function(self.clean_dir, self.noisy_dir)
