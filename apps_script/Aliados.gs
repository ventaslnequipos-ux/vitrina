/**
 * Yellow Yard · Cuentas de aliados (comisionistas)
 *
 * Atiende la vista de aliados de la página (…/vitrina/?aliado=1):
 *   - registro:  crea la cuenta del aliado (nombre, WhatsApp, PIN) en la pestaña "Aliados".
 *   - entrar:    ingreso con WhatsApp + PIN. Cinco intentos fallidos bloquean 15 minutos.
 *   - perfil:    datos del aliado y sus clientes registrados (valida la sesión en cada visita).
 *   - referido:  registra un cliente en la pestaña "Referidos" y avisa si otro aliado ya lo tenía.
 *   - estado:    para la vista del cliente: dice si el WhatsApp de un aliado sigue activo.
 *
 * Cómo retirar a un aliado: en la pestaña "Aliados", columna Estado, elegir "Retirado".
 * Desde ese momento no puede entrar, su sesión se cierra la próxima vez que abra la página
 * y su botón de WhatsApp desaparece de los enlaces que ya compartió.
 * Olvidó el PIN: borrar su celda en "Clave (no editar)"; al entrar, el PIN que escriba queda como nuevo.
 *
 * Va en un proyecto aparte de Apps Script (script.google.com), implementado como
 * aplicación web: Ejecutar como "Yo", acceso "Cualquier persona".
 */
var HOJA_ID = "1AmKrHDG9YT2otmiZ0MEMZ2MkBEavVABn2lC3-WofZzY";
var ESTADO_INICIAL = "Activo";   // cambiar a "Pendiente" para aprobar a mano cada aliado nuevo
var AVISAR_POR_CORREO = true;    // correo a Nestor por cada aliado nuevo y cada cliente registrado
var ZONA = "America/Bogota";

// Columnas (1 = A)
var A = { alta: 1, nombre: 2, tel: 3, empresa: 4, ciudad: 5, estado: 6, clientes: 7, ingreso: 8, notas: 9, clave: 10, sesion: 11 };
var R = { codigo: 1, fecha: 2, aliado: 3, tel: 4, cliente: 5, telCliente: 6, ciudad: 7, lotes: 8, nota: 9, estado: 10, notas: 11 };

function doGet(e) { return responder(atender((e && e.parameter) || {})); }
function doPost(e) {
  var d = {};
  try { d = JSON.parse(e.postData.contents); } catch (x) { d = (e && e.parameter) || {}; }
  return responder(atender(d));
}
function responder(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

function atender(d) {
  try {
    switch (d.accion) {
      case "registro": return registro(d);
      case "entrar": return entrar(d);
      case "perfil": return perfil(d);
      case "referido": return referido(d);
      case "estado": return estadoPublico(d);
      default: return { ok: false, error: "Acción desconocida." };
    }
  } catch (err) {
    return { ok: false, error: "No se pudo completar. Intenta de nuevo en un momento." , detalle: String(err && err.message || err) };
  }
}

// ---------- utilidades ----------
function libro() { return SpreadsheetApp.openById(HOJA_ID); }
function hoja(nombre) { return libro().getSheetByName(nombre); }
function txt(v, max) { return String(v == null ? "" : v).replace(/\s+/g, " ").trim().slice(0, max || 120); }
function tel(v) {
  var n = String(v || "").replace(/\D/g, "");
  if (n.length === 10 && n.charAt(0) === "3") n = "57" + n;
  return /^\d{11,13}$/.test(n) ? n : "";
}
function fmtTel(n) { return n.length === 12 && n.indexOf("57") === 0 ? n.slice(2, 5) + " " + n.slice(5, 8) + " " + n.slice(8) : "+" + n; }
function fecha(d) { return d instanceof Date ? Utilities.formatDate(d, ZONA, "dd/MM/yyyy HH:mm") : String(d || ""); }
function sal() {
  var p = PropertiesService.getScriptProperties(), s = p.getProperty("SAL");
  if (!s) { s = Utilities.getUuid(); p.setProperty("SAL", s); }
  return s;
}
function cifrar(t, pin) {
  var b = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, sal() + "|" + t + "|" + pin, Utilities.Charset.UTF_8);
  return b.map(function (x) { return ("0" + (x & 255).toString(16)).slice(-2); }).join("");
}
function buscar(t) { // fila del aliado (número de fila en la hoja) o 0
  var sh = hoja("Aliados"), n = sh.getLastRow(); if (n < 2) return 0;
  var col = sh.getRange(2, A.tel, n - 1, 1).getDisplayValues();
  for (var i = 0; i < col.length; i++) if (tel(col[i][0]) === t) return i + 2;
  return 0;
}
function fila(r) { var v = hoja("Aliados").getRange(r, 1, 1, 11).getValues()[0]; return { nombre: v[A.nombre - 1], tel: tel(v[A.tel - 1]), empresa: v[A.empresa - 1], ciudad: v[A.ciudad - 1], estado: String(v[A.estado - 1] || ""), clave: String(v[A.clave - 1] || ""), sesion: String(v[A.sesion - 1] || "") }; }
function publico(f) { return { nombre: f.nombre, tel: f.tel, empresa: f.empresa, ciudad: f.ciudad, estado: f.estado }; }
function avisar(asunto, cuerpo) {
  if (!AVISAR_POR_CORREO) return;
  try { MailApp.sendEmail(Session.getEffectiveUser().getEmail(), asunto, cuerpo + "\n\nBase de datos: " + libro().getUrl()); } catch (x) {}
}
function sesionValida(d) {
  var t = tel(d.tel), r = t ? buscar(t) : 0;
  if (!r) return { error: "Tu cuenta ya no existe. Escríbele a Nestor.", salir: true };
  var f = fila(r);
  if (!d.token || f.sesion !== String(d.token)) return { error: "Tu sesión se cerró. Entra de nuevo con tu PIN.", salir: true };
  if (f.estado !== "Activo") return { error: f.estado === "Pendiente" ? "Tu cuenta de aliado está en revisión." : "Tu cuenta de aliado no está activa. Comunícate con Nestor.", salir: true };
  return { r: r, f: f };
}

