"""Adapter AWS Rekognition — extrae texto de imágenes.

Integración extra (+1.5): el usuario sube una foto de un cartel, horario
o post de DNI y el agente verifica si el contenido coincide con el corpus oficial.
"""
from __future__ import annotations
import boto3
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class RekognitionAdapter:
    """Extrae texto de imágenes usando AWS Rekognition detect_text."""

    def __init__(self) -> None:
        self.client = boto3.client(
            "rekognition",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    def extract_text(self, image_bytes: bytes) -> str:
        """Extrae texto de una imagen y devuelve las líneas unidas."""
        response = self.client.detect_text(
            Image={"Bytes": image_bytes}
        )
        lines = [
            d["DetectedText"]
            for d in response["TextDetections"]
            if d["Type"] == "LINE"
        ]
        return " ".join(lines).strip()