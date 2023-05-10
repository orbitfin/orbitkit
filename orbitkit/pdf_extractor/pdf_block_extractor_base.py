from abc import abstractmethod
import abc


class PdfBlockExtractBase(metaclass=abc.ABCMeta):
    """Interface for pdf extractor."""

    @abstractmethod
    def extract(self):
        """Main method for extract
        """
        raise NotImplementedError

    def _sentence_filter(self, sentence: str):
        sentence = sentence.strip()
        is_valid_sentence = True
        if sentence == '':
            is_valid_sentence = False
        if len(sentence) < 3:
            is_valid_sentence = False
        return {
            'sentence': sentence,
            'is_valid_sentence': is_valid_sentence,
        }
