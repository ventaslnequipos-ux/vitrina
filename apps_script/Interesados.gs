/**
 * Yellow Yard · Formulario "Me interesa"
 * Recibe los datos que deja un visitante en la página y:
 *   1) los anota en la pestaña "Interesados" de la Base de datos Yellow Yard;
 *   2) te envía un correo con los datos para que lo contactes.
 * Va pegado en: Base de datos Yellow Yard > Extensiones > Apps Script.
 */
function doPost(e) {
  var d = (e && e.parameter) || {};
  if (d.web) return ContentService.createTextOutput("ok"); // casilla trampa contra robots
  var hoja = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Interesados");

  // Primera fila vacía según la columna A (la columna C se llena sola con el nombre del equipo)
  var colA = hoja.getRange("A:A").getValues();
  var fila = 2;
  while (fila <= colA.length && colA[fila - 1][0] !== "") fila++;

  var notas = [d.ciudad ? "Ciudad: " + d.ciudad : "", d.mensaje || "", "Llegó por la página web"].filter(String).join(" · ");
  hoja.getRange(fila, 1, 1, 2).setValues([[new Date(), "'" + (d.lote || "")]]);
  hoja.getRange(fila, 4, 1, 3).setValues([[d.nombre || "", d.telefono || "", d.correo || ""]]);
  hoja.getRange(fila, 8, 1, 2).setValues([["Nuevo", notas]]);

  var tel = String(d.telefono || "").replace(/\D/g, "");
  if (tel.length === 10) tel = "57" + tel;
  var cuerpo = "Nuevo interesado en Yellow Yard\n\n" +
    "Equipo: Lote " + d.lote + " · " + d.equipo + " (" + d.precio + ")\n" +
    "Nombre: " + d.nombre + "\n" +
    "Celular: " + d.telefono + "\n" +
    (d.ciudad ? "Ciudad: " + d.ciudad + "\n" : "") +
    (d.correo ? "Correo: " + d.correo + "\n" : "") +
    (d.mensaje ? "Mensaje: " + d.mensaje + "\n" : "") +
    "\nEscribirle por WhatsApp: https://wa.me/" + tel + "\n" +
    "Base de datos: " + SpreadsheetApp.getActiveSpreadsheet().getUrl();
  MailApp.sendEmail(Session.getEffectiveUser().getEmail(), "Interesado: lote " + d.lote + " · " + d.equipo + " · " + d.nombre, cuerpo);

  return ContentService.createTextOutput("ok");
}
