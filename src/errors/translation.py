code_translation = {
    "ENGINE_UNKNOWN_ERROR": "Er is een onbekende fout opgetreden. Probeer het later opnieuw.",
    "ENGINE_FORMAT_ERROR": "De bron mag alleen bestaan uit kleine letters, nummers en koppeltekens (-).",
    "ENGINE_FORMAT_DASH_ERROR": "De naam van een bron mag niet starten of eindigen met een koppelteken (-). Ook mogen niet meerdere koppeltekens achter elkaar.",
    "ENGINE_ALREADY_EXISTS": "Deze bron bestaat al.",
}


def translate_error(error: str) -> str:
    return code_translation.get(error, error)
