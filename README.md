# Mundial 2026 Picks 🏆

Página de predicciones del Mundial 2026 entre amigos: partidos en vivo,
bingo diario, picks tipo pick'em y subasta de selecciones — alojada gratis
en GitHub Pages, sin servidor propio.

## Estado del proyecto (fase por fase)

- [x] **Fase 1 — Página base + datos automáticos de partidos** (esta entrega)
- [ ] Fase 2 — Registro de usuarios + picks (Google Form/Sheet) + ranking
- [ ] Fase 3 — Bingo diario interactivo
- [ ] Fase 4 — Subasta interactiva de selecciones

---

## Fase 1: cómo dejarla funcionando

### 1. Subir este proyecto a tu repositorio

```bash
cd mundial2026
git init
git add .
git commit -m "Fase 1: pagina base + datos automaticos del Mundial"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### 2. Activar GitHub Pages

1. En tu repo de GitHub: **Settings → Pages**.
2. En "Branch", elegí `main` y la carpeta `/docs`.
3. Guardar. En 1-2 minutos tu página estará en
   `https://TU_USUARIO.github.io/TU_REPO/`.

### 3. Conseguir tu API key gratuita de datos del Mundial

1. Andá a [api-football.com](https://www.api-football.com/) (o
   [dashboard.api-football.com](https://dashboard.api-football.com/register))
   y creá una cuenta gratis.
2. Copiá tu API key del dashboard (plan **Free**, 100 requests/día).
3. En tu repo de GitHub: **Settings → Secrets and variables → Actions →
   New repository secret**.
   - Nombre: `API_FOOTBALL_KEY`
   - Valor: tu API key
4. Guardar. **Nunca pongas la key directamente en el código** — por eso
   usamos este "secret", para que no quede visible públicamente.

### 4. Probar la actualización automática

1. En tu repo: pestaña **Actions**.
2. Elegí el workflow **"Actualizar datos del Mundial"**.
3. Click en **"Run workflow"** para probarlo manualmente la primera vez.
4. Si todo sale bien, vas a ver un commit automático actualizando
   `data/partidos.json`.
5. A partir de ahí, corre solo cada 3 horas (podés ajustar el horario en
   `.github/workflows/update.yml`, línea `cron`).

### 5. Verificar

Abrí tu página publicada y deberías ver el marcador destacado y la lista
de partidos. Si la API key todavía no está configurada, vas a ver los
datos de ejemplo que vienen precargados en `docs/data/partidos.json`.

---

## Estructura del proyecto

```
mundial2026/
├── docs/                   ← esto es lo que GitHub Pages publica
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── data/
│       └── partidos.json   ← se regenera solo, no lo edites a mano
├── scripts/
│   └── fetch_matches.py    ← descarga datos desde API-Football
└── .github/workflows/
    └── update.yml          ← corre el script automáticamente
```

## Notas importantes

- **No edites `docs/data/partidos.json` a mano** una vez que el Action esté
  funcionando — se sobrescribe solo.
- El plan gratuito de API-Football da 100 requests/día. El script está
  diseñado para gastar muy pocos (1 para el calendario general + hasta 15
  para estadísticas de partidos en vivo/recientes), dejando margen de
  sobra incluso corriendo cada 3 horas.
- Si en algún momento el Action falla, revisá la pestaña **Actions** del
  repo — ahí se ve el error exacto (API key mal puesta, límite alcanzado,
  etc.).

## Próximos pasos

Cuando confirmes que esta fase funciona en tu repo real, seguimos con la
**Fase 2**: registro de usuarios por correo (Google Form), formulario de
picks por jornada, y la tabla de ranking de puntos.