// ---------- acciones ----------
function registro(d) {
  var t = tel(d.tel), nombre = txt(d.nombre, 80), pin = String(d.pin || "");
  if (nombre.length < 3) return { ok: false, error: "Escribe tu nombre completo." };
  if (!t) return { ok: false, error: "Escribe un número de WhatsApp válido, por ejemplo 300 123 4567." };
  if (!/^\d{4,6}$/.test(pin)) return { ok: false, error: "El PIN debe tener de 4 a 6 números." };
  if (!d.acepta) return { ok: false, error: "Para crear la cuenta debes aceptar las condiciones de aliado." };
  var lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    if (buscar(t)) return { ok: false, error: "Ese número ya tiene una cuenta de aliado. Entra con tu PIN." };
    var sh = hoja("Aliados"), r = sh.getLastRow() + 1, token = Utilities.getUuid(), ahora = new Date();
    sh.getRange(r, A.tel).setNumberFormat("@");
    sh.getRange(r, 1, 1, 11).setValues([[ahora, nombre, t, txt(d.empresa, 80), txt(d.ciudad, 60), ESTADO_INICIAL,
      "=COUNTIF(Referidos!D:D,C" + r + ")", ahora, "Aceptó condiciones de aliado y tratamiento de datos el " + fecha(ahora), cifrar(t, pin), token]]);
    avisar("Nuevo aliado Yellow Yard: " + nombre,
      "Se registró un aliado nuevo en la página.\n\nNombre: " + nombre + "\nWhatsApp: " + fmtTel(t) +
      (d.empresa ? "\nEmpresa: " + txt(d.empresa, 80) : "") + (d.ciudad ? "\nCiudad: " + txt(d.ciudad, 60) : "") +
      "\nEstado: " + ESTADO_INICIAL + "\n\nPara retirarlo: pestaña Aliados, columna Estado, elegir Retirado.\nWhatsApp: https://wa.me/" + t);
    var f = fila(r);
    if (ESTADO_INICIAL !== "Activo") return { ok: true, pendiente: true, mensaje: "Tu cuenta quedó en revisión. Nestor te avisará cuando esté activa." };
    return { ok: true, token: token, perfil: publico(f), referidos: [] };
  } finally { lock.releaseLock(); }
}

function entrar(d) {
  var t = tel(d.tel), pin = String(d.pin || "");
  if (!t || !/^\d{4,6}$/.test(pin)) return { ok: false, error: "Escribe tu WhatsApp y tu PIN." };
  var cache = CacheService.getScriptCache(), k = "fallos_" + t, fallos = Number(cache.get(k) || 0);
  if (fallos >= 5) return { ok: false, error: "Demasiados intentos. Espera 15 minutos o escríbele a Nestor." };
  var r = buscar(t);
  if (!r) return { ok: false, error: "No encontramos una cuenta de aliado con ese número. Crea tu cuenta." };
  var f = fila(r), sh = hoja("Aliados");
  if (f.estado === "Retirado") return { ok: false, error: "Tu cuenta de aliado no está activa. Comunícate con Nestor." };
  if (f.estado === "Pendiente") return { ok: false, error: "Tu cuenta de aliado está en revisión. Nestor te avisará cuando esté activa." };
  if (f.estado !== "Activo") return { ok: false, error: "Tu cuenta de aliado no está activa. Comunícate con Nestor." };
  if (!f.clave) { sh.getRange(r, A.clave).setValue(cifrar(t, pin)); f.clave = cifrar(t, pin); } // PIN nuevo tras borrar la clave
  if (f.clave !== cifrar(t, pin)) {
    cache.put(k, String(fallos + 1), 900);
    return { ok: false, error: "PIN incorrecto." + (fallos + 1 >= 3 ? " Te quedan " + (5 - fallos - 1) + " intentos." : "") };
  }
  cache.remove(k);
  var token = f.sesion || Utilities.getUuid();
  sh.getRange(r, A.ingreso).setValue(new Date());
  if (!f.sesion) sh.getRange(r, A.sesion).setValue(token);
  return { ok: true, token: token, perfil: publico(f), referidos: misReferidos(t) };
}

