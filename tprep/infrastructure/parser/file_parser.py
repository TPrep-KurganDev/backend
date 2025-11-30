from starlette.datastructures import UploadFile

from tprep.infrastructure.exceptions.file_decode import FileDecode


class FileParser:
    @staticmethod
    async def parse_file(file: UploadFile) -> list[tuple[str, str]]:
        content = await file.read()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            raise FileDecode("Cant decode this file")
        cards_data: list[tuple[str, str]] = []
        lines = text.split(";")
        for line in lines:
            line = line.strip().replace("\n", "")
            if not line:
                continue
            question, answer = line.split("|")
            question.strip()
            answer.strip()
            cards_data.append((question, answer))
        return cards_data

    @staticmethod
    def check_extension(filename: str | None) -> bool:
        if filename:
            return filename.endswith((".txt", ".csv", ".log", ".md"))
        return False
