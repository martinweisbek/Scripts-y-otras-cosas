import numpy as np

def DibujarTabla(matriz_tabla:np.ndarray):

    ValorX = "| X |"
    ValorO = "| O |"
    SinValor = "|   |"
    

    for fila in matriz_tabla:
        
        for i in range(0,len(fila)):
            print("+---+", end= " ")
        print()
        for dato in fila:
            if(dato == True):
                print(ValorX, end=" ")
            elif (dato == False):
                print(ValorO, end=" ")
            else:
                print(SinValor, end=" ")
        print()

    for i in range(0,len(fila)):
        print("+---+", end= " ")

    print()
    
def ElegirSimbolo(jugadores : dict) -> dict:
    DictSimbolos = {"X": 1, "O": 0}  
    ListaSimbolos = ["X", "O"]
    simbolos = {
        jugadores["p1"] : None,
        jugadores["p2"] : None
    }

    p1_simbolo = input(f'{jugadores["p1"]}, seleccione X/O: ').upper()

    while(p1_simbolo not in ListaSimbolos):
        print("Error - Las opciones son X | O")
        p1_simbolo = input(f'{jugadores["p1"]}, seleccione X/O: ').upper()
    
    if(p1_simbolo == "X"):
        simbolos[jugadores["p1"]] = DictSimbolos["X"]
        simbolos[jugadores["p2"]] = DictSimbolos["O"]
    else:
        simbolos[jugadores["p1"]] = DictSimbolos["O"]
        simbolos[jugadores["p2"]] = DictSimbolos["X"]

    return simbolos

    
def ChequeoColumnas(matriz_tabla:np.ndarray) -> int:

    ganaX = [1,1,1]
    ganaO = [0,0,0]
    for columna in matriz_tabla.tolist():
        if(columna == ganaX):
            return 1
        elif(columna == ganaO):
            return 0
        
    return -1

def ChequeoFilas(matriz_tabla:np.ndarray) -> int:
    print()
    tamanioMatrix = len(matriz_tabla)
    Fila = []
    ListaMatrix = []
    ganaX = [1,1,1]
    ganaO = [0,0,0]

    for i in range(0,tamanioMatrix):
        for j in range(0,tamanioMatrix):
            Fila.append(matriz_tabla[j][i])
        ListaMatrix.append(Fila)
        Fila = []

    for fila in ListaMatrix:
        if(fila == ganaX):
            return 1
        elif(fila == ganaO):
            return 0
        
    return -1
                    
def ChequeoDiagonal_1(matriz_tabla:np.ndarray) -> int:
    print()
    tamanioMatriz = len(matriz_tabla)

    ListaDiagonal = []
    ganaX = [1,1,1]
    ganaO = [0,0,0]
    
    #Recorro la primera diagonal
    for i in range(0,tamanioMatriz):
        ListaDiagonal.append(matriz_tabla[i][i])

    if(ListaDiagonal == ganaX):
        return 1
    elif(ListaDiagonal == ganaO):
        return 0

    return -1

def ChequeoDiagonal_2(matriz_tabla:np.ndarray) -> int:
    print()
    tamanioMatriz = len(matriz_tabla)

    ListaDiagonal = []
    ganaX = [1,1,1]
    ganaO = [0,0,0]
    
    #Recorro la segunda diagonal
    for i in range(0,tamanioMatriz):
        tamanioMatriz = tamanioMatriz - 1
        ListaDiagonal.append(matriz_tabla[tamanioMatriz][i])
    
    if(ListaDiagonal == ganaX):
        return 1
    elif(ListaDiagonal == ganaO):
        return 0
        
    return -1


def ChequeoEmpate(matriz_tabla:np.ndarray) -> bool:

    for i in matriz_tabla:
        for j in i:
            if j == None:
                return False
    print("Hubo un empate!")
    return True


"""
    1) Al menos una columna tiene los mismos simbolos
    2) Al menos una fila tiene los mismos simbolos
    3) Reviso diagonales
        3.1) 00, 11,22
        3.2) 12, 11,20

"""
def CheckGanador(matriz_tabla : np.ndarray, simbolos : dict) -> bool:

    if (ChequeoEmpate(matriz_tabla)): return True

    resultado = ChequeoColumnas(matriz_tabla)
    if(resultado == -1):
        resultado = ChequeoFilas(matriz_tabla)
        if (resultado == -1):
            resultado = ChequeoDiagonal_1(matriz_tabla)
            if (resultado == -1):
                resultado = ChequeoDiagonal_2(matriz_tabla)
                if (resultado != -1):
                    nombre = list(simbolos.keys())[list(simbolos.values()).index(resultado)]
                    print(f"{nombre} ganó la partida")
            else:
                nombre = list(simbolos.keys())[list(simbolos.values()).index(resultado)]
                print(f"{nombre} ganó la partida")
        else:
            nombre = list(simbolos.keys())[list(simbolos.values()).index(resultado)]
            print(f"{nombre} ganó la partida")
    else:
        nombre = list(simbolos.keys())[list(simbolos.values()).index(resultado)]
        print(f"{nombre} ganó la partida")
    
    if(resultado == -1):
        return False
    else:
        return True




def main():

    jugadores = {
        "p1" : "",
        "p2" : ""
    }

    turno = "p1"
    matriz_tabla = np.array([[None,None,None],
                             [None,None,None],
                             [None,None,None]])

    print("--- TA TE TI ---")

    p1 = input("Ingrese el nombre del jugador 1: ")
    p2 = input("Ingrese el nombre del jugador 2: ")

    jugadores["p1"] = p1
    jugadores["p2"] = p2

    print(jugadores["p1"])
    simbolos = ElegirSimbolo(jugadores)

    print(f"Comienza {jugadores[turno]}.")
    DibujarTabla(matriz_tabla)
    while (CheckGanador(matriz_tabla,simbolos) == False):
        columna = input(f"{jugadores[turno]} ingrese numero de columna: ")
        fila = input(f"{jugadores[turno]} ingrese numero de fila: ")

        if(columna.isnumeric() and fila.isnumeric()):
            columna = int (columna)
            fila = int(fila)
            if (columna > 0 and columna <= 3 and fila > 0 and fila <= 3):
                columna = columna - 1
                fila = fila - 1
                if(matriz_tabla[fila][columna] != None):
                    print("Esa posicion ya esta ocupada. Elija otra")
                    DibujarTabla(matriz_tabla)
                else:
                    matriz_tabla[fila][columna] = simbolos[jugadores[turno]]
                    if(turno == "p1"): turno = "p2"
                    elif(turno == "p2"): turno = "p1"
                    DibujarTabla(matriz_tabla)
            else:
                print("ERROR - Ingrese solo valores numericos del 1 al 3")
        else:
            print("ERROR - Ingrese solo valores numericos del 1 al 3")


if __name__ == "__main__":

    main()




