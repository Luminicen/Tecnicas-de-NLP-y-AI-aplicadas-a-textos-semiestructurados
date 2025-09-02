# Guía para instalar y ejecutar Manim en Windows

Este documento explica cómo instalar **Manim** en Windows, incluyendo las dependencias necesarias, cómo ejecutar un script de animación y dónde encontrar el video generado.

---

## 1. Requisitos previos

Antes de instalar Manim, asegúrate de tener:

- **Python 3.10 o superior**  
- **pip actualizado**:

```bash
python -m pip install --upgrade pip 
```

Microsoft Visual C++ Redistributable (necesario para algunos módulos de Manim como mapbox_earcut)

Descargar: Microsoft Visual C++ 2015-2022 Redistributable

Instalar y reiniciar la computadora.

Opcional: LaTeX (si vas a usar Tex para fórmulas matemáticas)

Recomendado: MiKTeX https://miktex.org/download

Durante la instalación, seleccionar “Install missing packages on-the-fly”.

## 2. Instalar Manim

```bash
pip install manim[windows]
```
## 3. Navegar a la carpeta del proyecto
```bash
cd ruta\de\tu\proyecto\video
```
## 4. Compilar un script de Manim
El archivo se llama pasiva.py y la clase de animación es ConversorPasivaActiva
Comando básico para renderizar y abrir el video automáticamente:
```bash
manim -p -qh pasiva.py ConversorPasivaActiva
```
-p → reproduce automáticamente el video después de compilarlo.

-ql → calidad baja (rápida) para pruebas.

-qlh → calidad alta (lento).

## 5. Ubicación del video generado
Por defecto, Manim guarda los videos en:
```bash
media/videos/<nombre_del_script>/<resolución>/<nombre_de_la_clase>.mp4
```
Si usas la opción -o nombre_video, el archivo se llamará
```bash
media/videos/video/<resolución>/nombre_video.mp4
```
## 5. Algunas Post Datas
Si no quieres instalar LaTeX, puedes reemplazar Tex por Text en los scripts de Manim. En el script pasiva.py deje comentadas las que usan Latex.
-J