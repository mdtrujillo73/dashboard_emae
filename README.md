# 🏛️ Dashboard EMAE – SECOPI 2023-2025

![Colombia Compra Eficiente](assets/escudo.png)

Este repositorio contiene el **Dashboard Analítico** de la Subdirección EMAE de **Colombia Compra Eficiente**. Se trata de una herramienta interactiva que permite explorar, cruzar y visualizar la contratación estatal registrada en el portal SECOP I, así como validar la información frente al universo de entidades obligadas por la Circular 674.

---

## ✨ Características Principales

* **📊 Métricas Clave (KPIs):** Resumen inmediato de total de contratos, valor contratado, entidades identificadas y entidades obligadas bajo la Circular 674.
* **🔎 Filtros Dinámicos:** Cruza la información filtrando por Vigencia (2023-2025), Departamento, Escenario de Reporte y Régimen de contratación.
* **📈 Visualizaciones Interactivas:**
  * Dona descriptiva de proporciones por *Escenario Analítico*.
  * Gráfico comparativo interanual por vigencias (en cantidad y montos).
  * Panel topológico y mapeo de contratos consolidados.
* **🎨 Identidad Institucional:** Aplicación de la paleta oficial (Amarillo, Naranja, Vinotinto, Azul Institucional) y estilos visuales del manual de marca de CCE.
* **⚡ Ultra Rápido:** Utiliza archivos `.parquet` como capa de caché local para manejar millones de filas de contratación pública casi de forma instantánea.

---

## 🛠️ Tecnologías y Requisitos

Este proyecto está construido 100% en Python utilizando las siguientes librerías core:

* **[Streamlit](https://streamlit.io/):** Framework para la construcción de toda la interfaz web.
* **[Pandas](https://pandas.pydata.org/):** Limpieza, normalización (unificación de categorías de modalidades) y procesamiento de datos.
* **[Plotly Express / GO](https://plotly.com/python/):** Componente de graficación avanzada y dinámica.
* **PyArrow:** Motor de compresión y lectura en formato columnar (Parquet).

Asegúrate de contar con **Python 3.9 o superior**.

---

## 🚀 Cómo correr el proyecto localmente

1. **Clona este repositorio:**
   ```bash
   git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   cd TU_REPOSITORIO/dashboard_emae
   ```

2. **Crea y activa un entorno virtual** (si usas Conda):
   ```bash
   conda create -n ColombiaCompra python=3.10
   conda activate ColombiaCompra
   ```

3. **Instala las dependencias** (puedes usar un `requirements.txt` o Poetry):
   ```bash
   pip install streamlit pandas plotly openpyxl pyarrow
   ```

4. **Agrega tu base de datos y logo:**
   * Ubica el archivo maestro de Excel o `.parquet` llamado `emae_base_estrella.parquet` en la raíz del proyecto.
   * Coloca el archivo `escudo.png` dentro de la carpeta `assets/` para cargar el logo.

5. **Levanta el servidor local:**
   ```bash
   streamlit run app.py
   ```
   *El dashboard abrirá automáticamente en tu navegador a través de `http://localhost:8501`*.

---

## 📁 Estructura del Directorio

```text
dashboard_emae/
│
├── app.py                      # 🚀 Punto de entrada y estructura web del dashboard
├── pyproject.toml              # 📦 Dependencias y configuración (Poetry)
├── README.md                   # 📖 Este archivo de documentación
│
├── assets/                     # 🖼️ Recursos gráficos
│   └── escudo.png              # Logo CCE
│
└── utils/                      # ⚙️ Módulos de lógica y procesamiento
    ├── charts.py               # Lógica de construcción de gráficos Plotly e identidad visual
    └── data_loader.py          # Lógica de carga pesada, caché Parquet y limpieza Pandas
```

---

*Desarrollado con 💻 para la democratización y análisis transparente de los datos de contratación en Colombia.*
