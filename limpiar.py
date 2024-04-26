import re

def limpiar_cadena(cadena):
    """
    Elimina los caracteres no imprimibles al principio y al final de la cadena.
    
    Args:
        cadena (str): La cadena que se desea limpiar.
    
    Returns:
        str: La cadena limpia.
    """
    return re.sub(r'^[\s\x00-\x1f\x7f-\xff]*|[\s\x00-\x1f\x7f-\xff]*$', '', cadena, flags=re.MULTILINE)

# Ejemplo de uso:
cadena_con_caracteres_ocultos = ' 0.028 \r 0.028 '
cadena_limpia = limpiar_cadena(cadena_con_caracteres_ocultos)
print("Cadena original:", repr(cadena_con_caracteres_ocultos))
print("Cadena limpia:", repr(cadena_limpia))
