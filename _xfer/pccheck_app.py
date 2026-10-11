import json, os, re, subprocess, sys, threading, time, urllib.request, webbrowser

DISCORD_URL = "https://discord.gg/nXfqTgbVUt"
# Auto-actualizacion: pega aqui la URL CRUDA (raw) de tu version.json.
# Ej GitHub: https://raw.githubusercontent.com/USUARIO/REPO/main/version.json
UPDATE_URL = "https://api.github.com/repos/arrozlarpero1234-afk/skibidi/contents/version.json"


def _ver_gt(a, b):
    def parts(v):
        return [int(x) if x.isdigit() else 0 for x in re.split(r"[.\-]", str(v or ""))]
    pa, pb = parts(a), parts(b)
    n = max(len(pa), len(pb)); pa += [0] * (n - len(pa)); pb += [0] * (n - len(pb))
    return pa > pb

import pccheck_core as core
import licencia_pc as lic
import pccheck_monitor

APP_VERSION = "4.0"
LAD = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
DATA_DIR = os.path.join(LAD, "PCCheckAssist")
os.makedirs(DATA_DIR, exist_ok=True)
LICENSE_FILE = os.path.join(DATA_DIR, "license.key")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
PROFILES_DIR = os.path.join(DATA_DIR, "perfiles")
NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def _read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


THEMES = ("clasico", "patrio", "navidad", "muertos", "halloween")
FREE_THEMES = ("clasico", "patrio")  # gratis para todos (no VIP)


