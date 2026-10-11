"""Reporte en PDF de PC Check Assist. Solo escribe el PDF que el admin pide exportar."""
import hashlib, json, os, time
import pccheck_core as _core


def _T(s):
    return _core._T(s)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

RED = colors.HexColor("#DC2626")
INK = colors.HexColor("#1B1013")
MUTED = colors.HexColor("#6B5B5E")
LINE = colors.HexColor("#E6DADC")
OKC, MIDC, BADC = colors.HexColor("#16A34A"), colors.HexColor("#D97706"), colors.HexColor("#DC2626")
MUTEDC = colors.HexColor("#6B7280")


def _fonts():
    cands = [(r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf"),
             ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")]
    for reg, bold in cands:
        if os.path.isfile(reg) and os.path.isfile(bold):
            pdfmetrics.registerFont(TTFont("R", reg))
            pdfmetrics.registerFont(TTFont("B", bold))
            return "R", "B"
    return "Helvetica", "Helvetica-Bold"


def fingerprint(res):
    data = {k: v for k, v in res.items() if k != "fingerprint"}
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def make_pdf(res, path, logo=None, brand=None, extra=None):
    R, B = _fonts()
    fp = fingerprint(res)
    brand = brand or {}
    is_vip = bool(brand.get("vip"))
    checker = (brand.get("checker") or "").strip()
    league = (brand.get("league") or "").strip()
    extra = extra or {}
    player = (extra.get("player") or "").strip()
    s = lambda n, **k: ParagraphStyle(n, fontName=k.pop("f", R), fontSize=k.pop("s", 9), leading=k.pop("l", 12), textColor=k.pop("c", INK), **k)
    body, small, mono = s("b"), s("sm", s=8, l=10, c=MUTED), s("m", s=7.5, l=9.5, c=MUTED)
    h2 = s("h2", f=B, s=11, l=14, c=RED, spaceBefore=10, spaceAfter=4)
    esc = lambda t: str(t if t is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    verdict = {"limpio": ("SIN BANDERAS", OKC), "revisar": (_T("REVISAR CON CALMA"), MIDC),
               "sospechoso": ("BANDERAS DETECTADAS", BADC)}[res["verdict"]]

    foot_left = "PC Check Assist by Arroz  -  Huella SHA-256: " + fp
    if not is_vip:
        foot_left = "PC Check Assist by Arroz (version libre)  -  SHA-256: " + fp

    def footer(c, d):
        c.saveState()
        c.setFont(R, 7)
        c.setFillColor(MUTED)
        c.drawString(18 * mm, 10 * mm, foot_left)
        c.drawRightString(A4[0] - 18 * mm, 10 * mm, "Pagina %d" % d.page)
        c.restoreState()

    story = []
    right = "<font color='#F7ECEC'>by Arroz  -  Reporte de revision</font><br/><font color='#CFA9AD' size='8'>%s  -  %s s</font>" % (esc(res["time"]), esc(res.get("secs")))
    if is_vip and (checker or league):
        bits = []
        if league:
            bits.append("Liga: " + esc(league))
        if checker:
            bits.append("Revisor: " + esc(checker))
        right = "<font color='#F7ECEC'>%s</font><br/><font color='#CFA9AD' size='8'>%s  -  %s s</font>" % ("  -  ".join(bits), esc(res["time"]), esc(res.get("secs")))
    if player:
        right = right.replace("<br/>", "<br/><font color='#FFFFFF' size='9'><b>Jugador: %s</b></font><br/>" % esc(player), 1)
    title_txt = "<font color='white'><b>PC CHECK ASSIST</b></font>"
    if is_vip:
        title_txt += "  <font color='#A78BFA' size='9'><b>VIP</b></font>"
    head = Table([[Paragraph(title_txt, s("t", f=B, s=17, l=20)),
                   Paragraph(right, s("t2", s=9, l=12, alignment=2))]],
                 colWidths=[85 * mm, 89 * mm])
    head.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), INK), ("LINEBELOW", (0, 0), (-1, -1), 3, RED),
                              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 10),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 10), ("LEFTPADDING", (0, 0), (-1, -1), 10)]))
    story += [head, Spacer(1, 8)]

    rk = res.get("risk") or {"score": 0, "level": "bajo", "factors": []}
    lvl_txt = {"bajo": _T("RIESGO BAJO"), "medio": _T("RIESGO MEDIO"), "alto": _T("RIESGO ALTO")}.get(rk["level"], "RIESGO")
    vb = Table([[Paragraph("<font color='white'><b>%s  -  %d/100</b></font>" % (lvl_txt, rk["score"]), s("v", f=B, s=13, l=16)),
                 Paragraph("<font color='white'>%s<br/>%d flags prohibidos  -  %d alertas  -  %d flags leidos</font>"
                           % (verdict[0], len(res["flags"]), len(res["alerts"]), res["total_flags"]), s("v2", s=8.5, l=11, alignment=2))]],
               colWidths=[88 * mm, 86 * mm])
    vb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), verdict[1]), ("TOPPADDING", (0, 0), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story += [vb, Paragraph("La puntuacion es orientativa: suma indicios, no prueba nada por si sola. La decision final es del admin.", small), Spacer(1, 4)]

    def table(rows, widths, header):
        data = [[Paragraph("<b>%s</b>" % h, small) for h in header]] + rows
        t = Table(data, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F6EFF0")),
                               ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
        return t

    def section(title, items, empty, widths=None, header=None, limit=40):
        if not items:
            story.append(KeepTogether([Paragraph(title, h2), Paragraph(empty, small)]))
            return
        t = table(items[:limit], widths, header)
        story.append(KeepTogether([Paragraph(title, h2), t]) if len(items) <= 12 else Paragraph(title, h2))
        if len(items) > 12:
            story.append(t)
        if len(items) > limit:
            story.append(Paragraph("... y %d mas (ver el archivo JSON del reporte)." % (len(items) - limit), small))

    P = lambda t, st=body: Paragraph(esc(t), st)

    section("Por que este puntaje", [[P("+%d" % x["pts"], s("pt", f=B, s=9, c=BADC if x["pts"] >= 30 else (MIDC if x["pts"] >= 8 else MUTED))),
                                       P(x["title"], s("ft", f=B, s=8.5, l=11)), P(x["detail"], mono)] for x in rk["factors"]],
            "No se encontraron indicios.", [14 * mm, 58 * mm, 102 * mm], ["Puntos", "Indicio", "Detalle"])
    dfx = res.get("diff")
    if dfx:
        section("Cambios desde la revision anterior (hace %s min, riesgo %s -> %s)" % (dfx.get("minutes"), dfx.get("prev_score"), rk["score"]),
                [[P({"high": "ALTA", "mid": "MEDIA"}.get(x["lvl"], "INFO"), s("dl", f=B, s=8, c=BADC if x["lvl"] == "high" else (MIDC if x["lvl"] == "mid" else MUTED))),
                  P(x["text"])] for x in dfx.get("items", [])],
                "Nada relevante cambio entre las dos revisiones.", [18 * mm, 156 * mm], ["Nivel", "Cambio"])
    ck = extra.get("checklist") or []
    if ck:
        section(_T("Checklist del revisor"), [[P("SI" if c.get("done") else "NO", s("ck", f=B, s=8, c=OKC if c.get("done") else BADC)), P(c.get("text", ""))] for c in ck],
                "", [14 * mm, 160 * mm], ["Hecho", "Paso"])

    section("Alertas", [[P({"high": "ALTA", "mid": "MEDIA"}.get(a["lvl"], "INFO"), s("lv", f=B, s=8, c=BADC if a["lvl"] == "high" else (MIDC if a["lvl"] == "mid" else MUTEDC))), P(a["msg"])]
                        for a in res["alerts"]], "Sin alertas.", [18 * mm, 156 * mm], ["Nivel", "Detalle"])
    section(_T("Flags ilegales o sospechosos"), [[P(f["name"], s("fn", f=B, s=8.5, l=11)), P(f["value"], mono), P(f["why"], mono),
                                               P("%s  -  mod. %s%s" % (f["owner"], f.get("mtime", ""), "  -  en %d archivos" % f["n_files"] if f.get("n_files", 1) > 1 else ""), mono)]
                                              for f in res["flags"]], _T("Ningun flag coincide con las reglas."),
            [58 * mm, 18 * mm, 38 * mm, 60 * mm], ["Flag", "Valor", "Regla", "Origen"], 60)
    lf = [(x, f) for x in res.get("log_findings", []) for f in x["illegal"]]
    section(_T("Flags prohibidos vistos en los logs de Roblox (cargados al abrir el juego)"),
            [[P(f["name"], s("fn2", f=B, s=8.5, l=11)), P(f["value"], mono),
              P("ACEPTADO" if f["accepted"] else "RECHAZADO", s("ac", f=B, s=8, c=BADC if f["accepted"] else MIDC)),
              P("%s  -  %s" % (x["log"], x["when"]), mono)] for x, f in lf],
            "Los logs no muestran flags prohibidos.", [58 * mm, 18 * mm, 24 * mm, 74 * mm], ["Flag", "Valor", "Roblox", "Log"])
    rp = res.get("roblox_procs") or []
    section("Roblox abierto", [[P("PID %s" % r.get("pid")), P(r.get("parent") or "?"), P("%s (hace %s min)" % (r.get("start"), r.get("up_min"))), P(r.get("cmd"), mono)] for r in rp],
            "Roblox no estaba abierto.", [20 * mm, 24 * mm, 42 * mm, 88 * mm], ["Proceso", "Lanzado por", "Inicio", "Argumentos"])
    section("RobloxPlayerBeta.exe", [[P(e["path"], mono), P("VALIDA" if e["valid"] else ("NO VERIFICADA" if e["valid"] is None else "INVALIDA"), s("sg", f=B, s=8, c=OKC if e["valid"] else (MUTEDC if e["valid"] is None else BADC))), P(e["sha"], mono)] for e in res["exes"]],
            "No se encontro el ejecutable.", [70 * mm, 20 * mm, 84 * mm], ["Ruta", "Firma", "SHA-256"])
    section(_T("Straps: procesos, carpetas y archivos fuera de lugar"),
            [[P("Proceso"), P("%s (PID %s)" % (p["name"], p["pid"]), mono)] for p in res["procs"]] +
            [[P("Carpeta"), P(d, mono)] for d in res["dirs"]] +
            [[P(h["why"]), P(h["path"], mono)] for h in res.get("hidden", [])], "Sin rastros de straps.", [48 * mm, 126 * mm], ["Tipo", "Ruta"])
    section("Ejecutables de straps detectados por su firma interna (incluye renombrados)",
            [[P(x["why"], s("ew", f=B, s=8.5, l=11, c=BADC if x["kind"] == "renombrado" else INK)), P(x["path"], mono), P(x.get("product", ""), mono)] for x in res.get("exe_ids", [])],
            "Ningun ejecutable de strap renombrado o suelto.", [44 * mm, 96 * mm, 34 * mm], ["Que es", "Ruta", "Producto"])
    section(_T("Cambios recientes en archivos"), [[P(r["path"], mono), P(r["mtime"], mono)] for r in res.get("recent", [])],
            "Sin cambios recientes.", [140 * mm, 34 * mm], ["Archivo", "Modificado"], 30)
    section(_T("Papelera de reciclaje (relacionado)"), [[P(x["name"]), P(x["from"], mono), P(x["date"], mono)] for x in res.get("recycle", [])],
            "Nada relacionado.", [50 * mm, 90 * mm, 34 * mm], ["Elemento", "Origen", "Borrado"])
    KN = {"strap": "Strap", "tool": "Herramienta", "inyector": "Inyector", "borrado": "Borrado"}
    section(_T("Historial de ejecucion de Windows (UserAssist%s)") % (" + BAM" if res.get("bam_ok") else ", sin BAM: falto administrador"),
            [[P("%s  (%s)" % (x["name"], KN.get(x.get("kind"), "")), s("xn", f=B, s=8.5, l=11, c=BADC if x.get("lvl") == "high" else INK)),
              P(x["path"], mono), P(x.get("when") or "?", mono),
              P("EXISTE" if x.get("exists") else "YA NO EXISTE", s("xe", f=B, s=8, c=MUTED if x.get("exists") else BADC))]
             for x in res.get("exec", [])],
            "Windows no registra straps, inyectores ni herramientas ejecutados.", [42 * mm, 82 * mm, 28 * mm, 22 * mm],
            ["Programa", "Ruta", "Ultima vez", "Estado"])
    if res.get("ua_off"):
        story.append(Paragraph(_T("En esta PC esta apagado 'Permitir que Windows rastree los inicios de aplicaciones', asi que UserAssist no guarda historial.")
                               + ("" if res.get("bam_ok") else " Sin administrador tampoco se pudo leer BAM: el historial de ejecucion queda incompleto."), small))
    section("Ejecutados en las ultimas 72 h que ya no existen", [[P(x["name"]), P(x["path"], mono), P(x.get("when") or "", mono)] for x in res.get("exec_gone", [])],
            "Nada.", [40 * mm, 106 * mm, 28 * mm], ["Programa", "Ruta", "Ultima vez"], 30)
    section("Arranque automatico (registro, carpeta de Inicio, tareas programadas)",
            [[P(a["name"], s("an", f=B, s=8.5, l=11)), P(a["where"], mono), P(a["target"], mono)] for a in res.get("autoruns", [])],
            "Ningun strap, inyector ni herramienta se abre solo con Windows.", [40 * mm, 44 * mm, 90 * mm], ["Entrada", "Donde", "Destino"])
    if res.get("defender_ok"):
        section(_T("Exclusiones del antivirus (Defender)"),
                [[P(d["value"], mono), P(d["type"]), P((d.get("kind") or "").upper(), s("dk", f=B, s=8, c=BADC if d["lvl"] == "high" else (MIDC if d["lvl"] == "mid" else MUTED)))]
                 for d in res.get("defender", [])], "Sin exclusiones.", [110 * mm, 34 * mm, 30 * mm], ["Exclusion", "Tipo", "Marca"])
    else:
        story.append(Paragraph(_T("Exclusiones del antivirus (Defender)"), h2))
        story.append(Paragraph(_T("No se pudieron leer: Windows solo las muestra como administrador."), small))
    tl = [e for e in res.get("timeline", []) if res.get("now_ep", 0) - e["ep"] <= 2 * 86400]
    lvc = {"high": BADC, "mid": MIDC, "check": RED}
    section("Linea de tiempo (ultimas 48 h)", [[P(e["when"], mono), P(e["text"], s("te", s=8.5, l=11, c=lvc.get(e["lvl"], INK)))] for e in tl[-60:]],
            "Sin eventos en las ultimas 48 h.", [30 * mm, 144 * mm], ["Cuando", "Que paso"], 60)
    mon = extra.get("monitor") or []
    if mon:
        section("Monitor en vivo durante el check", [[P(e["when"], mono), P(e["text"], s("me", s=8.5, l=11, c=lvc.get(e["lvl"], INK)))] for e in mon],
                "", [22 * mm, 152 * mm], ["Hora", "Evento"], 80)
    section("Logs encontrados", [[P(l["owner"]), P(l["name"], mono), P("%s  (%d KB)" % (l["mtime"], l["kb"]), mono)] for l in res["logs"]],
            "Sin logs.", [26 * mm, 100 * mm, 48 * mm], ["Origen", "Archivo", "Fecha"])

    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm, bottomMargin=18 * mm,
                            title="PC Check Assist - Reporte", author="PC Check Assist by Arroz")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return fp
