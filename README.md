# DSL de procesamiento de imágenes

Proyecto académico para el Tema 31 de Teoría de Lenguajes Formales. Modela un
lenguaje que describe operaciones ordenadas sobre una imagen y genera árboles
de derivación a partir de expansiones indicadas por el usuario.

El proyecto **no procesa archivos de imagen, no comprueba la validez semántica
de los parámetros y no infiere una derivación a partir de una cadena**.

## Sección I. Gramática independiente del contexto

La gramática es `G = (V, Σ, R, S)`.

- `V = {PROGRAMA, OPERACIONES, OPERACION, RECORTE, ESCALA, ROTACION, FILTRO,
  NOMBRE_FILTRO}`.
- `Σ` contiene las palabras clave y signos literales, además de los tokens
  léxicos `IDENT` y `NUM`.
- `S = PROGRAMA`.
- `R` está definida en la sección II.

`IDENT` y `NUM` son clases de tokens terminales, no no terminales de la GIC.
En la herramienta se pueden expandir como sustituciones léxicas opcionales
(por ejemplo, `IDENT → foto`) para que las hojas del árbol muestren los
lexemas concretos. Estas sustituciones de ejemplo no cambian la gramática
sintáctica.

## Sección II. BNF y EBNF

### BNF

```bnf
<programa> ::= "imagen" IDENT "{" <operaciones> "}"
<operaciones> ::= <operacion>
                | <operacion> ";" <operaciones>
<operacion> ::= <recorte> | <escala> | <rotacion> | <filtro>
<recorte> ::= "recortar" "(" NUM "," NUM "," NUM "," NUM ")"
<escala> ::= "escalar" "(" NUM "," NUM ")"
<rotacion> ::= "rotar" "(" NUM ")"
<filtro> ::= "filtro" "(" <nombre_filtro> ")"
<nombre_filtro> ::= "desenfoque" | "nitidez"
                  | "escala_grises" | "sepia"
```

### EBNF

```ebnf
programa = "imagen", IDENT, "{", operacion, { ";", operacion }, "}" ;
operacion = recorte | escala | rotacion | filtro ;
recorte = "recortar", "(", NUM, ",", NUM, ",", NUM, ",", NUM, ")" ;
escala = "escalar", "(", NUM, ",", NUM, ")" ;
rotacion = "rotar", "(", NUM, ")" ;
filtro = "filtro", "(", nombre_filtro, ")" ;
nombre_filtro = "desenfoque" | "nitidez" | "escala_grises" | "sepia" ;
```

La recursividad por la derecha en BNF equivale a repetir cero o más pares
`";", operacion` en EBNF. Se requiere al menos una operación y no se admite
un punto y coma final.

## Sección III. Derivaciones y árboles

El programa incluye dos derivaciones completas precargadas:

```text
python -m imagen_dsl --example w1
python -m imagen_dsl --example w2
```

`w1` deriva `imagen foto { recortar(10, 20, 300, 200); filtro(sepia) }`
por la izquierda. `w2` deriva
`imagen paisaje { escalar(800, 600); rotar(90); filtro(escala_grises) }`
por la derecha. Ambas salidas muestran el árbol y la cadena terminal.

Una cadena como `imagen foto { recortar(10, 20, 300); filtro(sepia) }` no
puede derivarse: `recortar` requiere cuatro parámetros numéricos.

## Sección IV. Ambigüedad y precedencia

Una alternativa problemática sería
`<operaciones> ::= <operaciones> ";" <operaciones> | <operacion>`.
Permite agrupar `A; B; C` como `(A; B); C` o como `A; (B; C)`, por lo que es
ambigua. La definición recursiva por la derecha de la sección II fija la
agrupación de la lista. No hay operadores aritméticos ni precedencia entre
transformaciones: se ejecutan en el orden textual, aunque este proyecto solo
representa la sintaxis.

## Sección V. Generador de árboles en Python

La entrada contiene la gramática, el símbolo inicial, la estrategia
(`leftmost` o `rightmost`) y los pasos. Cada paso indica la alternativa que se
aplica al siguiente no terminal según la estrategia. Las alternativas se
numeran desde cero. El generador valida cada expansión, informa errores de
secuencia o de gramática y rechaza derivaciones incompletas.

#### Clases y relación entre ellas

- `Grammar` guarda el símbolo inicial y las producciones de la GIC; su método
  `validate()` comprueba su estructura.
- `DerivationStep` representa una expansión solicitada: el no terminal y el
  índice de la alternativa elegida.
- `build_derivation(grammar, steps, strategy)` recibe esos datos, selecciona
  el siguiente no terminal y crea un `Node` por cada símbolo del lado derecho
  de la regla. No infiere reglas desde una cadena.
- `Node` es la unidad del árbol: contiene el símbolo y sus hijos. El nodo raíz
  corresponde al símbolo inicial; los terminales quedan como hojas.
- `render_tree(root)` muestra los nodos jerárquicamente en texto;
  `render_svg(root)` crea una versión gráfica y `yield_string(root)` concatena
  las hojas para mostrar la cadena terminal.
- `DerivationError` informa gramáticas o pasos inválidos. En modo consola,
  `_load_request()` convierte el JSON en `Grammar` y `DerivationStep`, y
  `main()` coordina la construcción y la presentación del árbol.

### Ejecutar

Requiere Python 3.10 o posterior; no necesita dependencias externas.

```text
python -m imagen_dsl --example w1
python -m imagen_dsl --example w2
python -m imagen_dsl --example w1 --svg
python -m imagen_dsl --example w2 --svg
python -m unittest discover -s tests -v
```

Las opciones `--svg` generan `arbol_w1.svg` o `arbol_w2.svg` en la carpeta
actual. Abra el archivo con un navegador para explorar el árbol gráfico.
También se puede elegir la ubicación y el nombre con `--output`, por ejemplo:
`python -m imagen_dsl --example w1 --output imagenes\mi_arbol.svg`.

### Recorrer la derivación de forma visual

Abra `visualizador_derivaciones.html` en un navegador para avanzar y retroceder
por cada expansión, reproducir los pasos y observar el árbol y la forma
sentencial. Incluye `w1` y `w2`; también permite cargar una derivación JSON con
el mismo formato que usa la herramienta de consola. No requiere servidor ni
instalaciones.

El apartado **Comprobar una cadena del DSL** permite escribir un programa y
verificar su sintaxis. Por ejemplo,
`imagen foto { recortar(10, 20, 300); filtro(sepia) }` se reporta como inválido
porque `recortar` requiere cuatro parámetros. Esta comprobación solo valida la
sintaxis; no valida las dimensiones ni procesa imágenes.

Para una derivación propia, guarde un JSON con esta forma y ejecútelo como
`python -m imagen_dsl ruta\derivacion.json`:

```json
{
  "start_symbol": "S",
  "strategy": "leftmost",
  "productions": {
    "S": [["a", "A"]],
    "A": [["b"]]
  },
  "steps": [
    {"symbol": "S", "alternative": 0},
    {"symbol": "A", "alternative": 0}
  ]
}
```

Las cadenas RHS se representan como listas ordenadas de símbolos. Un símbolo
es expandible si aparece como clave en `productions`; los demás se convierten
en hojas terminales.
