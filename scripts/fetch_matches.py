#!/usr/bin/env python3
"""
Descarga datos del Mundial 2026 desde API-Football y los guarda como JSON
estatico en data/partidos.json para que la pagina de GitHub Pages los lea
sin necesidad de llamar a la API desde el navegador de cada usuario.

Requiere la variable de entorno API_FOOTBALL_KEY (se configura como
"secret" en GitHub Actions, nunca se sube al repo en texto plano).

Uso:
    API_FOOTBALL_KEY=xxxx python3 fetch_matches.py
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib import request, error

API_BASE = "https://v3.football.api-sports.io"
LEAGUE_ID = 1          # World Cup, segun documentacion API-Football
SEASON = 2026
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "partidos.json")


def api_get(endpoint: str, params: dict, api_key: str) -> dict:
    """Llama a un endpoint de API-Football y devuelve el JSON parseado."""
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{API_BASE}/{endpoint}?{query}"
    req = request.Request(url, headers={"x-apisports-key": api_key})
    try:
        with request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as e:
        print(f"[ERROR HTTP] {endpoint}: {e.code} {e.reason}", file=sys.stderr)
        return {"response": []}
    except Exception as e:  # noqa: BLE001 - queremos seguir aunque falle una llamada
        print(f"[ERROR] {endpoint}: {e}", file=sys.stderr)
        return {"response": []}


def extraer_estadisticas(stats_response: list) -> dict:
    """Convierte el bloque de /fixtures/statistics en un dict simple por equipo."""
    resultado = {}
    for bloque in stats_response:
        equipo = bloque.get("team", {}).get("name", "desconocido")
        valores = {}
        for item in bloque.get("statistics", []):
            valores[item.get("type")] = item.get("value")
        resultado[equipo] = valores
    return resultado


def normalizar_partido(fixture: dict, stats_por_equipo: dict | None = None) -> dict:
    fx = fixture.get("fixture", {})
    teams = fixture.get("teams", {})
    goals = fixture.get("goals", {})
    score = fixture.get("score", {})

    home = teams.get("home", {}).get("name")
    away = teams.get("away", {}).get("name")

    partido = {
        "id": fx.get("id"),
        "fecha_utc": fx.get("date"),
        "estadio": fx.get("venue", {}).get("name"),
        "ciudad": fx.get("venue", {}).get("city"),
        "estado": fx.get("status", {}).get("short"),  # NS, 1H, HT, 2H, ET, P, FT, etc.
        "minuto": fx.get("status", {}).get("elapsed"),
        "grupo": fixture.get("league", {}).get("round"),
        "local": home,
        "visitante": away,
        "goles_local": goals.get("home"),
        "goles_visitante": goals.get("away"),
        "goles_primer_tiempo": {
            "local": score.get("halftime", {}).get("home"),
            "visitante": score.get("halftime", {}).get("away"),
        },
        "goles_segundo_tiempo": None,  # se calcula abajo si hay datos
        "hubo_alargue": score.get("extratime", {}).get("home") is not None,
        "goles_alargue": {
            "local": score.get("extratime", {}).get("home"),
            "visitante": score.get("extratime", {}).get("away"),
        },
        "hubo_penales": score.get("penalty", {}).get("home") is not None,
        "penales": {
            "local": score.get("penalty", {}).get("home"),
            "visitante": score.get("penalty", {}).get("away"),
        },
    }

    # Goles del segundo tiempo = goles totales (90min) - goles primer tiempo
    ht_l = partido["goles_primer_tiempo"]["local"]
    ht_v = partido["goles_primer_tiempo"]["visitante"]
    ft_l = score.get("fulltime", {}).get("home")
    ft_v = score.get("fulltime", {}).get("away")
    if ht_l is not None and ft_l is not None:
        partido["goles_segundo_tiempo"] = {
            "local": ft_l - ht_l,
            "visitante": ft_v - ht_v,
        }

    # Estadisticas (tiros al arco, tarjetas) si se obtuvieron
    if stats_por_equipo and home in stats_por_equipo:
        st = stats_por_equipo.get(home, {})
        partido["tiros_arco_local"] = st.get("Shots on Goal")
        partido["tarjetas_amarillas_local"] = st.get("Yellow Cards")
        partido["tarjetas_rojas_local"] = st.get("Red Cards")
    if stats_por_equipo and away in stats_por_equipo:
        st = stats_por_equipo.get(away, {})
        partido["tiros_arco_visitante"] = st.get("Shots on Goal")
        partido["tarjetas_amarillas_visitante"] = st.get("Yellow Cards")
        partido["tarjetas_rojas_visitante"] = st.get("Red Cards")

    return partido


def main():
    api_key = os.environ.get("API_FOOTBALL_KEY")
    if not api_key:
        print("[ERROR] Falta la variable de entorno API_FOOTBALL_KEY", file=sys.stderr)
        sys.exit(1)

    print("Consultando fixtures del Mundial 2026...")
    data = api_get("fixtures", {"league": LEAGUE_ID, "season": SEASON}, api_key)
    fixtures = data.get("response", [])
    print(f"  -> {len(fixtures)} partidos recibidos")

    # Para no gastar cuota (free = 100 req/dia), solo pedimos estadisticas
    # detalladas (tiros al arco, tarjetas) de partidos en vivo o recien
    # terminados en las ultimas horas. El resto se guarda sin ese detalle.
    partidos = []
    llamadas_stats_usadas = 0
    MAX_LLAMADAS_STATS = 15  # margen de seguridad dentro de las 100/dia

    ahora = datetime.now(timezone.utc)

    for fixture in fixtures:
        estado = fixture.get("fixture", {}).get("status", {}).get("short")
        fixture_id = fixture.get("fixture", {}).get("id")

        estados_relevantes = {"1H", "HT", "2H", "ET", "P", "FT", "AET", "PEN"}
        stats_por_equipo = None

        if estado in estados_relevantes and llamadas_stats_usadas < MAX_LLAMADAS_STATS:
            stats_data = api_get(
                "fixtures/statistics", {"fixture": fixture_id}, api_key
            )
            stats_por_equipo = extraer_estadisticas(stats_data.get("response", []))
            llamadas_stats_usadas += 1
            time.sleep(0.3)  # respeta el limite de 10 req/min del plan free

        partidos.append(normalizar_partido(fixture, stats_por_equipo))

    salida = {
        "actualizado_utc": ahora.isoformat(),
        "total_partidos": len(partidos),
        "partidos": partidos,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    print(f"Listo. Guardado en {OUTPUT_PATH}")
    print(f"Llamadas a /fixtures/statistics usadas: {llamadas_stats_usadas}")


if __name__ == "__main__":
    main()
