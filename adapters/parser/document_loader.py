# adapters/parser/document_loader.py
from __future__ import annotations
from pathlib import Path
from domain.entities import Chunk

def obtener_todos_los_chunks_del_disco(corpus_dir: Path) -> list[Chunk]:
    """Lee todos los archivos .txt del corpus y los transforma en Chunks,

    asociando inteligentemente los títulos con sus respectivos contenidos.
    """
    corpus_path = Path(corpus_dir)
    if not corpus_path.exists():
        print(f"⚠️ [DocumentLoader] Advertencia: La carpeta {corpus_dir} no existe.")
        return []

    chunks_totales = []

    for archivo_path in corpus_path.glob("*.txt"):
        nombre_fuente = archivo_path.name
        
        try:
            with open(archivo_path, "r", encoding="utf-8") as f:
                contenido = f.read()
        except UnicodeDecodeError:
            with open(archivo_path, "r", encoding="latin-1") as f:
                    contenido = f.read()

        # 1. Separación inicial por bloques vacíos
        bloques_crudos = contenido.split("\n\n")
        bloques_consolidados = []
        
        acumulador_titulo = ""
        
        for bloque in bloques_crudos:
            texto_limpio = bloque.strip()
            if not texto_limpio:
                continue
                
            # Detectamos si el bloque actual es un título/encabezado corto:
            # - Tiene una sola línea corta (menos de 60 caracteres)
            # - O está completamente en mayúsculas
            # - O empieza por marcadores de formato como '###'
            lineas = texto_limpio.split("\n")
            es_encabezado = len(lineas) == 1 and (
                len(texto_limpio) < 60 
                or texto_limpio.isupper() 
                or texto_limpio.startswith("#")
                or texto_limpio.startswith("-")
            )
            
            if es_encabezado:
                # Si ya teníamos un título acumulado previo sin texto (raro, pero posible), lo guardamos
                if acumulador_titulo:
                    bloques_consolidados.append(acumulador_titulo)
                acumulador_titulo = texto_limpio
            else:
                # Si veníamos de leer un título, lo fusionamos con este bloque de contenido
                if acumulador_titulo:
                    bloque_fusionado = f"{acumulador_titulo}\n{texto_limpio}"
                    bloques_consolidados.append(bloque_fusionado)
                    acumulador_titulo = "" # Limpiamos el acumulador
                else:
                    bloques_consolidados.append(texto_limpio)
                    
        # Limpieza final por si quedó un título suelto al final del archivo
        if acumulador_titulo:
            bloques_consolidados.append(acumulador_titulo)

        # 2. Convertimos los bloques consolidados en objetos Chunk de tu Dominio
        for idx, texto_chunk in enumerate(bloques_consolidados):
            id_unico = f"{nombre_fuente}_{idx}"
            
            chunk = Chunk(
                source=nombre_fuente,
                text=texto_chunk,
                score=0.0,
                chunk_id=id_unico
            )
            
            # Inyecciones de compatibilidad estructural
            chunk.id = id_unico
            chunk.chunk_index = idx
            
            chunks_totales.append(chunk)

    return chunks_totales