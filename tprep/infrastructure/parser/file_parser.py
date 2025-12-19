from fastapi import UploadFile
from docx import Document
import pandas as pd
import io
from tprep.infrastructure.exceptions.file_decode import FileDecode
from tprep.infrastructure.exceptions.file_extension import FileExtension
from tprep.infrastructure.exceptions.file_parsing import FileParsing


class FileParser:
    @staticmethod
    async def parse_file(file: UploadFile) -> list[tuple[str, str]]:
        content = await file.read()
        file_extension = FileParser.get_extension(file.filename)

        if file_extension in (".txt", ".log", ".md"):
            return FileParser.parse_txt(content)

        elif file_extension in (".csv", ".xlsx"):
            return FileParser.parse_csv_xlsx(content, file_extension)

        elif file_extension == ".docx":
            return FileParser.parse_docx(content)

        else:
            raise FileExtension(f"Unsupported file type: {file_extension}")

    @staticmethod
    def parse_csv_xlsx(content: bytes, file_extension: str) -> list[tuple[str, str]]:
        try:
            data_io = io.BytesIO(content)

            if file_extension == ".csv":
                df = pd.read_csv(data_io, header=None)
            elif file_extension == ".xlsx":
                df = pd.read_excel(data_io, header=None)
            else:
                return []

            cards_data: list[tuple[str, str]] = []
            if df.shape[1] >= 2:
                for index, row in df.iterrows():
                    question = str(row[0]).strip() if pd.notna(row[0]) else ""
                    answer = str(row[1]).strip() if pd.notna(row[1]) else ""

                    if question and answer:
                        cards_data.append((question, answer))

            return cards_data

        except Exception:
            raise FileParsing(f"Error parsing {file_extension} file")

    @staticmethod
    def parse_docx(content: bytes) -> list[tuple[str, str]]:
        try:
            data_io = io.BytesIO(content)
            document = Document(data_io)
            cards_data: list[tuple[str, str]] = []

            for paragraph in document.paragraphs:
                line = paragraph.text.strip()
                if not line or '|' not in line:
                    continue
                try:
                    question, answer = line.split("|", 1)
                    question = question.strip()
                    answer = answer.strip()
                    if question and answer:
                        cards_data.append((question, answer))
                except ValueError:
                    continue

            return cards_data

        except Exception:
            raise FileParsing("Error parsing DOCX file")

    @staticmethod
    def parse_txt(content: bytes) -> list[tuple[str, str]]:
        try:
            text = content.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeDecodeError:
            raise FileDecode("Cant decode this file (UTF-8 expected)")

        cards_data: list[tuple[str, str]] = []
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line or '|' not in line:
                continue
            try:
                question, answer = line.split("|", 1)
                question = question.strip()
                answer = answer.strip()
                if question and answer:
                    cards_data.append((question, answer))
            except ValueError:
                continue

        return cards_data

    @staticmethod
    def check_extension(filename: str) -> bool:
        supported_extensions = {".txt", ".csv", ".log", ".md", ".xlsx", ".docx"}
        extension = FileParser.get_extension(filename)
        if extension:
            return extension in supported_extensions
        return False

    @staticmethod
    def get_extension(filename: str | None) -> str | None:
        if filename and "." in filename:
            return "." + filename.rsplit(".", 1)[-1].lower()
        return None
