# Challenges

## Implementación de Pipeline de Entrenamiento y Versionado

### Contexto del proyecto

> **Simple ML Training Project** — Proyecto que entrena un modelo RandomForest sobre datos tabulares.

El objetivo de esta fase fue construir un pipeline de CI/CD que automatizara el entrenamiento, validación y publicación del modelo, incluyendo su versionado semántico mediante tags de Git.

---

### Problemas encontrados y soluciones

#### 1. Separación de jobs: testing y release

El pipeline inicial agrupaba las fases de testing y release en un único job. Esto dificultaba la trazabilidad, impedía reutilizar los jobs de forma independiente y hacía que un fallo en el release bloqueara la visibilidad de los resultados de los tests.

**Solución:** Se dividieron en dos jobs diferenciados. El job de testing ejecuta las validaciones del modelo y el de release solo se activa si el anterior finaliza con éxito, manteniendo una separación clara de responsabilidades en el pipeline.

---

#### 2. Ejecución de `model_tests`

Al integrar la ejecución de `pytest` sobre `test_model.py`, aparecieron varios errores en cascada.

**2a. Warnings de módulos no importados en la cobertura**

```
CoverageWarning: Module evaluate was never imported. (module-not-imported)
CoverageWarning: Module data_loader was never imported. (module-not-imported)
```

`pytest-cov` estaba configurado para medir cobertura sobre módulos (`evaluate`, `data_loader`) que el script de test no importaba directamente, por lo que nunca se instrumentaban.

**2b. Sin datos de cobertura, sin reporte**

```
CoverageWarning: No data was collected. (no-data-collected)
CovReportWarning: Failed to generate report: No data to report.
```

Al no importarse ninguno de los módulos indicados, la herramienta de cobertura no recopilaba datos y fallaba al intentar generar el informe.

**Solución (2a y 2b):** Se eliminó la configuración de `pytest-cov` del comando de ejecución. El script `test_model.py` valida únicamente el comportamiento del modelo entrenado, no los módulos internos de la aplicación, por lo que exigir cobertura sobre ellos no tenía sentido y generaba falsos negativos.

**2c. Error de conversión de datos en tiempo de test**

```
FAILED model_tests/test_model.py::test_model_accuracy
ValueError: could not convert string to float: ' Private'
```

El pipeline de preprocesamiento no estaba codificando correctamente las variables categóricas antes de pasarlas al modelo, lo que provocaba que valores como `' Private'` llegaran sin transformar.

**Solución:** Se analizó el flujo de preprocesamiento, se corrigió el script `test_model.py` para asegurar que los datos pasaban por la misma transformación que durante el entrenamiento, y se iteró hasta que el test pasó correctamente.

---

#### 3. Nomenclatura de tags inválida

El job de release fallaba porque el tag generado no seguía un formato válido reconocido por GitHub.

**Solución:** Se consultaron las buenas prácticas de versionado semántico (SemVer) y se adoptó el formato `V1.X.0`, donde el componente *minor* se incrementa en cada ejecución del workflow, reflejando la adición de nuevas funcionalidades.

Como mejora futura, se identificó que lo ideal sería determinar el tipo de cambio automáticamente (major, minor o patch) en función de la rama de origen o de convenciones en el mensaje del commit (por ejemplo, Conventional Commits), de modo que el tag refleje fielmente la naturaleza del cambio sin intervención manual.
