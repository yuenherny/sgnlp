import pathlib
import pickle
from typing import Dict, List, Optional, Tuple

from transformers import PreTrainedTokenizer


VOCAB_FILES_NAMES = {"vocab_file": "vocab.pkl"}


class SenticASGCNTokenizer(PreTrainedTokenizer):
    vocab_files_names = VOCAB_FILES_NAMES

    def __init__(
        self,
        vocab_file: str = None,
        train_files: List[str] = None,
        train_vocab: bool = False,
        do_lower_case: bool = True,
        unk_token: str = "<unk>",
        pad_token: str = "<pad>",
        **kwargs,
    ):
        super().__init__(
            do_lower_case=do_lower_case,
            unk_token=unk_token,
            pad_token=pad_token,
            **kwargs,
        )
        self.do_lower_case = do_lower_case
        if train_vocab:
            self.vocab = self.create_vocab(train_files)
        else:
            with open(vocab_file, "rb") as fin:
                self.vocab = pickle.load(fin)
        self.ids_to_tokens = {v: k for k, v in self.vocab.items()}

    @property
    def vocab_size(self):
        return len(self.vocab)

    def get_vocab(self):
        return dict(self.vocab)

    def _convert_token_to_id(self, token: str) -> int:
        return self.vocab.get(token, self.vocab.get(self.unk_token))

    def _convert_id_to_token(self, index: int) -> str:
        return self.ids_to_tokens(index, self.unk_token)

    @staticmethod
    def __read_text_file(file_names: List[str]) -> str:
        """
        Helper method to read contents of a list of text files.

        Args:
            file_names (List[str]): list of text files to read.

        Returns:
            str: return a concatenated string of text files contents.
        """
        text = ""
        for fname in file_names:
            with open(
                fname, "r", encoding="utf-8", newline="\n", errors="ignore"
            ) as fin:
                lines = fin.readlines()
            for i in range(0, len(lines), 3):
                text_left, _, text_right = [
                    s.lower().strip() for s in lines[i].partition("$T$")
                ]
                aspect = lines[i + 1].lower().strip()
                text += f"{text_left} {aspect} {text_right} "  # Left a space at the end
        return text

    def create_vocab(self, train_files: List[str]) -> Dict[str, int]:
        text = self.__read_text_file(train_files)
        if self.do_lower_case:
            text = text.lower()
        vocab = {}
        vocab[self.pad_token] = 0
        vocab[self.unk_token] = 1
        offset = len(vocab.keys())

        words = text.split()
        for word in words:
            if word not in vocab:
                vocab[word] = offset
                offset += 1
        return vocab

    def _tokenize(self, text, **kwargs):
        if self.do_lower_case:
            text = text.lower()
        words = text.split()
        return words

    def save_vocabulary(
        self, save_directory: str, filename_prefix: Optional[str] = None
    ) -> Tuple[str]:
        save_dir = pathlib.Path(save_directory)
        save_dir.mkdir(exist_ok=True)
        vocab_file_path = save_dir.joinpath("vocab.pkl")
        with open(vocab_file_path, "wb") as fout:
            pickle.dump(self.vocab, fout)
        return (str(vocab_file_path),)
