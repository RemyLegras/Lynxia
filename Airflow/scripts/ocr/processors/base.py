from abc import ABC, abstractmethod

class DocumentProcessor(ABC):
    @abstractmethod
    def can_handle(self, text_up: str) -> bool:
        """Détermine si ce processeur est capable de traiter ce document."""
        pass

    @abstractmethod
    def process(self, result, text_up: str) -> dict:
        """Extrait les données spécifiques au type de document."""
        pass