function perfil(d) {
  var v = sesionValida(d); if (v.error) return { ok: false, error: v.error, salir: v.salir };
  hoja("Aliados").getRange(v.r, A.ingreso).setValue(new Date());
  return { ok: true, perfil: publico(v.f), referidos: misReferidos(v.f.tel) };
}

function misReferidos(t) {
  var sh = hoja("Referidos"), n = sh.getLastRow(); if (n < 2) return [];
  var v = sh.getRange(2, 1, n - 1, 11).getValues(), out = [];
  for (var i = 0; i < v.length; i++) if (tel(v[i][R.tel - 1]) === t)
    out.push({ codigo: v[i][R.codigo - 1], fecha: fecha(v[i][R.fecha - 1]), cliente: v[i][R.cliente - 1], lotes: v[i][R.lotes - 1], estado: v[i][R.estado - 1] });
  return out.reverse();
}

function norm(s) { return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, ""); }

function referido(d) {
  var v = sesionValida(d); if (v.error) return { ok: false, error: v.error, salir: v.salir };
  var cliente = txt(d.cliente, 100); if (cliente.length < 2) return { ok: false, error: "Escribe el nombre del cliente." };
  var telC = String(d.telCliente || "").replace(/\D/g, "").slice(-10);
  var lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    var sh = hoja("Referidos"), n = sh.getLastRow(), previo = null;
    if (n >= 2) {
      var vals = sh.getRange(2, 1, n - 1, 11).getValues();
      for (var i = 0; i < vals.length; i++) {
        var x = vals[i]; if (x[R.estado - 1] === "Descartado" || tel(x[R.tel - 1]) === v.f.tel) continue;
        var mismoTel = telC.length >= 7 && String(x[R.telCliente - 1]).replace(/\D/g, "").slice(-10) === telC;
        var mismoNombre = norm(x[R.cliente - 1]) && norm(x[R.cliente - 1]) === norm(cliente);
        if (mismoTel || mismoNombre) { previo = x; break; }
      }
    }
    var r = n + 1, codigo = "R-" + ("000" + (r - 1)).slice(-4), ahora = new Date();
    var estado = previo ? "Duplicado: revisar" : "Registrado";
    sh.getRange(r, R.tel, 1, 3).setNumberFormat("@");
    sh.getRange(r, 1, 1, 11).setValues([[codigo, ahora, v.f.nombre, v.f.tel, cliente, txt(d.telCliente, 30), txt(d.ciudad, 60), txt(d.lotes, 120), txt(d.nota, 300), estado,
      previo ? "Ya lo había registrado " + previo[R.aliado - 1] + " (" + previo[R.codigo - 1] + ", " + fecha(previo[R.fecha - 1]) + ")" : ""]]);
    avisar((previo ? "REVISAR cliente duplicado · " : "Cliente referido · ") + cliente + " · " + v.f.nombre,
      "Código: " + codigo + "\nFecha: " + fecha(ahora) + "\nAliado: " + v.f.nombre + " · " + fmtTel(v.f.tel) +
      "\nCliente: " + cliente + (d.telCliente ? "\nCelular del cliente: " + txt(d.telCliente, 30) : "") + (d.ciudad ? "\nCiudad: " + txt(d.ciudad, 60) : "") +
      (d.lotes ? "\nEquipos: " + txt(d.lotes, 120) : "") + (d.nota ? "\nNota: " + txt(d.nota, 300) : "") +
      (previo ? "\n\nATENCIÓN: este cliente ya estaba registrado por " + previo[R.aliado - 1] + " (" + previo[R.codigo - 1] + ", " + fecha(previo[R.fecha - 1]) + ")." : ""));
    return { ok: true, codigo: codigo, fecha: fecha(ahora), duplicado: !!previo, referidos: misReferidos(v.f.tel) };
  } finally { lock.releaseLock(); }
}

function estadoPublico(d) {
  var t = tel(d.tel), r = t ? buscar(t) : 0;
  return { ok: true, activo: !!r && fila(r).estado === "Activo" };
}

/** Ejecútala una vez desde el editor (botón Ejecutar) para dar los permisos de la hoja y del correo. */
function autorizar() {
  Logger.log(libro().getName() + " · " + hoja("Aliados").getName() + " · " + hoja("Referidos").getName());
  Logger.log("Correo de avisos: " + Session.getEffectiveUser().getEmail());
  sal();
}
