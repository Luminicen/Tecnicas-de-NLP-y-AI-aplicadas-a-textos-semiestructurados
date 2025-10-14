# Proyecto-IDI-2025
# Servicio: Detección de Tiempos Verbales en Español

Este proyecto implementa un detector de **tiempos verbales** en español usando [spaCy](https://spacy.io/).
Recibe una cadena de texto y devuelve una lista de tuplas, cada una con el verbo encontrado y la etiqueta de su tiempo verbal.

## 🚀 Características

- Detección de tiempos **simples** (presente, pasado, futuro).
- Detección de tiempos **compuestos** (pretérito perfecto compuesto, pluscuamperfecto, futuro compuesto).
- Reconocimiento de **perífrasis verbales** comunes (futuro perifrástico, presente progresivo), incluyendo discontinuas (con adverbios intercalados).
- Evita duplicados (no cuenta participios o auxiliares sueltos como tiempos simples).

---

## 📦 Instalación

Cloná este repositorio y creá un entorno virtual:

``` bash
git clone https://github.com/usuario/Proyecto-IDI-2025.git
cd Proyecto-IDI-2025
python3 -m venv entorno
source entorno/bin/activate   # Linux/macOS
entorno\Scripts\activate      # Windows
pip install requirements.txt
```