class Api:
    def __init__(self):
        self._res = None
        self._window = None
        self._ext = None
        self._settings = _read_json(SETTINGS_FILE, {}) or {}
        try:
            with open(LICENSE_FILE, encoding="utf-8") as f:
                self._key = f.read().strip()
        except Exception:
            self._key = ""
        self._lic = lic.check(self._key)
        self._mon = pccheck_monitor.Monitor()

    # ---------- licencia ----------
    @property
    def _vip(self):
        return bool(self._lic.get("ok"))

    def _license_out(self):
        return {"vip": self._vip, "reason": self._lic.get("reason", ""),
                "expires": self._lic.get("expires"), "hwid": lic.get_hwid(), "has_key": bool(self._key)}

    def _save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=1, ensure_ascii=False)
        except Exception:
            pass

    def state(self):
        return {"ok": True, "version": APP_VERSION, "license": self._license_out(),
                "checker": self._settings.get("checker", ""), "league": self._settings.get("league", ""),
                "accent": self._settings.get("accent", "#dc2626"),
                "theme": self._theme(), "themes": list(THEMES), "lang": self._settings.get("lang", "es"),
                "profiles": self._profiles(), "discord": DISCORD_URL, "admin": core.is_admin(),
                "frozen": bool(getattr(sys, "frozen", False))}

    def activate(self, key):
        key = (key or "").strip()
        res = lic.check(key)
        if not res["ok"]:
            msg = {"bad": "Key invalida.", "other_pc": "Esa key es de otra PC.",
                   "expired": "La key vencio el " + str(res.get("expires")),
                   "nokey": "Escribe una key."}.get(res["reason"], "No se pudo activar.")
            return {"ok": False, "error": msg}
        try:
            with open(LICENSE_FILE, "w", encoding="utf-8") as f:
                f.write(key)
        except Exception as e:
            return {"ok": False, "error": "No se pudo guardar: " + str(e)}
        self._key, self._lic = key, res
        return {"ok": True, "license": self._license_out()}

    def remove_license(self):
        try:
            os.remove(LICENSE_FILE)
        except Exception:
            pass
        self._key, self._lic = "", lic.check("")
        return {"ok": True, "license": self._license_out()}

    def _theme(self):
        t = self._settings.get("theme", "clasico")
        return t if (t in FREE_THEMES or (self._vip and t in THEMES)) else "clasico"

    def set_setting(self, key, value):
        if key == "theme":
            if value not in THEMES:
                return {"ok": False, "error": "Tema desconocido."}
            if value not in FREE_THEMES and not self._vip:
                return {"ok": False, "error": "Los temas son VIP."}
            self._settings["theme"] = value
            self._save_settings()
            return {"ok": True, "theme": self._theme()}
        if key == "lang":
            self._settings["lang"] = "en" if value == "en" else "es"
            self._save_settings()
            return {"ok": True, "lang": self._settings["lang"]}
        if key in ("checker", "league", "accent"):
            self._settings[key] = value
            self._save_settings()
        return {"ok": True}

    # ---------- escaneo ----------
    def scan(self):
        try:
            core.LANG = self._settings.get("lang", "es")
            prev = self._res
            res = core.scan()
            if prev:
                try:
                    res["diff"] = core.diff_scans(prev, res)
                    core.finalize(res)
                except Exception:
                    pass
            self._res = res
            return {"ok": True, "res": self._res}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def log(self, i):
        try:
            allowed = {l["path"] for l in (self._res or {}).get("logs", [])}
            p = self._res["logs"][int(i)]["path"]
            return {"ok": True, "text": core.read_log(p, allowed)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def analyze(self, i):
        try:
            import pccheck_logs
            p = self._res["logs"][int(i)]["path"]
            return {"ok": True, "a": pccheck_logs.analyze(p, core.matcher())}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def analyze_file(self):
        try:
            import webview, pccheck_logs
            fd = getattr(webview, "FileDialog", None)
            kind = fd.OPEN if fd else webview.OPEN_DIALOG
            sel = self._window.create_file_dialog(kind, allow_multiple=False,
                                                  file_types=("Logs (*.log;*.txt)", "Todos los archivos (*.*)"))
            if not sel:
                return {"ok": False, "cancel": True}
            p = sel[0] if isinstance(sel, (list, tuple)) else sel
            self._ext = p
            return {"ok": True, "a": pccheck_logs.analyze(p, core.matcher()), "path": p}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def ext_text(self):
        try:
            with open(self._ext, "rb") as f:
                return {"ok": True, "text": f.read().decode("utf-8", errors="replace")}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def copy_text(self, text):
        """Copia texto al portapapeles de Windows (para pegar el resumen en Discord)."""
        try:
            _set_clipboard(str(text or ""))
            return {"ok": True}
        except Exception:
            try:
                subprocess.run(["clip"], input=b"\xff\xfe" + str(text or "").encode("utf-16-le"),
                               creationflags=NO_WINDOW, timeout=10)
                return {"ok": True}
            except Exception as e:
                return {"ok": False, "error": str(e)}

    # ---------- abrir ubicacion de archivos (todos) ----------
    def reveal(self, path):
        """Abre el Explorador con el archivo seleccionado. Solo rutas que el escaneo listo."""
        try:
            allowed = set()
            r = self._res or {}
            for l in r.get("logs", []):
                allowed.add(l["path"])
            for f in r.get("flag_files", []):
                allowed.add(f["path"])
            for f in r.get("flags", []):
                allowed.add(f.get("file"))
            for key in ("hidden", "exe_ids", "recent", "exec", "exec_gone", "autoruns"):
                for x in r.get(key, []):
                    allowed.add(x.get("path"))
            for d in r.get("dirs", []):
                allowed.add(d)
            for e in r.get("exes", []):
                allowed.add(e.get("path"))
            for x in r.get("timeline", []):
                if x.get("src"):
                    allowed.add(x["src"])
            for e in self._mon.all_events():
                if e.get("path"):
                    allowed.add(e["path"])
            if self._ext:
                allowed.add(self._ext)
            if path not in allowed or not os.path.exists(path):
                return {"ok": False, "error": "Ruta no disponible."}
            if os.name == "nt":
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)], creationflags=NO_WINDOW)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_folder(self, which):
        """Abre la carpeta de logs de Roblox o la de reportes."""
        paths = {"roblox_logs": os.path.join(LAD, "Roblox", "logs"),
                 "reportes": os.path.join(core.app_dir(), "reportes"),
                 "datos": DATA_DIR}
        p = paths.get(which)
        if not p:
            return {"ok": False, "error": "?"}
        os.makedirs(p, exist_ok=True)
        if os.name == "nt":
            os.startfile(p)
        return {"ok": True}

    def open_discord(self):
        webbrowser.open(DISCORD_URL)
        return {"ok": True}

    def check_update(self):
        if not UPDATE_URL:
            return {"ok": True, "update": False, "reason": "sin configurar"}
        try:
            req = urllib.request.Request(UPDATE_URL,
                                         headers={"User-Agent": "PCCheckAssist",
                                                  "Accept": "application/vnd.github.raw+json",
                                                  "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8", "replace"))
        except Exception as e:
            return {"ok": False, "error": str(e)[:90]}
        latest = str(data.get("version", "")).strip()
        url = str(data.get("url", "")).strip()
        newer = _ver_gt(latest, APP_VERSION) and url.startswith("https://")
        return {"ok": True, "update": bool(newer), "version": latest, "url": url,
                "notes": str(data.get("notes", "")), "current": APP_VERSION}

    def open_update(self, url):
        u = str(url or "")
        if u.startswith("https://"):
            webbrowser.open(u)
            return {"ok": True}
        return {"ok": False, "error": "URL no valida"}

    def open_rules(self):
        core.load_rules()
        if os.name == "nt":
            os.startfile(core.RULES_FILE)
        return {"ok": True}

    # ---------- perfiles de reglas (VIP) ----------
    def _profiles(self):
        try:
            os.makedirs(PROFILES_DIR, exist_ok=True)
            return sorted(f[:-5] for f in os.listdir(PROFILES_DIR) if f.lower().endswith(".json"))
        except Exception:
            return []

    def save_profile(self, name):
        if not self._vip:
            return {"ok": False, "error": "Los perfiles de reglas son VIP."}
        name = "".join(c for c in (name or "") if c.isalnum() or c in " _-").strip()
        if not name:
            return {"ok": False, "error": "Ponle un nombre al perfil."}
        try:
            os.makedirs(PROFILES_DIR, exist_ok=True)
            rules = core.load_rules()
            with open(os.path.join(PROFILES_DIR, name + ".json"), "w", encoding="utf-8") as f:
                json.dump(rules, f, indent=2, ensure_ascii=False)
            return {"ok": True, "profiles": self._profiles()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def load_profile(self, name):
        if not self._vip:
            return {"ok": False, "error": "Los perfiles de reglas son VIP."}
        try:
            with open(os.path.join(PROFILES_DIR, name + ".json"), encoding="utf-8") as f:
                rules = json.load(f)
            with open(core.RULES_FILE, "w", encoding="utf-8") as f:
                json.dump(rules, f, indent=2, ensure_ascii=False)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------- reglas (editor visual, para todos) ----------
    def get_rules(self):
        r = core.load_rules()
        return {"ok": True, "rules": {k: list(r.get(k, [])) for k in ("exactas", "patrones", "permitidas")},
                "path": core.RULES_FILE}

    def save_rules(self, rules):
        try:
            clean = core.save_rules(rules or {})
            return {"ok": True, "rules": {k: clean[k] for k in ("exactas", "patrones", "permitidas")}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def test_rule(self, name, rules=None):
        name = (name or "").strip()
        if not name:
            return {"ok": True, "match": None}
        try:
            why = core.matcher(rules)(name) if rules else core.matcher()(name)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True, "match": why}

    # ---------- administrador ----------
    def relaunch_admin(self):
        """Vuelve a abrir el programa como administrador (para leer Prefetch y procesos protegidos)."""
        try:
            import ctypes
            if getattr(sys, "frozen", False):
                exe, params = sys.executable, ""
            else:
                exe, params = sys.executable, '"%s"' % os.path.abspath(sys.argv[0])
            r = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
            if int(r) <= 32:
                return {"ok": False, "error": "Windows no dio permiso de administrador."}
            try:
                self._window.destroy()
            except Exception:
                pass
            threading.Timer(0.8, lambda: os._exit(0)).start()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------- monitor en vivo (VIP) ----------
    def monitor_start(self):
        if not self._vip:
            return {"ok": False, "error": "El monitor en vivo es VIP."}
        self._mon.start()
        return {"ok": True}

    def monitor_stop(self):
        self._mon.stop()
        return {"ok": True}

    def monitor_poll(self, since=0):
        try:
            return {"ok": True, **self._mon.poll(int(since or 0))}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------- reporte ----------
    def export(self, opts=None):
        opts = opts or {}
        if not self._res:
            return {"ok": False, "error": "Primero haz una revision."}
        try:
            core.LANG = self._settings.get("lang", "es")
            import pccheck_report as rep
            d = os.path.join(core.app_dir(), "reportes")
            os.makedirs(d, exist_ok=True)
            stamp = time.strftime("%Y%m%d_%H%M%S")
            pdf = os.path.join(d, "pccheck_%s.pdf" % stamp)
            brand = {"vip": self._vip, "checker": self._settings.get("checker", ""),
                     "league": self._settings.get("league", "")}
            extra = {"player": (opts.get("player") or "").strip()[:60],
                     "checklist": opts.get("checklist") or [],
                     "monitor": self._mon.all_events()}
            fp = rep.make_pdf(self._res, pdf, brand=brand, extra=extra)
            data = dict(self._res)
            data["fingerprint"] = fp
            data["player"] = extra["player"]
            data["checklist"] = extra["checklist"]
            data["monitor"] = extra["monitor"]
            data["_meta"] = {"app": "PC Check Assist", "version": APP_VERSION,
                             "extra": ["fingerprint", "player", "checklist", "monitor", "logs_full", "_meta"]}
            data["logs_full"] = []
            for l in data["logs"]:
                try:
                    data["logs_full"].append({"name": l["owner"] + "/" + l["name"],
                                              "text": core.read_log(l["path"], {l["path"]})})
                except Exception:
                    pass
            with open(os.path.join(d, "pccheck_%s.json" % stamp), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=1, ensure_ascii=False)
            if os.name == "nt":
                subprocess.Popen(["explorer", "/select,", pdf], creationflags=NO_WINDOW)
            return {"ok": True, "path": pdf}
        except Exception as e:
            return {"ok": False, "error": str(e)}


def _set_clipboard(text):
    import ctypes
    from ctypes import wintypes
    u32 = ctypes.WinDLL("user32", use_last_error=True)
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    k32.GlobalAlloc.restype = ctypes.c_void_p
    k32.GlobalLock.argtypes = [ctypes.c_void_p]
    k32.GlobalLock.restype = ctypes.c_void_p
    k32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    k32.GlobalFree.argtypes = [ctypes.c_void_p]
    u32.OpenClipboard.argtypes = [ctypes.c_void_p]
    u32.OpenClipboard.restype = wintypes.BOOL
    u32.SetClipboardData.argtypes = [wintypes.UINT, ctypes.c_void_p]
    u32.SetClipboardData.restype = ctypes.c_void_p
    data = text.encode("utf-16-le") + b"\x00\x00"
    for _ in range(10):
        if u32.OpenClipboard(None):
            break
        time.sleep(0.05)
    else:
        raise RuntimeError("El portapapeles está ocupado.")
    try:
        u32.EmptyClipboard()
        h = k32.GlobalAlloc(0x0002, len(data))
        p = k32.GlobalLock(h)
        ctypes.memmove(p, data, len(data))
        k32.GlobalUnlock(h)
        if not u32.SetClipboardData(13, h):
            k32.GlobalFree(h)
            raise RuntimeError("No se pudo copiar.")
    finally:
        u32.CloseClipboard()


def main():
    import webview
    api = Api()
    win = webview.create_window("PC Check Assist by Arroz", resource_path(os.path.join("ui", "index.html")),
                                js_api=api, width=1160, height=760, min_size=(1000, 660),
                                background_color="#0c0609")
    api._window = win
    webview.start()


if __name__ == "__main__":
    main()
