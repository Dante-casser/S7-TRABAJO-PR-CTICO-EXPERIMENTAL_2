import os


def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def imprimir_titulo(texto):
    print("\n" + "=" * 50)
    print(f"  {texto}")
    print("=" * 50)


def imprimir_exito(texto):
    print(f"[EXITO] {texto}")


def imprimir_error(texto):
    print(f"[ERROR] {texto}")


def imprimir_info(texto):
    print(f"[INFO] {texto}")


def confirmar(pregunta):
    respuesta = input(f"{pregunta} (s/n): ").strip().lower()
    return respuesta in ("s", "si", "y", "yes")
