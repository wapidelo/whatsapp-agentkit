# agent/tools.py — Herramientas del agente
# Generado por AgentKit

"""
Herramientas especificas del negocio.

OJO: estas funciones NO se ejecutan solas todavia. La informacion del negocio le llega
al agente por el system prompt (config/prompts.yaml), asi que para CONTESTAR preguntas
no hace falta nada de aca. Este archivo es el lugar para las ACCIONES —calificar un lead,
abrir un ticket— y conectarlas al ciclo de tool use de Claude es un paso aparte.

Casos de uso de Wapidelo: FAQ, calificacion de leads/ventas, soporte post-venta.
"""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger("agentkit")

CARPETA_KNOWLEDGE = Path("knowledge")


def cargar_info_negocio() -> dict:
    """Carga la informacion del negocio desde config/business.yaml."""
    try:
        with open("config/business.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.error("config/business.yaml no encontrado")
        return {}


def obtener_horario() -> dict:
    """Retorna el horario de atencion del negocio."""
    info = cargar_info_negocio()
    return {
        "horario": info.get("negocio", {}).get("horario", "No disponible"),
        "esta_abierto": True,  # TODO: calcular segun la hora actual y el horario
    }


def buscar_en_knowledge(consulta: str) -> str:
    """
    Busca informacion en los archivos de /knowledge.
    Retorna los fragmentos que coinciden con la consulta.
    """
    if not CARPETA_KNOWLEDGE.is_dir():
        return "No hay archivos de conocimiento disponibles."

    resultados = []
    for ruta in sorted(CARPETA_KNOWLEDGE.iterdir()):
        if ruta.name.startswith(".") or not ruta.is_file():
            continue
        try:
            contenido = ruta.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binarios y archivos ilegibles se saltean
        if consulta.lower() in contenido.lower():
            resultados.append(f"[{ruta.name}]: {contenido[:500]}")

    if resultados:
        return "\n---\n".join(resultados)
    return "No encontre informacion especifica sobre eso en mis archivos."


# ════════════════════════════════════════════════════════════
# Leads / ventas
# ════════════════════════════════════════════════════════════


def registrar_lead(telefono: str, nombre: str, interes: str) -> dict:
    """
    Registra un prospecto nuevo. Por ahora solo lo deja en el log del servidor;
    cuando quieras guardarlos de verdad, conecta esto a una tabla, una hoja de
    calculo o tu CRM.
    """
    lead = {"telefono": telefono, "nombre": nombre, "interes": interes}
    logger.info(f"Nuevo lead: {lead}")
    return lead


def calificar_lead(cantidad_productos: int, ya_vende_por_whatsapp: bool) -> str:
    """Sugiere el plan de Wapidelo segun el tamano del negocio del prospecto."""
    if cantidad_productos <= 15:
        return "Gratis"
    if cantidad_productos <= 100:
        return "Basica"
    if cantidad_productos <= 500:
        return "Estandar"
    return "Avanzada"


def escalar_a_vendedor(telefono: str, contexto: str) -> dict:
    """Marca la conversacion para que un vendedor humano le de seguimiento."""
    aviso = {"telefono": telefono, "contexto": contexto, "escalado": True}
    logger.info(f"Lead escalado a vendedor: {aviso}")
    return aviso


# ════════════════════════════════════════════════════════════
# Soporte post-venta
# ════════════════════════════════════════════════════════════


def crear_ticket(telefono: str, problema: str) -> dict:
    """
    Abre un ticket de soporte. Por ahora solo lo deja en el log del servidor;
    cuando quieras un sistema de tickets de verdad, conecta esto a tu helpdesk.
    """
    ticket = {"telefono": telefono, "problema": problema, "estado": "abierto"}
    logger.info(f"Nuevo ticket de soporte: {ticket}")
    return ticket


def escalar_ticket(telefono: str, razon: str) -> dict:
    """Deriva el caso al equipo humano de soporte cuando el agente no puede resolverlo."""
    aviso = {"telefono": telefono, "razon": razon, "escalado": True}
    logger.info(f"Ticket escalado a soporte humano: {aviso}")
    return aviso
