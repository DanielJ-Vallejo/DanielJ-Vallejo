# Security Policy / Política de Seguridad

## 🇬🇧 English

### Scope

This is a personal data science portfolio. Even so, it follows basic supply-chain and
data hygiene rules:

- **No secrets in the repository.** No API keys, tokens or credentials are committed;
  `.env` files are git-ignored. If you find one, please report it.
- **Dependency auditing.** CI runs `pip-audit` against every project's
  `requirements.txt` and `bandit` against all source code on every push.
- **Data privacy.** Datasets that are not freely redistributable (MeIA 2025 challenge
  data, sign-language images) are **excluded from version control**; only download/usage
  instructions are committed. The fraud detection data is synthetic by design.
- **Pinned minimum versions** in `requirements.txt` to avoid resolving to known-vulnerable
  releases.

### Reporting a vulnerability

Open a private report via GitHub *Security → Report a vulnerability*, or email
**daniel20615@gmail.com**. You should get a response within a week.

## 🇪🇸 Español

### Alcance

Este es un portafolio personal de ciencia de datos. Aun así, sigue reglas básicas de
higiene de datos y cadena de suministro:

- **Sin secretos en el repositorio.** No se suben llaves de API, tokens ni credenciales;
  los archivos `.env` están en `.gitignore`. Si encuentras alguno, repórtalo.
- **Auditoría de dependencias.** El CI ejecuta `pip-audit` sobre cada
  `requirements.txt` y `bandit` sobre todo el código fuente en cada push.
- **Privacidad de datos.** Los datasets que no son libremente redistribuibles (datos del
  reto MeIA 2025, imágenes de lengua de señas) están **excluidos del control de
  versiones**; solo se suben instrucciones de descarga/uso. Los datos de fraude son
  sintéticos por diseño.
- **Versiones mínimas fijadas** en `requirements.txt` para evitar resolver a versiones
  con vulnerabilidades conocidas.

### Reportar una vulnerabilidad

Abre un reporte privado vía GitHub *Security → Report a vulnerability*, o escribe a
**daniel20615@gmail.com**. Recibirás respuesta en menos de una semana.
