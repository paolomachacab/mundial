// ==========================================================================
// MUNDIAL 2026 PICKS — lee data/partidos.json (generado por GitHub Actions)
// y arma el marcador destacado + la lista de partidos del dia.
// No llama a ninguna API externa desde el navegador: todo sale de un
// archivo estatico del propio repo, asi que no hay limite de uso.
// ==========================================================================

const RUTA_DATOS = "data/partidos.json";

const ESTADOS_VIVO = new Set(["1H", "HT", "2H", "ET", "P", "BT"]);
const ESTADOS_FINALIZADO = new Set(["FT", "AET", "PEN"]);

const ETIQUETAS_ESTADO = {
  NS: "Por jugar",
  TBD: "Por confirmar",
  "1H": "1er tiempo",
  HT: "Entretiempo",
  "2H": "2do tiempo",
  ET: "Alargue",
  BT: "Descanso alargue",
  P: "Penales",
  FT: "Finalizado",
  AET: "Finalizado (alargue)",
  PEN: "Finalizado (penales)",
  PST: "Postergado",
  CANC: "Cancelado",
};

function iniciales(nombreEquipo) {
  if (!nombreEquipo) return "—";
  const partes = nombreEquipo.split(" ").filter(Boolean);
  if (partes.length === 1) return partes[0].slice(0, 3).toUpperCase();
  return partes.map(p => p[0]).join("").slice(0, 3).toUpperCase();
}

function formatearHora(fechaIso) {
  if (!fechaIso) return "—";
  const fecha = new Date(fechaIso);
  return fecha.toLocaleString("es-BO", {
    weekday: "short",
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function textoMarcador(partido) {
  if (partido.goles_local === null || partido.goles_local === undefined) {
    return "vs";
  }
  return `${partido.goles_local} : ${partido.goles_visitante}`;
}

function claseEstadoChip(estado) {
  if (ESTADOS_VIVO.has(estado)) return "partido__estado-chip--vivo";
  if (ESTADOS_FINALIZADO.has(estado)) return "partido__estado-chip--finalizado";
  return "";
}

function renderizarMarcadorDestacado(partido) {
  const contenedor = document.getElementById("marcador-destacado");
  if (!partido) {
    contenedor.querySelector(".marcador__cuerpo").innerHTML =
      "<p class='estado-carga'>No hay partidos cargados todavía.</p>";
    return;
  }

  const esVivo = ESTADOS_VIVO.has(partido.estado);
  const etiqueta = ETIQUETAS_ESTADO[partido.estado] || partido.estado;
  const minuto = partido.minuto ? ` · ${partido.minuto}'` : "";

  contenedor.querySelector(".marcador__equipo--local span:last-child").textContent = partido.local || "Por definir";
  contenedor.querySelector(".marcador__equipo--local .marcador__bandera").textContent = iniciales(partido.local);

  contenedor.querySelector(".marcador__equipo--visitante span:last-child").textContent = partido.visitante || "Por definir";
  contenedor.querySelector(".marcador__equipo--visitante .marcador__bandera").textContent = iniciales(partido.visitante);

  contenedor.querySelector(".marcador__goles").textContent = textoMarcador(partido);

  const chipEstado = contenedor.querySelector(".marcador__estado");
  chipEstado.textContent = etiqueta + minuto;
  chipEstado.className = "marcador__estado" + (esVivo ? " marcador__estado--vivo" : "");

  document.getElementById("marcador-estadio").textContent = partido.estadio
    ? `${partido.estadio}${partido.ciudad ? " · " + partido.ciudad : ""}`
    : "Estadio por confirmar";
  document.getElementById("marcador-grupo").textContent = partido.grupo || "";
}

function renderizarListaPartidos(partidos) {
  const contenedor = document.getElementById("lista-partidos");

  if (!partidos.length) {
    contenedor.innerHTML = "<p class='estado-carga'>No hay partidos para mostrar todavía.</p>";
    return;
  }

  contenedor.innerHTML = partidos.map(p => `
    <div class="partido">
      <div class="partido__hora">${formatearHora(p.fecha_utc)}</div>
      <div class="partido__equipos">
        <span class="partido__nombre partido__nombre--local">${p.local || "Por definir"}</span>
        <span class="partido__marcador">${textoMarcador(p)}</span>
        <span class="partido__nombre partido__nombre--visitante">${p.visitante || "Por definir"}</span>
      </div>
      <span class="partido__estado-chip ${claseEstadoChip(p.estado)}">${ETIQUETAS_ESTADO[p.estado] || p.estado}</span>
    </div>
  `).join("");
}

function elegirPartidoDestacado(partidos) {
  // Prioridad: 1) en vivo  2) el proximo por jugar  3) el ultimo finalizado
  const enVivo = partidos.find(p => ESTADOS_VIVO.has(p.estado));
  if (enVivo) return enVivo;

  const proximos = partidos
    .filter(p => p.estado === "NS" && p.fecha_utc)
    .sort((a, b) => new Date(a.fecha_utc) - new Date(b.fecha_utc));
  if (proximos.length) return proximos[0];

  const finalizados = partidos
    .filter(p => ESTADOS_FINALIZADO.has(p.estado) && p.fecha_utc)
    .sort((a, b) => new Date(b.fecha_utc) - new Date(a.fecha_utc));
  if (finalizados.length) return finalizados[0];

  return partidos[0] || null;
}

function formatearMarcaTiempo(fechaIso) {
  if (!fechaIso) return "—";
  const fecha = new Date(fechaIso);
  return "Actualizado " + fecha.toLocaleString("es-BO", {
    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

async function iniciar() {
  try {
    const respuesta = await fetch(RUTA_DATOS, { cache: "no-store" });
    if (!respuesta.ok) throw new Error("No se pudo leer " + RUTA_DATOS);
    const datos = await respuesta.json();

    const partidos = datos.partidos || [];

    renderizarMarcadorDestacado(elegirPartidoDestacado(partidos));
    renderizarListaPartidos(partidos);

    const marca = formatearMarcaTiempo(datos.actualizado_utc);
    document.getElementById("ultima-actualizacion").textContent = marca;
    document.getElementById("pie-actualizacion").textContent = marca;
  } catch (err) {
    console.error(err);
    document.getElementById("lista-partidos").innerHTML =
      "<p class='estado-carga'>No se pudieron cargar los partidos. Intentá recargar la página.</p>";
  }
}

iniciar();
