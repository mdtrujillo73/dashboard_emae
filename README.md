# 🏛️ Dashboard EMAE – Estrategia de Despliegue SECOP II (2026)

![Colombia Compra Eficiente](assets/escudo.png)

Este repositorio contiene el **Dashboard Analítico** de la Subdirección de Estudios de Mercado y Abastecimiento Estratégico (**EMAE**) y la Subdirección de Información y Desarrollo Tecnológico (**IDT**) de **Colombia Compra Eficiente**. Permite explorar, cruzar y visualizar el 100% de la contratación registrada en SECOP I durante las vigencias **2023, 2024 y 2025** (**985.596 procesos** consolidados en **57.543 registros agrupados** de **4.525 entidades compradoras** / **3.643 NITs homologados**), y trazar la ruta operativa de despliegue de SECOP II para 2026.

---

## ✨ Características Principales (Actualización 2026)

* **📊 Radiografía por Segmento Normativo y Obligatoriedad (2026):**
  * **Potencial Obligada 2026 – Contratación Ordinaria (`TD_01` y `TD_01B`):** 587.265 procesos (59,6%) | 2.975 cuentas (2.482 NITs) | \$48,01 Billones reales.
  * **Obligada Vigencias Anteriores (2020–2025):** 221.563 procesos ordinarios (22,5%) | 730 cuentas (557 NITs) | \$18,58 Billones reales.
  * **Régimen Especial y Fondos de Ley (`TD_03` – Ley 2195/2022 Art. 53):** 123.544 procesos (12,5%) | 1.423 cuentas (1.355 NITs) | \$13,76 Billones reales.
  * **Exclusión Normativa Circular SECOP II (`TD_02`):** 53.224 procesos (5,4%) | 991 cuentas (930 NITs) | \$56,64 Billones reales.
* **🔥 Mapas de Calor Geográficos (Departamental y Municipal):**
  * **Mapa de Calor Coroplético por Departamento:** Polígonos oficiales DANE de los 33 departamentos coloreados por N° de Entidades, Procesos en SECOP I, Cuantía Real, % Penetración de Internet Fijo MinTIC (3T-2025) o % de adopción de SECOP II.
  * **Mapa de Calor Municipal (1.076+ Municipios con Código DIVIPOLA):** Soporta **Mapa de Calor de Densidad (`Densitymapbox`) + Puntos Municipales**, **Polígonos Municipales Coropléticos** y **Burbujas Georreferenciadas**, con **auto-zoom inteligente** al seleccionar cualquier departamento.
  * **Matriz de Calor 2D:** Cruce matricial entre Departamentos y Naturaleza Institucional (10 tipologías), Categoría CGN (Ley 617) y Conectividad MinTIC.
* **🚀 Las 6 Rutas Operativas de Despliegue 2026 (`TD_01B_LISTA_ENTIDADES`):** Clasificación operativa para las 2.975 entidades potenciales (Fase 1, Fase 1B, Fase 2 subcuentas municipales, Fase 2 registro desde cero, doble acción Circular + Ley 2195, y verificación de bloqueo manual FSE/ESP/ESE).
* **⚡ Carga Instantánea:** Utiliza archivos `.parquet` (`emae_base_estrella.parquet` y `emae_td01b_entidades.parquet`) y cartografía GeoJSON optimizada en `assets/` para renderizar millones de procesos en milisegundos.

---

## 🚀 Cómo ejecutar el Dashboard localmente

```bash
cd dashboard_emae
streamlit run app.py
```

Si usas Anaconda en Windows:
```powershell
& "C:\ProgramData\anaconda3\Scripts\streamlit.exe" run dashboard_emae\app.py
```
