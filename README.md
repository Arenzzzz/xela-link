# Xela Link

Red social de escritorio en Python que encuentra, con el algoritmo de Dijkstra, la cadena de amistades más corta entre dos usuarios, y valida rutas como cadenas de un autómata finito determinista ponderado.

Proyecto final de **Lenguajes Formales y Autómatas**, Universidad Rafael Landívar, Campus Quetzaltenango. Grupo 6.

## Integrantes y roles

| Integrante | Rol | Archivos |
|---|---|---|
| Moshé Arenz Peláez Virula | Modelo técnico: grafo, Dijkstra, integración | `modelo/grafo.py`, `modelo/dijkstra.py`, `main.py` |
| Cristhian Estuardo De León Pérez | Autómata y modelo formal | `modelo/automata.py` |
| Ángel Emmanuel Rodas Berreondo | Interfaz gráfica | `interfaz/login.py`, `interfaz/ventana_principal.py` |
| Pedro Antonio Monroy Rímola | Datos y visualización | `datos/gestor_json.py`, `datos/usuarios.json`, `interfaz/vista_grafo.py` |
| Keila Belinda Puac Gómez | Informe y pruebas | `docs/`, `pruebas/` |

## Cómo ejecutar

```bash
pip install -r requirements.txt
python main.py
```

Pruebas:

```bash
python -m unittest discover pruebas
```

## Estructura

```
xela-link/
├── main.py                  # arranca la app
├── modelo/
│   ├── grafo.py             # usuarios, amistades y pesos (lista de adyacencia)
│   ├── dijkstra.py          # ruta más corta + tabla de pasos
│   └── automata.py          # AFD ponderado: valida cadenas
├── datos/
│   ├── gestor_json.py       # guardar / cargar
│   └── usuarios.json        # datos de prueba
├── interfaz/
│   ├── login.py             # login y registro
│   ├── ventana_principal.py # menú, amigos, búsqueda, validar cadena
│   └── vista_grafo.py       # dibujo del grafo con NetworkX
├── pruebas/
│   └── test_modelo.py
└── docs/                    # informe final
```

## Modelo formal (resumen)

A = (Q, Σ, δ, q₀, F, w)

- **Q**: usuarios registrados más un estado de error.
- **Σ**: un símbolo por usuario ("pasar al amigo v").
- **δ(u, v) = v** si u y v son amigos; si no, el estado de error.
- **q₀**: usuario que busca. **F**: {usuario buscado}.
- **w(u, v)**: nivel de cercanía (1 mejor amigo, 2 amigo, 3 conocido).

Dijkstra devuelve la cadena aceptada de menor peso.

## Flujo de trabajo

1. `git pull origin main` antes de empezar.
2. Trabaja en tu rama: `git checkout -b <tu-nombre>`.
3. Edita solo tus archivos.
4. `git push origin <tu-nombre>` y abre un Pull Request hacia `main`.
5. Nadie hace push directo a `main`.
