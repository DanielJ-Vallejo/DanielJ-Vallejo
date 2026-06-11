/* Bilingual toggle (ES default / EN) + footer year. No dependencies. */

const I18N = {
  en: {
    nav_projects: "Projects",
    nav_skills: "Skills",
    nav_contact: "Contact",
    hero_hello: "Hi, I'm",
    hero_role: "Data Science · Machine Learning · Scientific Computing",
    hero_bio:
      "Physicist in training (UNAM) building end-to-end machine learning systems: " +
      "from Monte Carlo simulation to transformers in production. Graduate of the " +
      "AI Macro-training program (MeIA 2025).",
    hero_cta_projects: "View projects",
    sec_projects: "Featured projects",
    sec_skills: "Skills",
    sec_contact: "Contact",
    tag_featured: "Featured",
    tag_nlp: "NLP",
    tag_cv: "Vision",
    tag_sim: "Simulation",
    tag_ml: "Classic ML",
    p1_title: "Credit Card Fraud Detection",
    p1_desc:
      "Full system: transaction simulator, RFM features with label delay, leakage-free " +
      "temporal validation and operational metrics (Card Precision@k). ROC-AUC 0.90 · " +
      "AP 0.61 on ~217k transactions with 1% fraud.",
    p2_title: "Spanish Sentiment Analysis — MeIA 2025",
    p2_desc:
      "BETO (Spanish BERT) fine-tuning for 1–5 polarity of tourism reviews: metadata-" +
      "enriched text, oversampling and partial layer freezing. Score 0.5889 on the " +
      "challenge leaderboard.",
    p5_title: "Mexican Sign Language Vowel Detection (YOLO)",
    p5_desc:
      "Mexican Sign Language in a few-shot regime: 9 trainings (YOLOv5/v8/v11 × " +
      "100/200/300 images) quantifying the data/performance trade-off. Best mAP@0.5: 0.853.",
    p4_title: "Statistical Physics Simulations",
    p4_desc:
      "2D/3D Ising with vectorized checkerboard Metropolis, Langevin dynamics and random " +
      "walks — validated against exact results (Onsager's Tc, Var[x]=2Dt) with jackknife errors.",
    p3_title: "Titanic without Data Leakage",
    p3_desc:
      "The classic benchmark with engineering discipline: preprocessing inside cross-" +
      "validated pipelines, domain features and honest evaluation. CV ROC-AUC 0.876, " +
      "consistent with holdout.",
    tag_auto: "Automation",
    p6_title: "Telegram Booking Agent",
    p6_desc:
      "Production-ready bot that books appointments and answers customers 24/7 at zero " +
      "cost: free Bot API, SQLite and fuzzy matching. New client = one YAML file, no " +
      "code changes. Optional local LLM via Ollama.",
    p7_title: "CFDI Invoice Extractor",
    p7_desc:
      "Mexican e-invoices (CFDI 3.3/4.0) to Excel in seconds: exact XML parsing, " +
      "drag-and-drop web app and optional OCR for scanned invoices. Fully local — " +
      "fiscal data never leaves your machine.",
    p8_title: "Price Monitor with Alerts",
    p8_desc:
      "Productized scraping: one YAML describes any store, the monitor stores history " +
      "in SQLite, detects drops and sends free Telegram alerts. Interactive Plotly " +
      "dashboard with CSV export.",
    view_code: "View code →",
    sk_lang: "Languages",
    sk_tools: "Tools",
    sk_domains: "Domains",
    dom_1: "Supervised learning",
    dom_2: "Computer vision",
    dom_3: "Monte Carlo simulation",
    dom_4: "Imbalanced data",
    contact_text:
      "I'm looking for opportunities in data science and machine learning. " +
      "If my profile fits your team, get in touch.",
    footer: "Built with plain HTML/CSS/JS",
  },
  es: {
    nav_projects: "Proyectos",
    nav_skills: "Habilidades",
    nav_contact: "Contacto",
    hero_hello: "Hola, soy",
    hero_role: "Ciencia de Datos · Machine Learning · Cómputo Científico",
    hero_bio:
      "Físico en formación (UNAM) que construye sistemas de machine learning de extremo " +
      "a extremo: de la simulación Monte Carlo a los transformers en producción. Egresado " +
      "del Macroentrenamiento en IA (MeIA 2025).",
    hero_cta_projects: "Ver proyectos",
    sec_projects: "Proyectos destacados",
    sec_skills: "Habilidades",
    sec_contact: "Contacto",
    tag_featured: "Destacado",
    tag_nlp: "NLP",
    tag_cv: "Visión",
    tag_sim: "Simulación",
    tag_ml: "ML clásico",
    p1_title: "Detección de Fraude con Tarjetas",
    p1_desc:
      "Sistema completo: simulador de transacciones, features RFM con retraso de " +
      "etiquetas, validación temporal sin fugas y métricas operativas (Card Precision@k). " +
      "ROC-AUC 0.90 · AP 0.61 con ~217k transacciones y 1% de fraude.",
    p2_title: "Análisis de Sentimientos en Español — MeIA 2025",
    p2_desc:
      "Fine-tuning de BETO (BERT español) para polaridad 1–5 de reseñas turísticas: " +
      "texto enriquecido con metadatos, sobremuestreo y congelamiento parcial de capas. " +
      "Score 0.5889 en el leaderboard del reto.",
    p5_title: "Detección de Vocales de LSM con YOLO",
    p5_desc:
      "Lengua de Señas Mexicana en régimen few-shot: 9 entrenamientos (YOLOv5/v8/v11 × " +
      "100/200/300 imágenes) cuantificando el compromiso datos/desempeño. Mejor mAP@0.5: 0.853.",
    p4_title: "Simulaciones de Física Estadística",
    p4_desc:
      "Ising 2D/3D con Metropolis checkerboard vectorizado, dinámica de Langevin y " +
      "caminatas aleatorias — validados contra resultados exactos (Tc de Onsager, " +
      "Var[x]=2Dt) con errores jackknife.",
    p3_title: "Titanic sin Fuga de Datos",
    p3_desc:
      "El benchmark clásico con disciplina de ingeniería: preprocesamiento dentro de " +
      "pipelines con validación cruzada, features de dominio y evaluación honesta. " +
      "ROC-AUC 0.876 (CV) consistente con holdout.",
    tag_auto: "Automatización",
    p6_title: "Agente de Citas por Telegram",
    p6_desc:
      "Bot listo para producción que agenda citas y responde clientes 24/7 con costo " +
      "cero: Bot API gratuita, SQLite y matching difuso. Cliente nuevo = un archivo " +
      "YAML, sin tocar código. LLM local opcional vía Ollama.",
    p7_title: "Extractor de Facturas CFDI",
    p7_desc:
      "Facturas electrónicas mexicanas (CFDI 3.3/4.0) a Excel en segundos: parsing " +
      "exacto del XML, app web de arrastrar y soltar, y OCR opcional para facturas " +
      "escaneadas. Todo local — los datos fiscales no salen de tu máquina.",
    p8_title: "Monitor de Precios con Alertas",
    p8_desc:
      "Scraping productizado: un YAML describe cualquier tienda, el monitor guarda " +
      "historial en SQLite, detecta bajadas y avisa gratis por Telegram. Dashboard " +
      "interactivo con Plotly y export a CSV.",
    view_code: "Ver código →",
    sk_lang: "Lenguajes",
    sk_tools: "Herramientas",
    sk_domains: "Dominios",
    dom_1: "Aprendizaje supervisado",
    dom_2: "Visión por computadora",
    dom_3: "Simulación Monte Carlo",
    dom_4: "Datos desbalanceados",
    contact_text:
      "Estoy buscando oportunidades en ciencia de datos y machine learning. " +
      "Si mi perfil encaja con tu equipo, escríbeme.",
    footer: "Hecho con HTML/CSS/JS puro",
  },
};

const stored = localStorage.getItem("lang");
let lang = Object.prototype.hasOwnProperty.call(I18N, stored) ? stored : "es";

function applyLanguage(next) {
  lang = next;
  localStorage.setItem("lang", lang);
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    if (I18N[lang][key]) el.textContent = I18N[lang][key];
  });
  // The button shows the language you would switch TO
  document.getElementById("lang-toggle").textContent = lang === "es" ? "EN" : "ES";
}

document.getElementById("lang-toggle").addEventListener("click", () => {
  applyLanguage(lang === "es" ? "en" : "es");
});

document.getElementById("year").textContent = new Date().getFullYear();
applyLanguage(lang);
