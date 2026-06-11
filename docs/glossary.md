# Glossary / Glosario

| Term / Término | EN | ES |
|---|---|---|
| **Average Precision (AP)** | Area under the precision-recall curve; the reference metric under heavy class imbalance. | Área bajo la curva precisión-exhaustividad; métrica de referencia con desbalance severo. |
| **Card Precision@k** | Of the *k* cards flagged per day by the model, the fraction that truly had fraud — models a daily investigation budget. | De las *k* tarjetas alertadas al día por el modelo, la fracción que realmente tuvo fraude — modela un presupuesto diario de investigación. |
| **Data leakage** | Information from the test set (or from the future) influencing training — produces optimistic, irreproducible results. | Información del conjunto de prueba (o del futuro) influyendo en el entrenamiento — produce resultados optimistas e irreproducibles. |
| **Delay period** | Days between a transaction and its label becoming reliable (the customer disputes the charge). Honest fraud systems leave this gap between train and test. | Días entre una transacción y la confiabilidad de su etiqueta (el cliente reclama el cargo). Los sistemas honestos dejan esta brecha entre entrenamiento y prueba. |
| **Few-shot learning** | Training useful models with very few labelled examples per class. | Entrenar modelos útiles con muy pocos ejemplos etiquetados por clase. |
| **Fine-tuning** | Continuing the training of a pre-trained model (e.g. BETO) on a downstream task. | Continuar el entrenamiento de un modelo preentrenado (p. ej. BETO) en una tarea específica. |
| **Jackknife** | Leave-one-out resampling estimate of an estimator's variance; the blocked variant handles autocorrelated Monte Carlo data. | Estimación de varianza por remuestreo dejando-uno-fuera; la variante por bloques maneja datos Monte Carlo autocorrelacionados. |
| **mAP@0.5** | Mean average precision of an object detector at IoU threshold 0.5. | Precisión media promedio de un detector de objetos con umbral IoU 0.5. |
| **Metropolis algorithm** | Markov chain Monte Carlo: propose a local change, accept with probability min(1, e^(−βΔE)). | Monte Carlo por cadenas de Markov: proponer un cambio local y aceptarlo con probabilidad min(1, e^(−βΔE)). |
| **Oversampling** | Repeating minority-class samples so the classifier doesn't ignore the rare class. | Repetir muestras de la clase minoritaria para que el clasificador no ignore la clase rara. |
| **RFM features** | Recency / Frequency / Monetary sliding-window aggregates describing an entity's recent behaviour. | Agregados de ventana deslizante Recencia / Frecuencia / Monto que describen el comportamiento reciente de una entidad. |
| **ROC-AUC** | Probability that a random positive scores above a random negative; insensitive to class balance. | Probabilidad de que un positivo aleatorio puntúe sobre un negativo aleatorio; insensible al balance de clases. |
