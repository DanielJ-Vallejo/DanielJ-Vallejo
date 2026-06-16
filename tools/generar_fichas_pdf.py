"""Generate a one-page-style summary PDF ("ficha") for every portfolio project.

Each ficha contains: summary, real results (metrics tables + figures produced
by the pipelines) and a practical application section. Output goes to
``<proyecto>/reports/ficha_<id>.pdf``.

Usage::

    python tools/generar_fichas_pdf.py
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPO = Path(__file__).resolve().parents[1]
GITHUB = "github.com/DanielJ-Vallejo/DanielJ-Vallejo"
CONTACT = "Daniel Jiménez Vallejo  ·  daniel20615@gmail.com  ·  " + GITHUB

ACCENT = colors.HexColor("#0e7490")
DARK = colors.HexColor("#0b1020")
GRAY = colors.HexColor("#5a6275")

_styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=_styles["Title"], fontSize=19, leading=23,
                    textColor=DARK, alignment=0, spaceAfter=2)
SUB = ParagraphStyle("SUB", parent=_styles["Normal"], fontSize=10.5, leading=14,
                     textColor=GRAY, spaceAfter=10)
H2 = ParagraphStyle("H2", parent=_styles["Heading2"], fontSize=12.5, leading=16,
                    textColor=ACCENT, spaceBefore=12, spaceAfter=4)
BODY = ParagraphStyle("BODY", parent=_styles["Normal"], fontSize=10, leading=14.5,
                      textColor=DARK, spaceAfter=6)
CAPTION = ParagraphStyle("CAP", parent=_styles["Normal"], fontSize=8.5, leading=11,
                         textColor=GRAY, alignment=1, spaceAfter=10)
FOOT = ParagraphStyle("FOOT", parent=_styles["Normal"], fontSize=8.5,
                      textColor=GRAY, alignment=1)


def fig(path: Path, caption: str, max_w=15.5 * cm, max_h=8.0 * cm) -> list:
    """Image flowable scaled to fit, with caption. Skips missing files."""
    if not path.exists():
        return []
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h, 1.0)
    return [Image(str(path), width=w * scale, height=h * scale),
            Paragraph(caption, CAPTION)]


def metrics_table(headers: list[str], rows: list[list[str]],
                  highlight_row: int | None = None) -> Table:
    data = [headers] + rows
    t = Table(data, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c8cdd8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#eef2f7")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if highlight_row is not None:
        style.append(("FONTNAME", (0, highlight_row + 1), (-1, highlight_row + 1),
                      "Helvetica-Bold"))
    t.setStyle(TableStyle(style))
    return t


def build_pdf(out_path: Path, title: str, subtitle: str, story_body: list) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(out_path), pagesize=letter,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.6 * cm, bottomMargin=1.6 * cm,
        title=title, author="Daniel Jiménez Vallejo",
    )
    story = [
        Paragraph(title, H1),
        Paragraph(subtitle, SUB),
        HRFlowable(width="100%", thickness=1.2, color=ACCENT),
        Spacer(1, 6),
        *story_body,
        Spacer(1, 14),
        HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#c8cdd8")),
        Spacer(1, 4),
        Paragraph(CONTACT, FOOT),
    ]
    doc.build(story)
    print(f"OK  {out_path.relative_to(REPO)}")


def p(text: str) -> Paragraph:
    return Paragraph(text, BODY)


def h(text: str) -> Paragraph:
    return Paragraph(text, H2)


# --------------------------------------------------------------------------
# Proyecto 01 — Fraude
# --------------------------------------------------------------------------
def ficha_01() -> None:
    root = REPO / "proyecto-01-fraud-detection"
    m = json.loads((root / "reports" / "metrics.json").read_text(encoding="utf-8"))
    rows = [
        [r["model"].replace("_", " "), f"{r['roc_auc']:.3f}",
         f"{r['average_precision']:.3f}", f"{r['card_precision_top_20']:.3f}"]
        for r in m["metrics"]
    ]
    best = max(range(len(rows)), key=lambda i: float(rows[i][2]))
    body = [
        h("Resumen"),
        p("Sistema de detección de fraude con tarjeta de extremo a extremo. Un "
          "simulador genera una red realista de clientes y terminales e inyecta tres "
          "escenarios de fraude (anomalías de monto, terminales comprometidas y robo "
          "de datos de tarjeta). Sobre esos datos se construyen variables de "
          "comportamiento tipo RFM y un score de riesgo por terminal <b>desplazado 7 "
          "días</b> — reproduciendo que en producción las etiquetas de fraude llegan "
          "tarde — y se entrenan tres clasificadores con partición temporal estricta "
          "(entrenamiento / brecha / prueba) que impide fugas de información."),
        h("Resultados (periodo de prueba)"),
        p(f"Datos: <b>{m['n_transactions']:,} transacciones</b>, "
          f"<b>{m['fraud_rate_pct']}% fraudulentas</b> — el desbalance real del "
          "problema. Con 1% de positivos, el ROC-AUC engaña; la métrica decisiva es "
          "Average Precision y la operativa es Card Precision@20: de las 20 tarjetas "
          "que un equipo antifraude puede revisar al día, cuántas eran fraude real."),
        metrics_table(
            ["Modelo", "ROC-AUC", "Average Precision", "Card Precision@20"],
            rows, highlight_row=best),
        Spacer(1, 8),
        *fig(root / "reports" / "figures" / "pr_curves.png",
             "Curvas Precisión-Recall en el periodo de prueba: el gradient boosting "
             "duplica la precisión de la línea base en casi todos los niveles de recall."),
        *fig(root / "reports" / "figures" / "daily_volume.png",
             "Volumen diario de transacciones y fraude del dataset simulado.",
             max_h=5.5 * cm),
        h("Aplicación real"),
        p("Bancos, fintechs y pasarelas de pago usan exactamente esta arquitectura "
          "para priorizar alertas con presupuesto limitado de analistas. La misma "
          "técnica (agregados de ventana + retraso de etiquetas + precisión@k) aplica "
          "a detección de contracargos en e-commerce, abuso de promociones y cuentas "
          "falsas. Todo el pipeline es reproducible con un comando y 11 pruebas "
          "automatizadas validan simulador, features y métricas."),
    ]
    build_pdf(root / "reports" / "ficha_fraud_detection.pdf",
              "Detección de Fraude con Tarjetas de Crédito",
              "Machine learning con validación temporal y métricas operativas de la "
              "industria  ·  Python, scikit-learn, pandas",
              body)


# --------------------------------------------------------------------------
# Proyecto 02 — Sentimientos MeIA
# --------------------------------------------------------------------------
def ficha_02() -> None:
    root = REPO / "proyecto-02-sentiment-analysis"
    body = [
        h("Resumen"),
        p("Participación en el reto nacional <b>MeIA 2025</b> (Macroentrenamiento en "
          "Inteligencia Artificial, UNAM): predecir la calificación 1–5 de reseñas "
          "turísticas mexicanas. La solución hace fine-tuning de <b>BETO</b> (BERT "
          "preentrenado en español) con tres decisiones clave: enriquecer el texto "
          "con metadatos como pseudo-tokens ([REGION] [TOWN] [SERVICE]), "
          "sobremuestrear la clase minoritaria y <b>congelar las primeras 6 capas</b> "
          "del encoder — con ~5,000 ejemplos el fine-tuning completo sobreajusta en "
          "dos épocas."),
        h("Resultados"),
        metrics_table(
            ["Concepto", "Valor"],
            [["Score en el leaderboard del reto", "0.5889"],
             ["Equipo", "Moodhacker4Neurona"],
             ["Modelo base", "dccuchile/bert-base-spanish-wwm-uncased (BETO)"],
             ["Clases", "5 niveles de polaridad (tarea fina, no binaria)"],
             ["Regularización", "dropout 0.4/0.3 + weight decay 0.1 + 6 capas congeladas"]]),
        Spacer(1, 6),
        p("La predicción fina de polaridad en español es considerablemente más dura "
          "que el sentimiento binario: la frontera entre 3 y 4 estrellas es subjetiva "
          "incluso para humanos. El archivo oficial de predicciones enviado al "
          "leaderboard se conserva en el repositorio como evidencia."),
        h("Aplicación real"),
        p("Hoteles, restaurantes y plataformas de reseñas usan esta tecnología para "
          "monitorear reputación a escala: clasificar miles de opiniones por "
          "sucursal, detectar caídas de satisfacción antes de que aparezcan en el "
          "rating global y priorizar respuestas. El mismo pipeline aplica a tickets "
          "de soporte, encuestas NPS y comentarios en redes sociales en español — un "
          "idioma donde los modelos genéricos en inglés fallan."),
    ]
    build_pdf(root / "reports" / "ficha_sentiment_analysis.pdf",
              "Análisis de Sentimientos en Español — Reto MeIA 2025",
              "Fine-tuning de BETO para polaridad fina de reseñas turísticas  ·  "
              "PyTorch, Hugging Face Transformers",
              body)


# --------------------------------------------------------------------------
# Proyecto 03 — Titanic
# --------------------------------------------------------------------------
def ficha_03() -> None:
    root = REPO / "proyecto-03-titanic"
    m = json.loads((root / "reports" / "metrics.json").read_text(encoding="utf-8"))
    rows = [
        [r["model"].replace("_", " "),
         f"{r['cv_accuracy']:.3f} ± {r['cv_accuracy_std']:.3f}",
         f"{r['cv_roc_auc']:.3f}", f"{r['cv_f1']:.3f}"]
        for r in m["cross_validation"]
    ]
    hold = m["holdout"]
    body = [
        h("Resumen"),
        p("El benchmark clásico, resuelto con la disciplina que la mayoría omite: "
          "<b>cero fuga de datos</b>. Todas las estadísticas aprendidas (medianas de "
          "imputación, escalado, categorías one-hot) viven dentro del pipeline y se "
          "ajustan por fold de validación cruzada. La ingeniería de variables usa "
          "conocimiento de dominio: título social extraído del nombre (Mr/Mrs/Master/"
          "Officer/Royalty), tamaño de familia y cubierta del camarote."),
        h("Resultados (891 pasajeros, 38.4% de supervivencia)"),
        metrics_table(
            ["Modelo", "Accuracy (CV 5-fold)", "ROC-AUC (CV)", "F1 (CV)"],
            rows, highlight_row=2),
        Spacer(1, 6),
        p(f"Evaluación final en retención del 20% jamás tocado: <b>accuracy "
          f"{hold['accuracy']:.3f}, ROC-AUC {hold['roc_auc']:.3f}, F1 "
          f"{hold['f1']:.3f}</b> — consistente con la validación cruzada, es decir, "
          "sin sesgo optimista: el número que se reporta es el que se obtendría en "
          "producción."),
        *fig(root / "reports" / "figures" / "survival_by_group.png",
             "Tasas de supervivencia por sexo, clase y título social — las tres "
             "variables más informativas.", max_h=5.5 * cm),
        *fig(root / "reports" / "figures" / "confusion_matrix.png",
             "Matriz de confusión del mejor modelo en el conjunto de retención.",
             max_h=6.5 * cm),
        h("Aplicación real"),
        p("La estructura de este proyecto es la plantilla de cualquier problema "
          "tabular de negocio: predicción de churn de clientes, scoring de riesgo "
          "crediticio, conversión de leads o abandono de carrito. Lo que se "
          "transfiere no es el dataset — es la disciplina: pipelines sin fuga, "
          "validación honesta y features con conocimiento del dominio."),
    ]
    build_pdf(root / "reports" / "ficha_titanic.pdf",
              "Predicción de Supervivencia — Titanic sin Fuga de Datos",
              "Pipelines de scikit-learn con validación honesta  ·  "
              "ColumnTransformer, validación cruzada",
              body)


# --------------------------------------------------------------------------
# Proyecto 04 — Simulaciones
# --------------------------------------------------------------------------
def ficha_04() -> None:
    root = REPO / "proyecto-04-simulaciones"
    body = [
        h("Resumen"),
        p("Física estadística computacional de mi formación en la UNAM, empaquetada "
          "como librería Python con pruebas: modelos de <b>Ising 2D y 3D</b> "
          "(algoritmo de Metropolis con actualización checkerboard vectorizada en "
          "NumPy puro — media red por operación, sin extensiones compiladas), "
          "<b>dinámica de Langevin</b> sobreamortiguada (Euler-Maruyama) y caminatas "
          "aleatorias, con estimación de errores por <b>jackknife por bloques</b> "
          "para datos autocorrelacionados."),
        h("Resultados validados contra teoría exacta"),
        metrics_table(
            ["Sistema", "Predicción teórica", "Resultado simulado"],
            [["Ising 2D", "Tc de Onsager = 2.269", "picos de χ y Cv en Tc"],
             ["Ising 3D", "Tc numérica = 4.5115", "pico de susceptibilidad en Tc"],
             ["Langevin", "Var[x(t)] = 2Dt (pendiente 2.0)", "pendiente ajustada 2.014"],
             ["Caminata aleatoria", "⟨x²⟩ = N", "escalamiento difusivo reproducido"]]),
        Spacer(1, 8),
        *fig(root / "reports" / "figures" / "ising2d_observables.png",
             "Ising 2D: magnetización, energía, susceptibilidad y calor específico vs "
             "temperatura para tres tamaños de red; la línea punteada es la Tc exacta "
             "de Onsager.", max_h=8.5 * cm),
        *fig(root / "reports" / "figures" / "langevin_variance.png",
             "Crecimiento lineal de la varianza en Langevin: pendiente empírica 2.014 "
             "vs valor exacto 2.0.", max_h=5.5 * cm),
        h("Aplicación real"),
        p("Los métodos de Monte Carlo y las ecuaciones diferenciales estocásticas de "
          "este proyecto son los mismos que se usan en finanzas cuantitativas "
          "(valuación de derivados, riesgo), en optimización (recocido simulado), en "
          "ciencia de materiales y en biofísica. Las 9 pruebas automatizadas son "
          "aserciones físicas que una implementación incorrecta no puede pasar — la "
          "misma mentalidad de validación que exige el ML en producción."),
    ]
    build_pdf(root / "reports" / "ficha_simulaciones.pdf",
              "Simulaciones de Física Estadística",
              "Monte Carlo, dinámica estocástica y errores rigurosos  ·  "
              "NumPy vectorizado, jackknife",
              body)


# --------------------------------------------------------------------------
# Proyecto 05 — LSM
# --------------------------------------------------------------------------
def ficha_05() -> None:
    root = REPO / "proyecto-05-lsm-vision"
    body = [
        h("Resumen"),
        p("Detección de las cinco vocales de la <b>Lengua de Señas Mexicana (LSM)</b> "
          "con YOLO en régimen de <b>few-shot learning</b>. En México ~2.4 millones "
          "de personas con discapacidad auditiva usan LSM, pero a diferencia del "
          "lenguaje de señas americano casi no existen datasets. El experimento "
          "cuantifica el compromiso datos/desempeño: malla de 3 arquitecturas "
          "(YOLOv5n, v8n, v11n) × 3 tamaños de entrenamiento (100/200/300 imágenes) "
          "= <b>9 entrenamientos</b> con hiperparámetros idénticos y rebalanceo de "
          "clases."),
        h("Resultados (conjunto de prueba)"),
        metrics_table(
            ["Modelo", "Imágenes", "Precisión", "Recall", "mAP@0.5"],
            [["YOLOv5n", "300", "0.838", "0.655", "0.805"],
             ["YOLOv8n", "300", "0.669", "0.762", "0.853"],
             ["YOLOv11n", "300", "0.822", "0.751", "0.810"]],
            highlight_row=1),
        Spacer(1, 6),
        p("Hallazgo central: triplicar los datos (100 → 300 imágenes) sube el mAP@0.5 "
          "<b>+0.26 en promedio</b>, mientras que la brecha entre arquitecturas con "
          "300 imágenes es de apenas 0.05 — en régimen de pocos datos, <b>los datos "
          "le ganan a la arquitectura por un factor de cinco</b>."),
        *fig(root / "reports" / "figures" / "1_map_vs_tamano.png",
             "mAP@0.5 en función del tamaño del dataset para las tres arquitecturas.",
             max_h=6.5 * cm),
        *fig(root / "reports" / "figures" / "5_confusion_matrix.png",
             "Matriz de confusión del mejor modelo sobre las cinco vocales.",
             max_h=6.5 * cm),
        h("Aplicación real"),
        p("Tecnología asistiva: traducción de señas en tiempo real para servicios "
          "públicos, kioscos y educación inclusiva. La metodología few-shot es "
          "directamente transferible a cualquier problema de visión con pocos datos "
          "etiquetados: defectos industriales raros, especies en cámaras trampa, "
          "inspección médica — los casos donde el dato es caro y mandan las técnicas "
          "de eficiencia de muestras."),
    ]
    build_pdf(root / "reports" / "ficha_lsm_vision.pdf",
              "Detección de Vocales de Lengua de Señas Mexicana",
              "YOLO con few-shot learning — 9 experimentos controlados  ·  "
              "YOLOv5/v8/v11, OpenCV",
              body)


# --------------------------------------------------------------------------
# Proyecto 06 — Telegram
# --------------------------------------------------------------------------
def ficha_06() -> None:
    root = REPO / "proyecto-06-telegram-agent"
    body = [
        h("Resumen"),
        p("Bot de Telegram listo para producción que atiende clientes de un negocio "
          "pequeño <b>24/7 con costo de operación de $0</b>: la Bot API de Telegram "
          "es gratuita (a diferencia de WhatsApp Business API, que cobra por "
          "conversación). Responde preguntas frecuentes con matching difuso tolerante "
          "a acentos y mensajes cortos, <b>agenda citas con botones</b> (servicio → "
          "horario libre → confirmación) sobre SQLite con horarios a prueba de "
          "duplicados, y reenvía al dueño lo que no sabe responder. Opcionalmente "
          "conecta un LLM local gratuito (Ollama) para preguntas abiertas."),
        h("Resultados"),
        metrics_table(
            ["Aspecto", "Estado"],
            [["Pruebas automatizadas", "11/11 pasando (matching, horarios, doble reserva)"],
             ["Costo de APIs", "$0 — Telegram Bot API gratuita, sin mensualidades"],
             ["Incorporar un negocio nuevo", "editar 1 archivo YAML, sin tocar código"],
             ["Doble reserva de horario", "imposible por restricción UNIQUE en BD"],
             ["Hardware necesario", "cualquier máquina: Raspberry Pi o plan gratuito en la nube"]]),
        Spacer(1, 6),
        p("Arquitectura: toda la lógica de negocio (scoring de FAQ, generación de "
          "horarios, reservas) es independiente del framework y está cubierta por "
          "pruebas; el adaptador de Telegram es una capa delgada — el mismo núcleo "
          "puede servir un widget web o un bot de Discord sin cambios."),
        h("Aplicación real"),
        p("Consultorios, estéticas, talleres y salones de eventos pierden clientes "
          "por no contestar a tiempo. Este bot es un <b>producto instalable</b>: el "
          "negocio define servicios, horarios y preguntas frecuentes en un YAML y "
          "queda operando el mismo día, siendo dueño de su bot sin cuotas "
          "recurrentes obligatorias. La misma arquitectura desacoplada permite "
          "adaptarlo a otros canales (web, Discord) reutilizando el núcleo probado."),
    ]
    build_pdf(root / "reports" / "ficha_telegram_agent.pdf",
              "Agente de Citas y Atención por Telegram",
              "Asistente 24/7 para negocios con costo cero de operación  ·  "
              "Telegram Bot API, SQLite, Ollama opcional",
              body)


# --------------------------------------------------------------------------
# Proyecto 07 — CFDI
# --------------------------------------------------------------------------
def ficha_07() -> None:
    root = REPO / "proyecto-07-facturas-cfdi"
    body = [
        h("Resumen"),
        p("Las facturas electrónicas mexicanas (<b>CFDI</b>) son XML con validez "
          "legal que contienen todos los datos fiscales — y aun así contadores y "
          "pymes los capturan a mano en Excel cada mes. Esta herramienta convierte "
          "carpetas completas de CFDI 3.3 y 4.0 en una hoja de cálculo limpia "
          "(UUID, RFC y nombre de emisor/receptor, fecha, subtotal, total, moneda) "
          "con <b>parsing exacto del XML</b> usando la librería estándar — sin "
          "adivinar con OCR. Incluye interfaz web de arrastrar y soltar (Streamlit) "
          "y capa OCR opcional con Tesseract para facturas escaneadas."),
        h("Resultados"),
        metrics_table(
            ["Aspecto", "Estado"],
            [["Pruebas automatizadas", "8/8 pasando (CFDI 3.3 y 4.0, archivos corruptos, OCR)"],
             ["Exactitud sobre XML", "100% — se leen los atributos legales, no se infiere"],
             ["Procesamiento por lote", "una carpeta entera; un XML inválido no detiene el lote"],
             ["Privacidad", "100% local: los datos fiscales no salen de la máquina"],
             ["Exportación", "Excel (.xlsx) y CSV con un clic"]]),
        Spacer(1, 6),
        p("Detalle de robustez encontrado por las pruebas: el patrón de OCR para "
          "'Total' coincidía también con 'Subtotal'; se corrigió con lookbehind "
          "negativo y tomando la última ocurrencia — ejemplo del valor de las pruebas "
          "automatizadas sobre expresiones regulares fiscales."),
        h("Aplicación real"),
        p("Despachos contables que procesan cientos de facturas por cliente al mes, "
          "pymes que concilian gastos, y cualquier flujo de cuentas por pagar. El "
          "ahorro es directo: minutos de captura por factura → segundos por carpeta, "
          "sin errores de dedo. Se adapta a cada despacho definiendo el formato de "
          "salida (carpeta → Excel con las columnas que cada flujo contable "
          "necesita)."),
    ]
    build_pdf(root / "reports" / "ficha_facturas_cfdi.pdf",
              "Extractor de Facturas CFDI a Excel",
              "Automatización fiscal mexicana 100% local  ·  Python stdlib, "
              "Streamlit, OCR opcional",
              body)


# --------------------------------------------------------------------------
# Proyecto 08 — Monitor de precios
# --------------------------------------------------------------------------
def ficha_08() -> None:
    root = REPO / "proyecto-08-price-monitor"
    body = [
        h("Resumen"),
        p("Web scraping convertido en producto: <b>un archivo YAML de 8 líneas "
          "describe la página de cualquier tienda</b> (selectores CSS de producto, "
          "título y precio) y el monitor hace el resto — scrapea con horario, guarda "
          "historial de precios en SQLite, detecta bajadas comparando los dos últimos "
          "snapshots por producto y envía <b>alertas gratuitas por Telegram</b>. "
          "Incluye dashboard interactivo (Plotly/Streamlit) con historial por "
          "producto y exportación a CSV. El parser de precios maneja formatos reales: "
          "$1,234.56, £51.77, 1.234,56 MXN y 19,99."),
        h("Resultados"),
        metrics_table(
            ["Aspecto", "Estado"],
            [["Pruebas automatizadas", "8/8 pasando, todas offline (fixture HTML, formatos, bajadas)"],
             ["Demo en vivo verificada", "14 productos scrapeados de books.toscrape.com (sitio legal de práctica)"],
             ["Sitio nuevo", "8 líneas de YAML — sin tocar código"],
             ["Alertas", "Telegram gratuito; el fallo de alerta nunca tumba el scrape"],
             ["Scraping responsable", "User-Agent identificado; se respetan robots.txt y ToS"]]),
        Spacer(1, 8),
        p("Arquitectura: YAML del sitio → scraper (requests + BeautifulSoup) → "
          "SQLite (historial) → detección de bajadas → alerta Telegram + dashboard. "
          "Programable gratis con el Programador de tareas de Windows o cron."),
        h("Aplicación real"),
        p("Comercios que vigilan precios de la competencia, compradores que esperan "
          "la bajada de un producto, y analistas que construyen historial para "
          "negociar con proveedores. La arquitectura desacoplada (un YAML por sitio) "
          "permite cubrir nuevos comercios sin tocar código y mantener un historial "
          "confiable para análisis de tendencias."),
    ]
    build_pdf(root / "reports" / "ficha_price_monitor.pdf",
              "Monitor de Precios con Alertas Automáticas",
              "Scraping configurable, historial y alertas Telegram gratis  ·  "
              "BeautifulSoup, SQLite, Plotly",
              body)


# --------------------------------------------------------------------------
# Proyecto 09 — Demanda Mundial 2026
# --------------------------------------------------------------------------
def ficha_09() -> None:
    root = REPO / "proyecto-09-mundial-demanda"
    body = [
        h("Resumen"),
        p("Análisis de datos de extremo a extremo: de una pregunta de negocio a una "
          "recomendación, usando <b>SQL</b>. Modela la ocupación y los precios de "
          "hoteles en las sedes mexicanas del Mundial 2026 (CDMX, Guadalajara, "
          "Monterrey) sobre SQLite, con consultas de negocio (JOIN, LEFT JOIN, "
          "GROUP BY) y una capa de presentación en pandas + matplotlib."),
        h("Resultados"),
        metrics_table(
            ["Indicador", "Valor"],
            [["Ocupación en día de partido", "92.9% (vs 60.3% normal, +54%)"],
             ["Alza de precio en día de partido", "+9% (la demanda no se refleja en el precio)"],
             ["Recomendación de pricing", "+20% en días de partido"],
             ["Ingreso adicional estimado", "~$5.2 M MXN"],
             ["Pruebas automatizadas", "6/6 pasando"]],
            highlight_row=2),
        *fig(root / "reports" / "partido_vs_normal.png",
             "Día de partido vs día normal: la demanda salta, el precio no."),
        h("Aplicación real"),
        p("Hoteles, plataformas de renta y comercios de las sedes ajustando precios a "
          "la demanda del evento. El mismo enfoque (SQL para consultar, pandas y "
          "matplotlib para presentar) sirve para cualquier análisis de demanda y "
          "pricing estacional."),
    ]
    build_pdf(root / "reports" / "ficha_mundial_demanda.pdf",
              "Demanda y Pricing Hotelero — Mundial 2026",
              "Análisis de datos end-to-end con SQL  ·  SQLite, pandas, matplotlib, Streamlit",
              body)


# --------------------------------------------------------------------------
# Proyecto 10 — Predicción de churn
# --------------------------------------------------------------------------
def ficha_10() -> None:
    root = REPO / "proyecto-10-churn-prediction"
    body = [
        h("Resumen"),
        p("Predicción de abandono de clientes (churn) de extremo a extremo: perfila el "
          "churn por segmento en <b>SQL</b> (GROUP BY, CASE WHEN) y entrena una "
          "regresión logística interpretable cuyos coeficientes son los <i>drivers</i> "
          "del abandono, traduciéndolo en una recomendación de retención con valor."),
        h("Resultados"),
        metrics_table(
            ["Indicador", "Valor"],
            [["ROC-AUC del modelo (prueba)", "0.773"],
             ["Churn — contrato mes a mes", "47.5% (vs ~16% anual/bianual)"],
             ["Segmento de mayor riesgo", "mes a mes + 3+ llamadas: 58% churn"],
             ["Recomendación", "campaña de retención al segmento de riesgo"],
             ["Rescate estimado", "~$33 K MXN/mes de ingreso recurrente"],
             ["Pruebas automatizadas", "6/6 pasando"]],
            highlight_row=0),
        *fig(root / "reports" / "churn_drivers.png",
             "Drivers del churn: contrato y antigüedad bajan el riesgo; soporte lo sube."),
        h("Aplicación real"),
        p("Cualquier negocio por suscripción (telecom, SaaS, gimnasios, streaming) que "
          "quiera saber QUÉ clientes va a perder y, sobre todo, QUÉ hacer: priorizar la "
          "retención donde más vale, que es mucho más barato que adquirir nuevos."),
    ]
    build_pdf(root / "reports" / "ficha_churn_prediction.pdf",
              "Predicción de Churn de Clientes",
              "SQL + Machine Learning + recomendación de retención  ·  scikit-learn, pandas",
              body)


# --------------------------------------------------------------------------
# Proyecto 11 — Visión por computadora (fundamentos + experimentos)
# --------------------------------------------------------------------------
def ficha_11() -> None:
    root = REPO / "proyecto-11-vision-fundamentos"
    body = [
        h("Resumen"),
        p("Proyecto de referencia en visión por computadora, en dos partes: (1) las "
          "operaciones base de CV <b>implementadas desde cero en numpy</b> (convolución, "
          "desenfoque gaussiano, bordes Sobel, umbralizado y conteo de objetos por "
          "componentes conexas) y (2) el <b>análisis comparativo de 9 experimentos YOLO "
          "reales</b> (3 arquitecturas × 3 tamaños de dataset)."),
        h("Resultados (experimentos YOLO reales)"),
        metrics_table(
            ["Experimento", "mAP@0.5"],
            [["yolov11n · 300 imágenes (mejor)", "0.891"],
             ["yolov11n · 200 imágenes", "0.875"],
             ["yolov5n · 300 imágenes", "0.851"],
             ["yolov8n · 300 imágenes", "0.846"],
             ["yolov5n · 100 imágenes (peor)", "0.637"]],
            highlight_row=0),
        *fig(root / "reports" / "tradeoff_experimentos.png",
             "Más datos ayudan, con rendimientos decrecientes; yolov11n domina."),
        h("Aplicación real"),
        p("Demuestra dominio de los fundamentos (no solo llamar a una librería) y rigor "
          "para comparar modelos: elegir arquitectura y tamaño de datos con criterio. La "
          "parte desde cero sirve además para enseñar y entender la visión por computadora."),
    ]
    build_pdf(root / "reports" / "ficha_vision_fundamentos.pdf",
              "Visión por Computadora — Fundamentos + Análisis de Experimentos",
              "CV desde cero (numpy) + comparación de 9 entrenamientos YOLO reales",
              body)


# --------------------------------------------------------------------------
# Proyecto 12 — Seguimiento de personas
# --------------------------------------------------------------------------
def ficha_12() -> None:
    root = REPO / "proyecto-12-people-tracking"
    body = [
        h("Resumen"),
        p("Sistema de <b>seguimiento multi-objeto</b> de personas: YOLO detecta en cada "
          "frame y un tracker asigna un <b>ID estable</b> combinando solapamiento "
          "espacial (IoU) y similitud de apariencia (histograma HSV), con asignación "
          "óptima por <b>algoritmo Húngaro</b> (SciPy). La lógica de tracking está "
          "desacoplada de la cámara para poder probarse de forma automática."),
        h("Diseño y resultados"),
        metrics_table(
            ["Aspecto", "Detalle"],
            [["Detección", "YOLOv8 (clase persona)"],
             ["Asociación", "IoU + coseno sobre histograma HSV; score max(blend, similitud)"],
             ["Asignación óptima", "algoritmo Húngaro (scipy linear_sum_assignment)"],
             ["Robustez a cortes de escena", "el match por apariencia conserva el ID si el IoU cae a 0"],
             ["Pruebas automatizadas", "6/6 (IoU, similitud, IDs estables, ciclo de vida)"]]),
        h("Aplicación real"),
        p("Conteo de personas, analítica de aforo/flujo en tiendas o eventos, y "
          "videovigilancia. Separar la lógica (probada, sin cámara) de la app de video "
          "(YOLO + OpenCV) la hace mantenible y confiable."),
    ]
    build_pdf(root / "reports" / "ficha_people_tracking.pdf",
              "Seguimiento de Personas — Tracking Multi-objeto",
              "YOLO + IoU + apariencia HSV + algoritmo Húngaro  ·  lógica desacoplada y probada",
              body)


if __name__ == "__main__":
    for builder in (ficha_01, ficha_02, ficha_03, ficha_04, ficha_05, ficha_06,
                    ficha_07, ficha_08, ficha_09, ficha_10, ficha_11, ficha_12):
        builder()
    print("\nFichas PDF generadas en <proyecto>/reports/")
