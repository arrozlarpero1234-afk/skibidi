"""Nucleo de PC Check Assist. SOLO LECTURA: no modifica nada del jugador ni de Roblox."""
import calendar, glob, hashlib, json, os, re, subprocess, sys, threading, time, unicodedata

NO_WINDOW = 0x08000000 if os.name == "nt" else 0

# ---------------- i18n ----------------
LANG = "es"
_TR = json.loads('{"carpeta con nombre de strap": "folder named like a strap", "Proceso de strap activo: %s": "Active strap process: %s", "Herramienta de modificación abierta: %s": "Modification tool open: %s", "RobloxPlayerBeta.exe sin firma valida de Roblox (posible parche)": "RobloxPlayerBeta.exe without a valid Roblox signature (possible patch)", "No se pudieron verificar %d firma(s) en esta PC (Windows bloqueo PowerShell). ": "Could not verify %d signature(s) on this PC (Windows blocked PowerShell). ", "No cuenta como prueba.": "Does not count as proof.", "Modulo cargado en Roblox que ya no existe en disco (inyeccion en memoria): ": "Module loaded in Roblox that no longer exists on disk (memory injection): ", "Modulo cargado en Roblox desde carpeta temporal/Descargas (inyeccion): ": "Module loaded in Roblox from a temp/Downloads folder (injection): ", "cargado en Roblox pero el archivo ya no existe": "loaded in Roblox but the file no longer exists", "cargado desde una carpeta temporal/Descargas": "loaded from a temp/Downloads folder", "DLL sin firma cargada en Roblox: ": "Unsigned DLL loaded in Roblox: ", "%d flags ilegales en la config que Roblox carga": "%d illegal flags in the config Roblox loads", "%d flag(s) ilegales en un archivo guardado (Descargas/Escritorio) que NO esta aplicado. ": "%d illegal flag(s) in a saved file (Downloads/Desktop) that is NOT applied. ", "Tener el archivo no es prueba de que lo haya usado.": "Having the file is not proof it was used.", "No se pudo leer el archivo de flags: ": "Could not read the flag file: ", "Archivo de flags modificado hace %d min: %s": "Flag file modified %d min ago: %s", "Carpeta de logs vacia en %s (posible borrado)": "Empty logs folder in %s (possible deletion)", "Carpeta de logs de Roblox vacia (posible borrado): no se puede ver que flags cargo": "Empty Roblox logs folder (possible deletion): cannot see which flags loaded", "El log mas reciente de Roblox tiene %d dias; falta el de las ultimas sesiones": "The most recent Roblox log is %d days old; the last sessions\' logs are missing", "El log %s muestra flags prohibidos cargados al abrir Roblox que ya no estan en los archivos: %s": "Log %s shows banned flags loaded when Roblox opened that are no longer in the files: %s", "El log %s confirma %d flag(s) prohibido(s) cargados al abrir Roblox": "Log %s confirms %d banned flag(s) loaded when Roblox opened", "Flags prohibidos en la config activa": "Banned flags in the active config", "%d flag(s) que tus reglas marcan, en la config que Roblox o el strap carga al abrir.": "%d flag(s) your rules match, in the config Roblox or the strap loads on open.", "Archivo de flags guardado (no aplicado)": "Saved flag file (not applied)", "%d flag(s) en un .json en Descargas/Escritorio. No esta en la config activa; tenerlo no prueba que lo haya usado.": "%d flag(s) in a .json in Downloads/Desktop. Not in the active config; having it is not proof it was used.", "Flags prohibidos que ya no están": "Banned flags that are no longer there", "Los logs de Roblox muestran %s cargado(s) al abrir el juego, pero ya no aparecen en los archivos.": "Roblox logs show %s loaded when the game opened, but they no longer appear in the files.", "Flags prohibidos usados en una sesión": "Banned flags used in a session", "Los logs muestran flags prohibidos aceptados por Roblox.": "The logs show banned flags accepted by Roblox.", "Intento de flags prohibidos": "Attempted banned flags", "Roblox rechazó %d flag(s) prohibidos; no tuvieron efecto.": "Roblox rejected %d banned flag(s); they had no effect.", "Roblox modificado": "Roblox modified", "RobloxPlayerBeta.exe no tiene una firma válida de Roblox.": "RobloxPlayerBeta.exe does not have a valid Roblox signature.", "DLL sin firma dentro de Roblox": "Unsigned DLL inside Roblox", "%d módulo(s) sin firma cargados en el proceso.": "%d unsigned module(s) loaded in the process.", "Strap renombrado": "Renamed strap", "Herramientas de modificación abiertas": "Modification tools open", "Ejecutable de strap fuera de su carpeta": "Strap executable outside its folder", "Hay un strap guardado en Descargas, Escritorio u otra carpeta.": "There is a strap saved in Downloads, Desktop or another folder.", "Strap abierto durante el check": "Strap open during the check", "Roblox lanzado por un strap": "Roblox launched by a strap", "El proceso padre de Roblox es un strap.": "Roblox\'s parent process is a strap.", "Logs de strap borrados": "Strap logs deleted", "Carpeta de logs vacía en: ": "Empty logs folder in: ", "Borró cosas relacionadas en las últimas 24 h": "Deleted related items in the last 24 h", "Hay cosas relacionadas en la papelera": "Related items in the recycle bin", "Archivo de flags modificado hace menos de 1 h": "Flag file modified less than 1 h ago", "Alguien tocó los flags justo antes del check.": "Someone touched the flags right before the check.", "Roblox se abrió justo antes del check": "Roblox opened right before the check", "Roblox lleva abierto solo %d min (se abrio justo antes del check)": "Roblox has been open only %d min (opened right before the check)", "Strap ejecutado en las últimas 24 h": "Strap executed in the last 24 h", "Según el historial de ejecución de Windows.": "According to Windows execution history.", "Strap o inyector ejecutado y luego borrado": "Strap or injector executed and then deleted", "Windows registra que se abrió %s, pero el archivo ya no está.": "Windows records that %s was opened, but the file is no longer there.", "Herramienta de modificación usada en las últimas 24 h": "Modification tool used in the last 24 h", "Programa ejecutado justo antes del check y borrado": "Program executed right before the check and deleted", "%s se abrió en la última hora y ya no existe.": "%s opened in the last hour and no longer exists.", "Strap o herramienta configurado para abrirse con Windows": "Strap or tool set to open with Windows", "Borró o cambió cosas durante el check": "Deleted or changed things during the check", "Entre una revisión y otra: ": "Between one review and the next: ", "Exclusión del antivirus para un strap o inyector": "Antivirus exclusion for a strap or injector", "Ejecutado desde USB o disco externo": "Executed from USB or external drive", "Correr el strap desde otra unidad evita dejar rastro en C:. Ruta: ": "Running the strap from another drive avoids leaving a trace on C:. Path: ", "Strap o flags en una unidad extraible conectada": "Strap or flags on a connected removable drive", "La PC se conecto a un dominio de strap o inyector": "The PC connected to a strap or injector domain", "Logs de Roblox borrados": "Roblox logs deleted", "No hay ningun log; no se puede ver que flags cargo al abrir.": "There are no logs; cannot see which flags loaded on open.", "Inyeccion en memoria en Roblox": "Memory injection in Roblox", "%d modulo(s) metidos en Roblox desde una ruta temporal o ya borrada: %s": "%d module(s) injected into Roblox from a temp or already-deleted path: %s", "Ejecucion en memoria (fileless)": "In-memory execution (fileless)", "PowerShell bajo y ejecuto algo sin dejar archivo: ": "PowerShell downloaded and ran something without leaving a file: ", "Fechas falsas (timestomp)": "Fake dates (timestomp)", "%d archivo(s) con fecha manipulada: %s": "%d file(s) with a manipulated date: %s", "Proceso disfrazado de sistema": "Process disguised as a system process", "%s corriendo fuera de Windows: %s": "%s running outside Windows: %s", "Microsoft Defender desactivado": "Microsoft Defender disabled", "Datos ocultos en flujos alternos (ADS)": "Hidden data in alternate streams (ADS)", "%d archivo(s) con algo escondido dentro: %s": "%d file(s) with something hidden inside: %s", "Inyector de flags en el disco": "Flag injector on disk", "Strap instalado": "Strap installed", "Tener un strap instalado no es trampa por sí solo: ": "Having a strap installed is not cheating by itself: ", "Windows (PCA) registra que se abrio %s el %s y ya no existe o es inyector": "Windows (PCA) records that %s was opened on %s and no longer exists or is an injector", "El disco registra actividad de %s (%s) %s": "The disk records activity of %s (%s) %s", "Alguien borro el Visor de eventos de Windows (%s)": "Someone cleared the Windows Event Viewer (%s)", "Se cambio la hora del sistema %d vez/veces en 30 dias": "The system clock was changed %d time(s) in 30 days", "Prefetch de Windows desactivado (no es normal; borra rastro de ejecucion)": "Windows Prefetch disabled (not normal; erases execution traces)", "El diario del disco (USN) se reinicio hace %.1f dias": "The disk journal (USN) was reset %.1f days ago", "Se ejecuto desde la unidad %s (USB/externa, no C:): %s": "Executed from drive %s (USB/external, not C:): %s", "Strap/inyector o archivo de flags en una unidad extraible conectada: ": "Strap/injector or flag file on a connected removable drive: ", "La PC se conecto a un dominio de strap/inyector: ": "The PC connected to a strap/injector domain: ", "Rastro de ejecucion en memoria (PowerShell): ": "In-memory execution trace (PowerShell): ", "Microsoft Defender ": "Microsoft Defender ", " (no es prueba de trampa; mucha gente lo apaga)": " (not proof of cheating; many people disable it)", "proteccion en tiempo real APAGADA": "real-time protection OFF", "proteccion contra manipulacion APAGADA": "tamper protection OFF", "monitoreo de comportamiento APAGADO": "behavior monitoring OFF", "antivirus APAGADO": "antivirus OFF", "Dato oculto en flujo alterno (ADS): %s en %s": "Hidden data in alternate stream (ADS): %s in %s", "Inyector detectado por %s: %s": "Injector detected by %s: %s", "hash conocido de ": "known hash of ", "huella interna: \'%s\'": "internal signature: \'%s\'", "Fecha falsa (%s) en %s": "Fake date (%s) in %s", "modificado antes de ser creado": "modified before it was created", "fecha en el futuro": "date in the future", "segundos exactos en cero (marca de timestomp)": "exact zero seconds (timestomp mark)", "Señales de limpieza anti-revisión": "Anti-review cleanup signs", "Prefetch desactivado": "Prefetch disabled", "Hora del sistema cambiada": "System clock changed", "Diario USN reiniciado hace poco": "USN journal reset recently", "Historial de Windows (UserAssist) apagado": "Windows history (UserAssist) off", "Un jugador normal no borra el Visor de eventos.": "A normal player does not clear the Event Viewer.", "Se abrió Roblox": "Roblox opened", "Se cerró Roblox": "Roblox closed", "Se reinició Roblox": "Roblox restarted", "Roblox se reinició": "Roblox restarted", "Se abrió %s": "%s opened", "Se abrió %s (sigue activo)": "%s opened (still active)", "Se cerró %s": "%s closed", "Entró a una partida (place %s)": "Joined a game (place %s)", "Roblox cargó %d flags locales (ninguno prohibido)": "Roblox loaded %d local flags (none banned)", "Roblox cargó %d flags locales, %d prohibidos: %s": "Roblox loaded %d local flags, %d banned: %s", "Se instaló ": "Installed ", "Se modificó un archivo de flags de %s (%d flags)": "A flag file was modified for %s (%d flags)", "Se modificó el archivo de flags de %s": "The flag file for %s was modified", "Se mandó a la papelera: %s": "Sent to the recycle bin: %s", "Se borró el log %s (%s)": "Deleted log %s (%s)", "Se borró %s (%s)": "Deleted %s (%s)", "Se borró o desinstaló la carpeta %s": "Deleted or uninstalled the folder %s", "Se ejecutó %s (ya no existe)": "Ran %s (no longer exists)", "Se ejecutó %s el %s (historial de Windows)": "Ran %s on %s (Windows history)", "Se ejecutó %s hace %d min y ya no existe": "Ran %s %d min ago and no longer exists", "Inicio de esta revisión": "Start of this review", "Última actividad del log de Roblox": "Last activity in the Roblox log", "Roblox fue lanzado por un strap: %s": "Roblox was launched by a strap: %s", "Strap instalado: %s (%s)": "Strap installed: %s (%s)", "Roblox abierto ahora (lanzado por explorer)": "Roblox open now (launched by explorer)", "hora previa al check": "hour before the check", "bajo": "low", "medio": "medium", "alto": "high", "limpio": "clean", "dudoso": "doubtful", "sospechoso": "suspicious", "Windows registra que se abrio un strap o herramienta": "Windows records that a strap or tool was opened", "ejecutable de strap": "strap executable", "ejecutable de %s": "%s executable", "instalador de %s": "%s installer", "%s renombrado": "%s renamed", " (ya se ejecutó el %s)": " (already ran on %s)", "%s: %s": "%s: %s", "lista exacta": "exact match", "ejecutable": "executable", "Roblox abierto ahora (lanzado por %s)": "Roblox open now (launched by %s)", "Roblox abierto ahora (el programa que lo abrió ya se cerró)": "Roblox open now (the program that launched it has already closed)", "Actividad de %s (log %s)": "Activity from %s (log %s)", "Apareció: %s (%s)": "Appeared: %s (%s)", "Apareció %s — %s": "Appeared %s — %s", "%d archivo(s) clave modificados en las ultimas %d h (ver Actividad)": "%d key file(s) modified in the last %d h (see Activity)", "%d elemento(s) relacionados en la papelera (ver Actividad)": "%d related item(s) in the recycle bin (see Activity)", "Apareció el flag prohibido %s (%s)": "The banned flag %s appeared (%s)", "Apareció un archivo de flags de %s (%d flags)": "A flag file for %s appeared (%d flags)", "Apareció la carpeta %s": "The folder %s appeared", "Apareció %s": "%s appeared", "%d flag(s) ilegales en un archivo guardado (Descargas/Escritorio) que NO esta aplicado. Tener el archivo no es prueba de que lo haya usado.": "%d illegal flag(s) in a saved file (Downloads/Desktop) that is NOT applied. Having the file is not proof it was used."}')
def _T(s):
    return _TR.get(s, s) if LANG == "en" else s


if os.name == "nt":
    # Sin popups de "La aplicacion no se pudo iniciar correctamente" en procesos hijos (se hereda).
    try:
        import ctypes
        ctypes.windll.kernel32.SetErrorMode(0x0001 | 0x0002 | 0x8000)
    except Exception:
        pass
LAD = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
STRAP_FOLDERS = ("Bloxstrap", "Fishstrap", "Voidstrap", "Froststrap", "Noozystrap", "NoozyStrap", "Arroztrap")
STRAP_NAMES = ["ez4strap", "bloxstrap", "fishstrap", "voidstrap", "froststrap", "lunastrap",
               "noozystrap", "arroztrap", "bloxshade", "rdd", "rcd"]
STRAP_RX = re.compile(r"(?i)(bloxstrap|fishstrap|voidstrap|froststrap|noozystrap|arroztrap|lunastrap|ez4strap|ez4\s?strap)")
# Bootstrappers legitimos que usa mucha gente limpia: no suman riesgo por si solos.
LEGIT_STRAPS = ("bloxstrap", "fishstrap")
def _is_legit(path):
    low = (path or "").lower()
    return any(s in low for s in LEGIT_STRAPS) and "ez4" not in low
TOOL_NAMES = ["cheatengine", "cheat engine", "processhacker", "systeminformer", "x64dbg", "x32dbg",
              "ollydbg", "extreme injector", "extremeinjector", "xenos"]
ROBLOX_PROCS = ("robloxplayerbeta", "windows10universal")

DEFAULT_RULES = {
    "_nota": "Edita segun el reglamento de tu liga. 'exactas' = nombre completo del flag; 'patrones' = regex sobre el nombre; 'permitidas' = flags que nunca se marcan. Los ejemplos son un punto de partida, no un reglamento oficial.",
    "exactas": ["DFIntS2PhysicsSenderRate", "DFIntMaxMissedWorldStepsRemembered",
                "FIntInterpolationMaxDelayMSec", "DFIntTouchSenderMaxBandwidthBps"],
    "patrones": [r"(?i)physicssender", r"(?i)ReplicatorRate", r"(?i)Humanoid.*(Speed|Jump)",
                 r"(?i)Hitbox", r"(?i)AntiCheat|Byfron|Hyperion"],
    "permitidas": [],
}


def app_dir():
    return os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))


def bundle_dir():
    """Carpeta de recursos empaquetados (PyInstaller) o la del script."""
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


# El archivo editable vive junto al .exe; la copia embebida es solo la semilla
# inicial (el bundle de PyInstaller es temporal y no se puede escribir).
RULES_FILE = os.path.join(app_dir(), "flags_ilegales.json")
RULES_SEED = os.path.join(bundle_dir(), "flags_ilegales.json")


# ---------------------------------------------------------------- utilidades
_PS_EXE = None
_PS_SEM = threading.Semaphore(2)  # hasta 2 PowerShell a la vez (el crash 0xc0000142 venia de 3+)
_PS_FAIL_CODES = {0xC0000142, -1073741502, 0xC0000135, -1073741515}


def _ps_exe():
    global _PS_EXE
    if _PS_EXE is None:
        root = os.environ.get("SystemRoot") or os.environ.get("WINDIR") or r"C:\Windows"
        full = os.path.join(root, "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
        _PS_EXE = full if os.path.isfile(full) else "powershell"
    return _PS_EXE


def _run_ps(args, stdin=None, timeout=60):
    """Una PowerShell a la vez y reintento si Windows no la deja arrancar (0xc0000142)."""
    cmd = [_ps_exe(), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass"] + args
    for intento in range(3):
        try:
            with _PS_SEM:
                r = subprocess.run(cmd, input=stdin, capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", timeout=timeout, creationflags=NO_WINDOW)
            if r.returncode in _PS_FAIL_CODES:
                raise OSError("powershell no inicio (%#x)" % (r.returncode & 0xFFFFFFFF))
            return r.stdout.strip()
        except subprocess.TimeoutExpired:
            return ""
        except Exception:
            time.sleep(0.6 * (intento + 1))
    return ""


def ps(cmd, timeout=60):
    return _run_ps(["-Command", "[Console]::OutputEncoding=[Text.Encoding]::UTF8;" + cmd], timeout=timeout)


def ps_stdin(script, timeout=90):
    """Ejecuta un script largo por stdin (sin limite de longitud de linea de comandos, sin escribir archivos)."""
    return _run_ps(["-Command", "-"], stdin="[Console]::OutputEncoding=[Text.Encoding]::UTF8\n" + script + "\n",
                   timeout=timeout)


def _json(out):
    try:
        data = json.loads(out) if out else []
    except ValueError:
        return []
    return [data] if isinstance(data, dict) else data


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fmt(ep, f="%Y-%m-%d %H:%M"):
    return time.strftime(f, time.localtime(ep)) if ep else ""


def _home():
    return os.path.expanduser("~")


_UD = None


def user_dirs():
    """Rutas reales de Escritorio, Documentos y Descargas (respeta OneDrive)."""
    global _UD
    if _UD is not None:
        return _UD
    home = _home()
    d = {"Desktop": os.path.join(home, "Desktop"), "Documents": os.path.join(home, "Documents"),
         "Downloads": os.path.join(home, "Downloads")}
    out = ps("[Environment]::GetFolderPath('Desktop');[Environment]::GetFolderPath('MyDocuments');(New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path", 20)
    parts = [x.strip() for x in out.splitlines() if x.strip()]
    for k, v in zip(("Desktop", "Documents", "Downloads"), parts):
        if os.path.isdir(v):
            d[k] = v
    _UD = d
    return d


def load_rules():
    if not os.path.isfile(RULES_FILE):
        seed = None
        if os.path.isfile(RULES_SEED) and os.path.abspath(RULES_SEED) != os.path.abspath(RULES_FILE):
            try:
                with open(RULES_SEED, encoding="utf-8") as f:
                    seed = json.load(f)
            except Exception:
                seed = None
        if not isinstance(seed, dict):
            seed = dict(DEFAULT_RULES)
        try:
            with open(RULES_FILE, "w", encoding="utf-8") as f:
                json.dump(seed, f, indent=2, ensure_ascii=False)
        except OSError:
            return seed
    try:
        with open(RULES_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return dict(DEFAULT_RULES)


def save_rules(rules):
    clean = {"_nota": DEFAULT_RULES["_nota"]}
    for k in ("exactas", "patrones", "permitidas"):
        vals = []
        for v in rules.get(k, []) or []:
            v = str(v).strip()
            if v and v not in vals:
                vals.append(v)
        clean[k] = vals
    bad = []
    for p in clean["patrones"]:
        try:
            re.compile(p)
        except re.error as e:
            bad.append("%s (%s)" % (p, e))
    if bad:
        raise ValueError("Patrones invalidos: " + "; ".join(bad))
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)
    return clean


def matcher(rules=None):
    rules = rules or load_rules()
    exact, ok = set(rules.get("exactas", [])), set(rules.get("permitidas", []))
    pats = []
    for p in rules.get("patrones", []):
        try:
            pats.append(re.compile(p))
        except re.error:
            pass

    def why(name):
        if name in ok:
            return None
        return _T("lista exacta") if name in exact else next((p.pattern for p in pats if p.search(name)), None)
    return why


# ---------------------------------------------------------------- recolectores
def _procs():
    out = ps("Get-Process | Select-Object Name,Id,Path,@{n='st';e={try{$_.StartTime.ToString('yyyy-MM-ddTHH:mm:ss')}catch{$null}}} | ConvertTo-Json -Compress")
    data = _json(out)
    for p in data:
        try:
            p["ep"] = time.mktime(time.strptime(p.get("st") or "", "%Y-%m-%dT%H:%M:%S"))
        except Exception:
            p["ep"] = None
    return data


def _sigs(paths):
    """Firma de varios archivos en UNA sola PowerShell. {ruta: (estado, firmante)}; estado '' = no se pudo verificar."""
    paths = [p for p in dict.fromkeys(paths) if p]
    if not paths:
        return {}
    lista = ",".join("'%s'" % p.replace("'", "''") for p in paths)
    out = ps_stdin("foreach($f in @(%s)){ try{ $s=Get-AuthenticodeSignature -LiteralPath $f -ErrorAction Stop; $f + '|' + $s.Status.ToString() + '|' + $s.SignerCertificate.Subject }catch{ $f + '||' } }" % lista,
                   timeout=120)
    res = {p: ("", "") for p in paths}
    low = {os.path.normcase(p): p for p in paths}
    for line in out.splitlines():
        f, _, rest = line.partition("|")
        st, _, subj = rest.partition("|")
        k = low.get(os.path.normcase(f.strip()))
        if k:
            res[k] = (st.strip(), subj.strip())
    return res


def _sig(path):
    st, subj = _sigs([path]).get(path, ("", ""))
    return "%s|%s" % (st or "desconocido", subj)


def _flag_files():
    pats = [os.path.join(LAD, "Roblox", "Versions", "*", "ClientSettings", "ClientAppSettings.json"),
            os.path.join(LAD, "Roblox", "ClientSettings", "ClientAppSettings.json")]
    for s in STRAP_FOLDERS:
        pats += [os.path.join(LAD, s, "Modifications", "ClientSettings", "ClientAppSettings.json"),
                 os.path.join(LAD, s, "Versions", "*", "ClientSettings", "ClientAppSettings.json"),
                 os.path.join(LAD, s, "ClientSettings", "ClientAppSettings.json"),
                 os.path.join(LAD, s, "user_flags.json"), os.path.join(LAD, s, "flags.json")]
    out = []
    for p in pats:
        out += glob.glob(p)
    return sorted(set(os.path.normcase(x) for x in out))


def _owner(path):
    low = path.lower()
    for s in STRAP_FOLDERS:
        if os.sep + s.lower() + os.sep in low:
            return s.capitalize()
    return "Roblox" if "roblox" in low else "Otros"


STRAP_EXES = {n + ".exe" for n in ("bloxstrap", "fishstrap", "voidstrap", "froststrap", "noozystrap", "arroztrap", "lunastrap")}
SKIP_DIRS = {"node_modules", "windows", "$recycle.bin", "__pycache__", ".git", "cache", "code cache",
             "gpucache", "program files", "program files (x86)", "microsoft", "packages", "temp", "site-packages"}
RECENT_HOURS = 6
FLAG_KEY = re.compile(r"^(DF|F|SF)(Flag|Int|String|Log)[A-Za-z0-9_]+$")
SECRET_ARG = re.compile(r"(?i)(-t|--authenticationticket|--ticket)\s+\S+")


def _walk(root, maxdepth, deadline):
    stack = [(root, 0)]
    while stack:
        if time.time() > deadline:
            return
        d, depth = stack.pop()
        try:
            items = list(os.scandir(d))
        except OSError:
            continue
        yield d, items
        if depth < maxdepth:
            for e in items:
                try:
                    if e.is_dir(follow_symlinks=False) and e.name.lower() not in SKIP_DIRS:
                        stack.append((e.path, depth + 1))
                except OSError:
                    pass


def _extract_flags(data, strict):
    """Devuelve {nombre: valor}. strict=True solo acepta claves con forma de FFlag."""
    out = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if not strict or FLAG_KEY.match(str(k)):
                out[str(k)] = v
    elif isinstance(data, list):
        for it in data:
            if isinstance(it, dict) and "name" in it and (not strict or FLAG_KEY.match(str(it["name"]))):
                out[str(it["name"])] = it.get("value")
    return out


def _generic_flag_files(known, deadline):
    """Busca .json con flags en carpetas de straps y en Escritorio/Descargas/Documentos."""
    ud, found = user_dirs(), []
    roots = [(os.path.join(LAD, s), 4) for s in STRAP_FOLDERS] + \
            [(ud["Desktop"], 2), (ud["Downloads"], 2), (ud["Documents"], 2)] + \
            [(os.path.join(os.environ.get("APPDATA", ""), s), 3) for s in STRAP_FOLDERS]
    for root, depth in roots:
        if not os.path.isdir(root):
            continue
        for d, items in _walk(root, depth, deadline):
            for e in items:
                n = e.name.lower()
                if not n.endswith(".json") or os.path.normcase(e.path) in known:
                    continue
                try:
                    if e.stat().st_size > 5 * 1024 * 1024:
                        continue
                    with open(e.path, encoding="utf-8-sig") as fh:
                        data = json.load(fh)
                except Exception:
                    continue
                if _extract_flags(data, True):
                    found.append(os.path.normcase(e.path))
    return sorted(set(found))


def _roblox_procs():
    out = ps('Get-CimInstance Win32_Process -Filter "Name=\'RobloxPlayerBeta.exe\'" | ForEach-Object { [pscustomobject]@{pid=$_.ProcessId;ppid=$_.ParentProcessId;cmd=$_.CommandLine;start=$_.CreationDate.ToString(\'yyyy-MM-dd HH:mm:ss\');parent=(Get-Process -Id $_.ParentProcessId -ErrorAction SilentlyContinue).ProcessName} } | ConvertTo-Json -Compress')
    data = _json(out)
    for d in data:
        d["cmd"] = SECRET_ARG.sub(lambda m: m.group(1) + " ***", d.get("cmd") or "")
        try:
            d["ep"] = time.mktime(time.strptime(d["start"], "%Y-%m-%d %H:%M:%S"))
            d["up_min"] = int((time.time() - d["ep"]) / 60)
        except Exception:
            d["ep"], d["up_min"] = None, None
    return data


def _recent_changes(deadline):
    cutoff = time.time() - RECENT_HOURS * 3600
    roots = [os.path.join(LAD, "Roblox")] + [os.path.join(LAD, s) for s in STRAP_FOLDERS]
    skip = ("\\roblox\\logs", "\\roblox\\downloads", "\\roblox\\rbxcsettings", "\\content\\", "\\cache",
            "\\roblox\\localstorage")
    out, seen = [], set()
    for root in roots:
        if not os.path.isdir(root):
            continue
        for d, items in _walk(root, 5, deadline):
            low = d.lower()
            if any(s in low for s in skip):
                continue
            for e in items:
                try:
                    if e.is_file(follow_symlinks=False):
                        mt = e.stat().st_mtime
                        if mt >= cutoff and e.path not in seen:
                            seen.add(e.path)
                            out.append({"path": e.path, "mtime": fmt(mt), "ts": mt,
                                        "kb": max(1, e.stat().st_size // 1024)})
                except OSError:
                    pass
    out.sort(key=lambda x: -x["ts"])
    return out[:300]


def install_dirs():
    """Carpetas donde un strap se instala normalmente: LOCALAPPDATA/<Strap> y LOCALAPPDATA/Programs/<carpeta con nombre de strap>."""
    out = [os.path.join(LAD, s) for s in STRAP_FOLDERS if os.path.isdir(os.path.join(LAD, s))]
    prog = os.path.join(LAD, "Programs")
    try:
        for e in os.scandir(prog):
            if e.is_dir(follow_symlinks=False) and STRAP_RX.search(e.name):
                out.append(e.path)
    except OSError:
        pass
    seen, res = set(), []
    for d in out:
        k = os.path.normcase(d)
        if k not in seen:
            seen.add(k)
            res.append(d)
    return res


def _hidden_straps(deadline):
    ud, home, hits = user_dirs(), _home(), []
    standard = {os.path.normcase(os.path.join(LAD, s)) for s in STRAP_FOLDERS} | {os.path.normcase(d) for d in install_dirs()}
    roots = [(LAD, 3), (os.environ.get("APPDATA", ""), 3), (ud["Desktop"], 3),
             (ud["Downloads"], 3), (ud["Documents"], 3), (home, 1)]
    seen = set()
    for root, depth in roots:
        if not root or not os.path.isdir(root):
            continue
        for d, items in _walk(root, depth, deadline):
            nd = os.path.normcase(d)
            if nd in seen:
                continue
            seen.add(nd)
            files = {}
            for e in items:
                try:
                    if not e.is_dir(follow_symlinks=False):
                        files[e.name.lower()] = e
                except OSError:
                    pass
            inside_std = any(nd == s or nd.startswith(s + os.sep) for s in standard)
            for fn in files:
                if fn in STRAP_EXES and not inside_std:
                    p = os.path.join(d, fn)
                    hits.append({"path": p, "why": _T("ejecutable de strap"), "lvl": "high", "ep": _ctime(p)})
            if "clientappsettings.json" in files and "\\roblox\\versions\\" not in nd and not inside_std \
                    and "\\modifications\\clientsettings" not in nd and "\\roblox\\clientsettings" not in nd:
                p = os.path.join(d, "ClientAppSettings.json")
                hits.append({"path": p, "why": "ClientAppSettings.json fuera de lugar", "lvl": "mid", "ep": _mtime(p)})
            base = os.path.basename(d).lower()
            if not inside_std and any(s in base for s in STRAP_NAMES if len(s) > 3) and nd not in standard:
                hits.append({"path": d, "why": _T("carpeta con nombre de strap"), "lvl": "mid", "ep": _ctime(d)})
    uniq = {h["path"]: h for h in hits}
    return list(uniq.values())[:100]


def _ctime(p):
    try:
        return os.path.getctime(p)
    except OSError:
        return None


def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return None


def _exe_candidates(deadline, limit=600):
    ud, home = user_dirs(), _home()
    roots = [(ud["Downloads"], 3), (ud["Desktop"], 3), (ud["Documents"], 2),
             (os.path.join(LAD, "Programs"), 2), (os.environ.get("APPDATA", ""), 2), (LAD, 1), (home, 1)]
    out, seen = [], set()
    for root, depth in roots:
        if not root or not os.path.isdir(root):
            continue
        for d, items in _walk(root, depth, deadline):
            for e in items:
                try:
                    if e.name.lower().endswith(".exe") and e.is_file(follow_symlinks=False) \
                            and e.stat().st_size < 250 * 1024 * 1024:
                        k = os.path.normcase(e.path)
                        if k not in seen:
                            seen.add(k)
                            out.append(e.path)
                except OSError:
                    pass
            if len(out) >= limit:
                return out
    return out


def _exe_identity(paths):
    """Lee la informacion de version (nombre de producto, nombre original...) de cada .exe."""
    res = []
    for i in range(0, len(paths), 150):
        chunk = paths[i:i + 150]
        arr = ",".join("'" + p.replace("'", "''") + "'" for p in chunk)
        script = ('$r=@();foreach($p in @(%s)){try{$v=[System.Diagnostics.FileVersionInfo]::GetVersionInfo($p);$r+=[pscustomobject]@{p=$p;o=$v.OriginalFilename;n=$v.ProductName;d=$v.FileDescription;c=$v.CompanyName;i=$v.InternalName}}catch{}};$r|ConvertTo-Json -Compress' % arr)
        res += _json(ps_stdin(script))
    return res


def _classify_exes(infos, hidden_paths):
    hits = []
    standard = {os.path.normcase(os.path.join(LAD, s)) for s in STRAP_FOLDERS} | {os.path.normcase(d) for d in install_dirs()}
    for x in infos:
        p = x.get("p") or ""
        blob = " ".join(str(x.get(k) or "") for k in ("o", "n", "d", "c", "i"))
        m = STRAP_RX.search(blob)
        if not m:
            continue
        strap = m.group(1).lower()
        fn = os.path.basename(p).lower()
        parent = os.path.basename(os.path.dirname(p)).lower()
        np_ = os.path.normcase(p)
        inside_std = any(np_.startswith(s + os.sep) for s in standard)
        installer = re.search(r"(?i)setup|uninstall|instal|unins\d", (x.get("d") or "") + " " + fn)
        named = strap in fn or strap in parent
        product = (x.get("n") or x.get("d") or strap).strip()
        if installer:
            if strap in parent or inside_std:
                continue  # desinstalador de un strap ya instalado: no aporta
            kind, lvl, why = "instalador", "mid", _T("instalador de %s") % strap.capitalize()
        elif named:
            if inside_std or np_ in hidden_paths or strap in parent:
                continue  # ya cubierto por carpetas/ejecutables con nombre
            kind, lvl, why = _T("ejecutable"), "mid", _T("ejecutable de %s") % strap.capitalize()
        else:
            kind, lvl, why = "renombrado", "high", _T("%s renombrado") % strap.capitalize()
        hits.append({"path": p, "strap": strap.capitalize(), "kind": kind, "lvl": lvl, "why": why,
                     "product": product, "ep": _ctime(p)})
    return hits


def _recycle():
    out = ps("$s=New-Object -ComObject Shell.Application;$b=$s.Namespace(10);$b.Items()|ForEach-Object{$dd=$null;try{$dd=$_.ExtendedProperty('System.Recycle.DateDeleted').ToString('yyyy-MM-ddTHH:mm:ss')}catch{};[pscustomobject]@{n=$_.Name;o=$b.GetDetailsOf($_,1);d=$b.GetDetailsOf($_,2);u=$dd}}|ConvertTo-Json -Compress", 40)
    data = _json(out)
    pat = re.compile(r"(?i)strap|clientappsettings|flags|fflag|injector|inyector|\.log$|rdd|rcd")
    skip_rec = re.compile(r"(?i)medal|obs|shadowplay|nvidia|geforce|outplayed|streamlabs|screenrec|bandicam")
    clean = lambda s: "".join(ch for ch in (s or "") if unicodedata.category(ch) not in ("Cf", "Cc")).strip()
    hits = []
    for x in data:
        _blob = (x.get("n") or "") + " " + (x.get("o") or "")
        if not pat.search(_blob) or skip_rec.search(_blob):
            continue
        ep = None
        try:  # DateDeleted viene en UTC
            ep = calendar.timegm(time.strptime(x.get("u") or "", "%Y-%m-%dT%H:%M:%S"))
        except Exception:
            pass
        hits.append({"name": clean(x.get("n")), "from": clean(x.get("o")),
                     "date": fmt(ep) if ep else clean(x.get("d")), "ep": ep,
                     "strap": bool(STRAP_RX.search(x.get("n") or ""))})
    hits.sort(key=lambda h: -(h["ep"] or 0))
    return len(data), hits[:100]


def _prefetch():
    out = []
    d = os.path.expandvars(r"%SystemRoot%\Prefetch")
    try:
        for fn in os.listdir(d):
            low = fn.lower()
            if low.endswith(".pf") and any(low.startswith(e) for e in STRAP_EXES):
                mt = os.path.getmtime(os.path.join(d, fn))
                out.append({"name": fn.split("-")[0], "last": fmt(mt), "ts": mt})
    except OSError:
        return None
    return out


def is_admin():
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _merge_sessions(sess):
    """Roblox escribe dos logs por cada apertura (con segundos de diferencia). Los une en una sesion."""
    out = []
    for s in sorted([x for x in sess if x.get("first_ep")], key=lambda x: x["first_ep"]):
        if out and abs(s["first_ep"] - out[-1]["first_ep"]) < 180:
            m = out[-1]
            m["last_ep"] = max(m.get("last_ep") or 0, s.get("last_ep") or 0)
            seen = {(g.get("ep"), g.get("place")) for g in m["games"]}
            m["games"] += [g for g in s["games"] if (g.get("ep"), g.get("place")) not in seen]
            if (s.get("local_flags") or 0) > (m.get("local_flags") or 0):
                m["local_flags"], m["local_ep"], m["illegal"] = s["local_flags"], s["local_ep"], s["illegal"]
        else:
            out.append(dict(s, games=list(s.get("games", []))))
    return out


# ---------------------------------------------------------------- linea de tiempo
def build_timeline(res):
    ev = []
    now = res["now_ep"]

    def add(ep, kind, text, lvl="info", src=""):
        if ep and now - 14 * 86400 <= ep <= now + 60:
            ev.append({"ep": ep, "when": fmt(ep), "kind": kind, "text": text, "lvl": lvl, "src": src,
                       "pre": now - 3600 <= ep <= now})

    for s in res.get("sessions", []):
        add(s.get("first_ep"), "roblox", _T("Se abrió Roblox"), "info", s["log"])
        if s.get("local_flags"):
            acc = [x["name"] for x in s.get("illegal", []) if x["accepted"]]
            if acc:
                add(s.get("local_ep"), "flags", _T("Roblox cargó %d flags locales, %d prohibidos: %s")
                    % (s["local_flags"], len(acc), ", ".join(acc[:4])), "high", s["log"])
            else:
                add(s.get("local_ep"), "flags", _T("Roblox cargó %d flags locales (ninguno prohibido)") % s["local_flags"],
                    "info", s["log"])
        for g in s.get("games", [])[:20]:
            add(g.get("ep"), "game", _T("Entró a una partida (place %s)") % g["place"], "info", s["log"])
        if s.get("last_ep") and s.get("first_ep") and s["last_ep"] - s["first_ep"] > 120:
            add(s.get("last_ep"), "roblox", _T("Última actividad del log de Roblox"), "low", s["log"])
    for r in res.get("roblox_procs", []):
        par = r.get("parent") or ""
        txt = (_T("Roblox abierto ahora (lanzado por %s)") % par) if par else _T("Roblox abierto ahora (el programa que lo abrió ya se cerró)")
        add(r.get("ep"), "roblox", txt, "mid" if STRAP_RX.search(par) else "info")
    bad_files = {f["file"] for f in res.get("flags", [])}
    for f in res.get("flag_files", []):
        add(f.get("ep"), "file", _T("Se modificó un archivo de flags de %s (%d flags)") % (f["owner"], f["count"]),
            "mid" if f["path"] in bad_files else "info", f["path"])
    for r in res.get("recent", []):
        if re.search(r"(?i)\.(exe|dll)$", r["path"]):
            add(r["ts"], "file", "Cambió " + os.path.basename(r["path"]), "low", r["path"])
    for x in res.get("recycle", []):
        add(x.get("ep"), "trash", _T("Se mandó a la papelera: %s") % x["name"], "high" if x.get("strap") else "mid", x["from"])
    for p in res.get("prefetch", []):
        add(p.get("ts"), "run", "Se ejecutó " + p["name"], "mid")
    for x in res.get("exec", []):
        add(x.get("ep"), "run", "Se ejecutó %s%s" % (x["name"], "" if x.get("exists") else " (ya no existe)"),
            x.get("lvl", "low"), x["path"])
    for x in res.get("exec_gone", []):
        add(x.get("ep"), "run", _T("Se ejecutó %s (ya no existe)") % x["name"], x.get("lvl", "low"), x["path"])
    for d in res.get("dir_info", []):
        add(d.get("ep"), "install", _T("Se instaló ") + d["name"], "info", d["path"])
    for l in res.get("logs", []):
        if l["owner"] != "Roblox":
            add(l.get("ep"), "strap", _T("Actividad de %s (log %s)") % (l["owner"], l["name"]), "low", l["path"])
    for p in res.get("procs", []):
        add(p.get("ep"), "run", _T("Se abrió %s (sigue activo)") % p["name"], "mid")
    for h in res.get("hidden", []):
        add(h.get("ep"), "strap", _T("Apareció: %s (%s)") % (os.path.basename(h["path"]), h["why"]), h["lvl"], h["path"])
    for x in res.get("exe_ids", []):
        add(x.get("ep"), "strap", _T("Apareció %s — %s") % (os.path.basename(x["path"]), x["why"]), x["lvl"], x["path"])
    add(now, "check", _T("Inicio de esta revisión"), "check")
    ev.sort(key=lambda e: e["ep"])
    return ev[-400:]


# ---------------------------------------------------------------- puntuacion de riesgo
def risk(res):
    f = []

    def add(pts, title, detail):
        f.append({"pts": pts, "title": title, "detail": detail})

    now = res["now_ep"]
    cur = res.get("flags", [])
    cur_names = {x["name"] for x in cur if x.get("active")}
    acc, gone, rej = set(), set(), set()
    for s in res.get("log_findings", []):
        for x in s["illegal"]:
            if x["accepted"]:
                acc.add(x["name"])
                if x["name"] not in cur_names:
                    gone.add(x["name"])
            else:
                rej.add(x["name"])
    cur_act = [x for x in cur if x.get("active")]
    cur_inert = [x for x in cur if not x.get("active")]
    if cur_act:
        add(45 + min(15, 5 * (len(cur_act) - 1)), _T("Flags prohibidos en la config activa"),
            _T("%d flag(s) que tus reglas marcan, en la config que Roblox o el strap carga al abrir.") % len(cur_act))
    if gone:
        add(50, _T("Flags prohibidos que ya no están"),
            _T("Los logs de Roblox muestran %s cargado(s) al abrir el juego, pero ya no aparecen en los archivos.")
            % ", ".join(sorted(gone)[:4]))
    elif acc and not cur:
        add(40, _T("Flags prohibidos usados en una sesión"), _T("Los logs muestran flags prohibidos aceptados por Roblox."))
    if rej and not (cur or acc):
        add(5, _T("Intento de flags prohibidos"), _T("Roblox rechazó %d flag(s) prohibidos; no tuvieron efecto.") % len(rej))
    if any(e["valid"] is False for e in res.get("exes", [])):
        add(45, _T("Roblox modificado"), _T("RobloxPlayerBeta.exe no tiene una firma válida de Roblox."))
    if res.get("dll_bad"):
        add(35, _T("DLL sin firma dentro de Roblox"), _T("%d módulo(s) sin firma cargados en el proceso.") % len(res["dll_bad"]))
    ren = [x for x in res.get("exe_ids", []) if x["kind"] == "renombrado"]
    if ren:
        add(35, _T("Strap renombrado"), "%s con otro nombre: %s" % (ren[0]["strap"], os.path.basename(ren[0]["path"])))
    if res.get("tools"):
        add(20, _T("Herramientas de modificación abiertas"), ", ".join(t["name"] for t in res["tools"][:3]))
    if [h for h in res.get("hidden", []) if h["lvl"] == "high"]:
        add(10, _T("Ejecutable de strap fuera de su carpeta"), _T("Hay un strap guardado en Descargas, Escritorio u otra carpeta."))
    if res.get("procs"):
        add(8, _T("Strap abierto durante el check"), ", ".join(p["name"] for p in res["procs"][:3]))
    if any(STRAP_RX.search(r.get("parent") or "") for r in res.get("roblox_procs", [])):
        add(8, _T("Roblox lanzado por un strap"), _T("El proceso padre de Roblox es un strap."))
    if res.get("empty_strap_logs"):
        add(12, _T("Logs de strap borrados"), _T("Carpeta de logs vacía en: ") + ", ".join(res["empty_strap_logs"]))
    rec = [x for x in res.get("recycle", []) if x.get("ep") and now - x["ep"] < 86400]
    old = [x for x in res.get("recycle", []) if not (x.get("ep") and now - x["ep"] < 86400)]
    if rec:
        add(15, _T("Borró cosas relacionadas en las últimas 24 h"), ", ".join(x["name"] for x in rec[:3]))
    elif old:
        add(4, _T("Hay cosas relacionadas en la papelera"), ", ".join(x["name"] for x in old[:3]))
    if any(f.get("recent") for f in res.get("flag_files", [])):
        add(12, _T("Archivo de flags modificado hace menos de 1 h"), _T("Alguien tocó los flags justo antes del check."))
    if any(r.get("up_min") is not None and r["up_min"] < 5 for r in res.get("roblox_procs", [])):
        add(6, _T("Roblox se abrió justo antes del check"), "Lleva menos de 5 minutos abierto.")
    ex = res.get("exec", [])
    ran24 = any(now - p["ts"] < 86400 for p in res.get("prefetch", [])) or \
        any(x["kind"] == "strap" and x.get("exists") and x.get("ep") and now - x["ep"] < 86400 for x in ex)
    if ran24:
        add(6, _T("Strap ejecutado en las últimas 24 h"), _T("Según el historial de ejecución de Windows."))
    gone = [x for x in ex if x["kind"] in ("strap", "inyector") and not x.get("exists") and x.get("ep") and now - x["ep"] < 7 * 86400]
    if gone:
        add(15, _T("Strap o inyector ejecutado y luego borrado"),
            _T("Windows registra que se abrió %s, pero el archivo ya no está.") % ", ".join(x["name"] for x in gone[:3]))
    tl = [x for x in ex if x["kind"] == "tool" and x.get("ep") and now - x["ep"] < 86400]
    if tl and not res.get("tools"):
        add(10, _T("Herramienta de modificación usada en las últimas 24 h"), ", ".join(x["name"] for x in tl[:3]))
    pg = [x for x in res.get("exec_gone", []) if x.get("ep") and now - x["ep"] < 3600]
    if pg:
        add(6, _T("Programa ejecutado justo antes del check y borrado"),
            _T("%s se abrió en la última hora y ya no existe.") % ", ".join(x["name"] for x in pg[:3]))
    au = [a for a in res.get("autoruns", []) if a["kind"] in ("strap", "inyector", "tool")]
    if au:
        add(4, _T("Strap o herramienta configurado para abrirse con Windows"), ", ".join(a["name"] for a in au[:3]))
    dfh = [x for x in (res.get("diff") or {}).get("items", []) if x["lvl"] == "high"]
    if dfh:
        add(20 + min(15, 5 * (len(dfh) - 1)), _T("Borró o cambió cosas durante el check"),
            _T("Entre una revisión y otra: ") + "; ".join(x["text"] for x in dfh[:3]))
    dh = [d for d in res.get("defender", []) if d["lvl"] == "high"]
    if dh:
        add(15, _T("Exclusión del antivirus para un strap o inyector"), ", ".join(d["value"] for d in dh[:2]))
    tr = res.get("traces") or {}
    if any(x.get("sus") for x in tr.get("pca", [])):
        add(25, _T("Windows registra que se abrio un strap o herramienta"), next(x["path"] for x in tr["pca"] if x.get("sus")))
    if tr.get("usn"):
        add(20, "Archivos de strap renombrados o borrados en el disco", tr["usn"][0]["name"])
    if tr.get("logs_cleared"):
        add(25, "Visor de eventos borrado", _T("Un jugador normal no borra el Visor de eventos."))
    lim = [t for t, ok in ((_T("Prefetch desactivado"), tr.get("prefetch_off")),
                           (_T("Hora del sistema cambiada"), tr.get("time_changed")),
                           (_T("Diario USN reiniciado hace poco"), (tr.get("usn_new_days") or 99) < 3),
                           (_T("Historial de Windows (UserAssist) apagado"), res.get("ua_off"))) if ok]
    if lim:
        add(10 * len(lim), _T("Señales de limpieza anti-revisión"), ", ".join(lim))
    if tr.get("usb_exec"):
        add(22, _T("Ejecutado desde USB o disco externo"),
            _T("Correr el strap desde otra unidad evita dejar rastro en C:. Ruta: ") + tr["usb_exec"][0]["path"])
    if tr.get("removable"):
        add(18, _T("Strap o flags en una unidad extraible conectada"), tr["removable"][0])
    if tr.get("dns"):
        add(20, _T("La PC se conecto a un dominio de strap o inyector"), ", ".join(tr["dns"][:3]))
    if res.get("roblox_logs_gap") == "vacia":
        add(18, _T("Logs de Roblox borrados"), _T("No hay ningun log; no se puede ver que flags cargo al abrir."))
    if res.get("injected"):
        add(40, _T("Inyeccion en memoria en Roblox"),
            _T("%d modulo(s) metidos en Roblox desde una ruta temporal o ya borrada: %s")
            % (len(res["injected"]), res["injected"][0]["path"]))
    if tr.get("fileless"):
        add(22, _T("Ejecucion en memoria (fileless)"), _T("PowerShell bajo y ejecuto algo sin dejar archivo: ") + tr["fileless"][0][:80])
    if res.get("timestomp"):
        add(15, _T("Fechas falsas (timestomp)"), _T("%d archivo(s) con fecha manipulada: %s") % (len(res["timestomp"]), res["timestomp"][0]["path"]))
    if res.get("masquerade"):
        add(30, _T("Proceso disfrazado de sistema"), _T("%s corriendo fuera de Windows: %s")
            % (res["masquerade"][0]["name"], res["masquerade"][0]["path"]))
    if tr.get("injectors"):
        add(45, _T("Inyector de flags en el disco"), "%s (%s)" % (tr["injectors"][0]["path"], tr["injectors"][0]["how"]))
    if tr.get("ads"):
        add(25, _T("Datos ocultos en flujos alternos (ADS)"), _T("%d archivo(s) con algo escondido dentro: %s")
            % (len(tr["ads"]), tr["ads"][0]["file"]))
    nonlegit_dirs = [d for d in res.get("dirs", []) if not _is_legit(d)]
    if nonlegit_dirs:
        add(3, _T("Strap instalado"), _T("Tener un strap instalado no es trampa por sí solo: ") +
            ", ".join(os.path.basename(d) for d in nonlegit_dirs))
    score = min(100, sum(x["pts"] for x in f))
    level = "bajo" if score < 20 else ("medio" if score < 50 else "alto")
    f.sort(key=lambda x: -x["pts"])
    return {"score": score, "level": level, "factors": f}


# ---------------------------------------------------------------- escaneo
def scan():
    """Devuelve un dict con todo el resultado. Nunca escribe nada en el sistema del jugador."""
    t0 = time.time()
    res = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "now_ep": t0, "alerts": [], "procs": [], "dirs": [],
           "dir_info": [], "exes": [], "dlls": [], "dll_bad": [], "flags": [], "flag_files": [], "logs": [],
           "total_flags": 0, "tools": [], "admin": is_admin()}
    alert = lambda lvl, msg: res["alerts"].append({"lvl": lvl, "msg": msg})

    # tareas lentas de PowerShell en paralelo (arranque automatico y antivirus)
    import concurrent.futures as _cf
    import pccheck_forense as fx
    _pool = _cf.ThreadPoolExecutor(max_workers=3)
    _f_auto = _pool.submit(fx.autoruns)
    _f_def = _pool.submit(fx.defender_exclusions, res["admin"])
    _f_tr = _pool.submit(fx.traces, res["admin"], t0)

    procs = _procs()
    res["n_procs"] = len(procs)
    for p in procs:
        n = (p.get("Name") or "").lower()
        if any(s in n for s in STRAP_NAMES):
            res["procs"].append({"name": p.get("Name"), "pid": p.get("Id"), "path": p.get("Path") or "", "ep": p.get("ep")})
            alert("high", _T("Proceso de strap activo: %s") % p.get("Name"))
        elif any(t in n for t in TOOL_NAMES):
            res["tools"].append({"name": p.get("Name"), "pid": p.get("Id"), "path": p.get("Path") or "", "ep": p.get("ep")})
            alert("high", _T("Herramienta de modificación abierta: %s") % p.get("Name"))
    res["roblox_running"] = any((p.get("Name") or "").lower() in ROBLOX_PROCS for p in procs)
    SYS = {"svchost","explorer","lsass","csrss","services","winlogon","smss","wininit",
           "runtimebroker","dllhost","taskhostw","conhost","spoolsv","sihost","ctfmon"}
    win = os.path.expandvars("%SystemRoot%").lower()
    res["masquerade"] = []
    for p in procs:
        n = (p.get("Name") or "").lower().replace(".exe","")
        path = (p.get("Path") or "")
        if n in SYS and path and not path.lower().startswith(win):
            res["masquerade"].append({"name": p.get("Name"), "pid": p.get("Id"), "path": path})
            alert("high", "Proceso con nombre de sistema corriendo fuera de Windows (disfraz): %s en %s" % (p.get("Name"), path))

    seen_names = set()
    for d in install_dirs():
        m = STRAP_RX.search(os.path.basename(d))
        name = m.group(1).capitalize() if m else os.path.basename(d)
        res["dirs"].append(d)
        res["dir_info"].append({"path": d, "name": name, "ep": _ctime(d), "when": fmt(_ctime(d))})
        if name.lower() not in seen_names:
            seen_names.add(name.lower())
            alert("low" if _is_legit(d) else "mid", _T("Strap instalado: %s (%s)") % (name, d))

    exes = set(p["Path"] for p in procs if (p.get("Name") or "").lower() in ROBLOX_PROCS and p.get("Path"))
    exes |= set(glob.glob(os.path.join(LAD, "Roblox", "Versions", "*", "RobloxPlayerBeta.exe")))
    out = ps('Get-Process RobloxPlayerBeta -ErrorAction SilentlyContinue | ForEach-Object { $_.Modules } | Select-Object -ExpandProperty FileName -Unique')
    mods = [m for m in out.splitlines() if m.strip()]
    win = os.path.expandvars("%SystemRoot%").lower()
    res["n_dlls"] = len(mods)
    mods_ext = [m for m in mods if not (m.lower().startswith(win) or "\\roblox\\versions\\" in m.lower())]
    firmas = _sigs(sorted(exes) + mods_ext)
    res["sig_unverified"] = 0

    for e in sorted(exes):
        st, subj = firmas.get(e, ("", ""))
        if not st:
            res["sig_unverified"] += 1
            res["exes"].append({"path": e, "sha": sha256(e), "status": "no verificado", "signer": "", "valid": None})
            continue
        valid = st.startswith("Valid") and "roblox" in subj.lower()
        res["exes"].append({"path": e, "sha": sha256(e), "status": st, "signer": subj, "valid": valid})
        if not valid:
            alert("high", _T("RobloxPlayerBeta.exe sin firma valida de Roblox (posible parche)"))

    res["injected"] = []
    tmp = (os.environ.get("TEMP", "").lower(), os.path.join(LAD, "temp").lower(),
           os.path.join(os.environ.get("APPDATA", ""), "").lower(), user_dirs().get("Downloads","").lower())
    for m in mods_ext:
        low = m.lower()
        if not os.path.exists(m):
            res["injected"].append({"path": m, "why": _T("cargado en Roblox pero el archivo ya no existe")})
            alert("high", _T("Modulo cargado en Roblox que ya no existe en disco (inyeccion en memoria): ") + os.path.basename(m))
        elif any(low.startswith(t) for t in tmp if t):
            res["injected"].append({"path": m, "why": _T("cargado desde una carpeta temporal/Descargas")})
            alert("high", _T("Modulo cargado en Roblox desde carpeta temporal/Descargas (inyeccion): ") + m)
        st = firmas.get(m, ("", ""))[0]
        if not st:
            res["sig_unverified"] += 1
            continue
        if not st.startswith("Valid"):
            res["dll_bad"].append({"path": m, "status": st})
            alert("high", _T("DLL sin firma cargada en Roblox: ") + os.path.basename(m))
    if res["sig_unverified"]:
        alert("low", _T('No se pudieron verificar %d firma(s) en esta PC (Windows bloqueo PowerShell). No cuenta como prueba.') % res["sig_unverified"])

    # --- flags en archivos ---
    why_of = matcher()
    deadline = time.time() + 40
    known = _flag_files()
    all_files = [(f, False) for f in known] + [(f, True) for f in _generic_flag_files(set(known), deadline)]
    for f, strict in all_files:
        try:
            with open(f, encoding="utf-8-sig") as fh:
                data = _extract_flags(json.load(fh), strict)
            if not data:
                continue
        except Exception:
            alert("mid", _T("No se pudo leer el archivo de flags: ") + f)
            continue
        mt = os.path.getmtime(f)
        age = (time.time() - mt) / 60
        active = not strict  # not strict = config que Roblox/strap si carga; strict = .json suelto en Descargas/Escritorio
        res["flag_files"].append({"path": f, "owner": _owner(f), "count": len(data), "ep": mt,
                                  "mtime": fmt(mt), "recent": age < 60, "active": active})
        if age < 60 and active:
            alert("mid", _T("Archivo de flags modificado hace %d min: %s") % (age, f))
        res["total_flags"] += len(data)
        for name, val in data.items():
            why = why_of(name)
            if why:
                res["flags"].append({"name": name, "value": str(val), "why": why, "active": active,
                                     "owner": _owner(f), "file": f, "mtime": fmt(mt), "recent": age < 60})
    merged = {}
    for f in res["flags"]:
        k = (f["owner"], f["name"], f["value"], f["why"])
        if k in merged:
            merged[k]["n_files"] += 1
            merged[k]["active"] = merged[k]["active"] or f["active"]
        else:
            f["n_files"] = 1
            merged[k] = f
    res["flags"] = list(merged.values())
    act = [x for x in res["flags"] if x["active"]]
    inert = [x for x in res["flags"] if not x["active"]]
    if act:
        alert("high", _T("%d flags ilegales en la config que Roblox carga") % len(act))
    if inert:
        alert("low", _T('%d flag(s) ilegales en un archivo guardado (Descargas/Escritorio) que NO esta aplicado. Tener el archivo no es prueba de que lo haya usado.') % len(inert))

    # --- logs ---
    logs = []
    for s in sorted(set(x.capitalize() for x in STRAP_FOLDERS)):
        logs += [(s, p) for p in glob.glob(os.path.join(LAD, s, "Logs", "*")) if os.path.isfile(p)]
    rb = sorted(glob.glob(os.path.join(LAD, "Roblox", "logs", "*.log")), key=os.path.getmtime)[-6:]
    logs += [("Roblox", p) for p in rb]
    res["empty_strap_logs"] = []
    for s in sorted(set(x.capitalize() for x in STRAP_FOLDERS)):
        d = os.path.join(LAD, s, "Logs")
        try:
            if os.path.isdir(d) and not any(os.path.isfile(os.path.join(d, n)) for n in os.listdir(d)):
                res["empty_strap_logs"].append(s)
                alert("mid", _T("Carpeta de logs vacia en %s (posible borrado)") % s)
        except OSError:
            pass
    for owner, p in logs:
        mt = _mtime(p) or 0
        res["logs"].append({"owner": owner, "path": p, "name": os.path.basename(p), "ep": mt,
                            "recent": time.time() - mt < 600, "kb": max(1, os.path.getsize(p) // 1024),
                            "mtime": fmt(mt)})

    # --- Roblox abierto ---
    res["roblox_procs"] = _roblox_procs()
    for rp in res["roblox_procs"]:
        par = (rp.get("parent") or "").lower()
        if any(s in par for s in STRAP_NAMES):
            alert("high", _T("Roblox fue lanzado por un strap: %s") % rp.get("parent"))
        if rp.get("up_min") is not None and rp["up_min"] < 5:
            alert("mid", _T("Roblox lleva abierto solo %d min (se abrio justo antes del check)") % rp["up_min"])

    # --- cambios recientes ---
    res["recent"] = _recent_changes(time.time() + 15)
    sens = [r for r in res["recent"] if re.search(r"(?i)clientappsettings\.json$|\.(exe|dll)$", r["path"])]
    if sens:
        alert("mid", _T("%d archivo(s) clave modificados en las ultimas %d h (ver Actividad)") % (len(sens), RECENT_HOURS))

    # --- rastros ---
    res["hidden"] = _hidden_straps(time.time() + 20)
    for h in res["hidden"]:
        alert(h["lvl"], "%s: %s" % (h["why"].capitalize(), h["path"]))
    hidden_paths = {os.path.normcase(h["path"]) for h in res["hidden"]}
    # --- historial de ejecucion de Windows (UserAssist / BAM) ---
    try:
        eh = fx.exec_history(user_dirs(), t0)
    except Exception:
        eh = {"items": [], "gone": [], "bam_ok": False, "n_total": 0, "candidates": [], "cand_ep": {}}
    res["exec"], res["exec_gone"] = eh["items"], eh["gone"]
    res["bam_ok"], res["exec_total"] = eh["bam_ok"], eh["n_total"]
    res["ua_off"] = eh.get("ua_off", False)

    # --- rastros que sobreviven al borrado y senales de limpieza ---
    try:
        tr = _f_tr.result(timeout=90)
    except Exception:
        tr = {"pca": [], "usn": [], "prefetch_off": False, "usn_new_days": None, "logs_cleared": [], "time_changed": [],
              "usb_exec": [], "removable": [], "dns": [], "fileless": [], "defender_off": [], "injectors": [], "ads": []}
    for x in tr["pca"]:
        x["sus"] = (not _is_legit(x["path"])) and (x["kind"] != "strap" or "ez4" in x["path"].lower() or not os.path.exists(x["path"]))
    tr["usn"] = [x for x in tr["usn"] if re.search(r"(?i)delete|rename|borr|cambi", x["reason"] or "")]
    res["traces"] = tr
    for h in tr.get("fileless", [])[:6]:
        alert("high", _T("Rastro de ejecucion en memoria (PowerShell): ") + h)
    for d in tr.get("defender_off", []):
        alert("low", "Microsoft Defender " + d + _T(" (no es prueba de trampa; mucha gente lo apaga)"))
    for x in tr.get("injectors", []):
        alert("high", _T("Inyector detectado por %s: %s") % (x["how"], x["path"]))
    for x in tr.get("ads", [])[:6]:
        alert("high", _T("Dato oculto en flujo alterno (ADS): %s en %s") % (x["stream"], x["file"]))
    cand = [e["path"] for e in res.get("exes", [])] + res.get("dirs", []) + \
           [f["path"] for f in res.get("flag_files", [])] + [i["path"] for i in res.get("injected", [])]
    res["timestomp"] = fx.timestomp(cand)
    for x in res["timestomp"]:
        alert("mid", _T("Fecha falsa (%s) en %s") % (x["why"], x["path"]))
    for x in [x for x in tr["pca"] if x["sus"]][:10]:
        alert("high", _T("Windows (PCA) registra que se abrio %s el %s y ya no existe o es inyector") % (x["path"], x["when"] or "?"))
    for x in tr["usn"][:10]:
        alert("high", _T("El disco registra actividad de %s (%s) %s") % (x["name"], x["reason"] or "cambio", x["when"]))
    if tr["logs_cleared"]:
        alert("high", _T("Alguien borro el Visor de eventos de Windows (%s)") % tr["logs_cleared"][0])
    if tr["time_changed"]:
        alert("mid", _T("Se cambio la hora del sistema %d vez/veces en 30 dias") % len(tr["time_changed"]))
    if tr["prefetch_off"]:
        alert("mid", _T("Prefetch de Windows desactivado (no es normal; borra rastro de ejecucion)"))
    if tr["usn_new_days"] is not None and tr["usn_new_days"] < 3:
        alert("mid", _T("El diario del disco (USN) se reinicio hace %.1f dias") % tr["usn_new_days"])
    for x in tr.get("usb_exec", [])[:8]:
        alert("high", _T("Se ejecuto desde la unidad %s (USB/externa, no C:): %s") % (x["drive"], x["path"]))
    for p2 in tr.get("removable", [])[:8]:
        alert("high", _T("Strap/inyector o archivo de flags en una unidad extraible conectada: ") + p2)
    for d in tr.get("dns", [])[:8]:
        alert("high", _T("La PC se conecto a un dominio de strap/inyector: ") + d)
    # hueco en logs de Roblox: Roblox instalado y usado, pero sin log reciente
    rb_logs = [p3 for p3 in glob.glob(os.path.join(LAD, "Roblox", "logs", "*.log"))]
    newest = max((_mtime(p3) or 0 for p3 in rb_logs), default=0)
    rb_dir = os.path.join(LAD, "Roblox", "logs")
    if os.path.isdir(rb_dir) and res.get("exes") and not res.get("roblox_running"):
        if not rb_logs:
            res["roblox_logs_gap"] = "vacia"
            alert("high", _T("Carpeta de logs de Roblox vacia (posible borrado): no se puede ver que flags cargo"))
        elif t0 - newest > 7 * 86400:
            res["roblox_logs_gap"] = "viejo"
            alert("mid", _T("El log mas reciente de Roblox tiene %d dias; falta el de las ultimas sesiones") % int((t0 - newest) / 86400))
    try:
        cands = _exe_candidates(time.time() + 15)
        seen_c = {os.path.normcase(c) for c in cands}
        cands += [c for c in eh["candidates"] if os.path.normcase(c) not in seen_c]
        res["exe_ids"] = _classify_exes(_exe_identity(cands), hidden_paths)
    except Exception:
        res["exe_ids"] = []
    for x in res["exe_ids"]:
        ran = eh.get("cand_ep", {}).get(os.path.normcase(x["path"]))
        if ran:
            x["ran"] = fmt(ran)
            x["why"] += _T(" (ya se ejecutó el %s)") % fmt(ran)
    for x in res["exe_ids"]:
        alert(x["lvl"], "%s: %s" % (x["why"].capitalize(), x["path"]))
    res["recycle_total"], res["recycle"] = _recycle()
    if res["recycle"]:
        alert("mid", _T("%d elemento(s) relacionados en la papelera (ver Actividad)") % len(res["recycle"]))
    pf = _prefetch()
    res["prefetch"] = pf if pf is not None else []
    res["prefetch_ok"] = pf is not None
    for p in res["prefetch"]:
        alert("mid", "Se ejecuto %s hace poco (Prefetch, ultima vez %s)" % (p["name"], p["last"]))
    for x in res["exec"]:
        if x["lvl"] == "high":
            alert("high", "Se ejecutó %s (%s) y ya no existe en la PC" % (x["name"], x["when"] or "fecha desconocida"))
        elif x["lvl"] == "mid":
            alert("mid", _T("Se ejecutó %s el %s (historial de Windows)") % (x["name"], x["when"]))
    for x in res["exec_gone"]:
        if x["lvl"] == "mid":
            alert("mid", _T("Se ejecutó %s hace %d min y ya no existe") % (x["name"], max(1, (t0 - x["ep"]) / 60)))
    try:
        res["autoruns"] = _f_auto.result(timeout=60) or []
    except Exception:
        res["autoruns"] = []
    try:
        dx = _f_def.result(timeout=60)
    except Exception:
        dx = None
    _pool.shutdown(wait=False)
    res["defender_ok"] = dx is not None
    res["defender"] = dx or []
    for a in res["autoruns"]:
        if a["lvl"] == "mid":
            alert("mid", "%s se abre solo con Windows (%s)" % (a["name"], a["where"]))
    for d in res["defender"]:
        if d["lvl"] == "high":
            alert("high", "Exclusión del antivirus para %s" % d["value"])
        elif d["lvl"] == "mid":
            alert("mid", "Exclusión del antivirus: %s" % d["value"])

    # --- sesiones y flags vistos en los logs de Roblox ---
    import pccheck_logs
    res["log_findings"], res["sessions"] = [], []
    current = {f["name"] for f in res["flags"]}
    for l in [x for x in res["logs"] if x["owner"] == "Roblox"]:
        try:
            a = pccheck_logs.analyze(l["path"], why_of, max_lines=0)
        except Exception:
            continue
        res["sessions"].append({"log": l["name"], "first_ep": a["first_ep"], "last_ep": a["last_ep"],
                                "first": a["first"], "last": a["last"], "minutes": a["minutes"],
                                "games": a["games"], "local_flags": a["local_flags"], "local_ep": a["local_ep"],
                                "illegal": a["illegal"]})
        if not a["local_flags"]:
            continue
        bad = [x for x in a["illegal"] if x["accepted"]]
        res["log_findings"].append({"log": l["name"], "when": a["local_ts"], "local_flags": a["local_flags"],
                                    "accepted": a["accepted"], "denied": a["denied"], "illegal": a["illegal"]})
        gone = [x["name"] for x in bad if x["name"] not in current]
        if gone:
            alert("high", _T("El log %s muestra flags prohibidos cargados al abrir Roblox que ya no estan en los archivos: %s")
                  % (l["name"][:40], ", ".join(gone[:5])))
        elif bad:
            alert("mid", _T("El log %s confirma %d flag(s) prohibido(s) cargados al abrir Roblox") % (l["name"][:40], len(bad)))

    res["sessions"] = _merge_sessions(res["sessions"])
    seen_lf, lf2 = set(), []
    for x in res["log_findings"]:
        k = (x["when"], x["local_flags"])
        if k not in seen_lf:
            seen_lf.add(k)
            lf2.append(x)
    res["log_findings"] = lf2
    seen_al, al2 = set(), []
    for a in res["alerts"]:
        k = re.sub(r"El log \S+", "El log", a["msg"])
        if k not in seen_al:
            seen_al.add(k)
            al2.append(a)
    res["alerts"] = al2
    res["timeline"] = build_timeline(res)
    finalize(res)
    res["secs"] = round(time.time() - t0, 1)
    return res


def finalize(res):
    res["risk"] = risk(res)
    sc = res["risk"]["score"]
    res["verdict"] = "limpio" if sc < 20 else ("revisar" if sc < 50 else "sospechoso")
    return res


# ---------------------------------------------------------------- comparar dos revisiones
def diff_scans(a, b):
    """Que cambio entre la revision anterior (a) y la nueva (b) en la misma sesion."""
    out = []
    add = lambda lvl, text: out.append({"lvl": lvl, "text": text})
    base = os.path.basename
    la = {l["path"]: l for l in a.get("logs", [])}
    lb = {l["path"] for l in b.get("logs", [])}
    for p_, l in la.items():
        if p_ not in lb and not os.path.exists(p_):
            add("high", _T("Se borró el log %s (%s)") % (l["name"], l["owner"]))
    fa = {(f["owner"], f["name"]): f for f in a.get("flags", [])}
    fb = {(f["owner"], f["name"]): f for f in b.get("flags", [])}
    for k in sorted(fa.keys() - fb.keys()):
        add("high", "Se quitó el flag prohibido %s (%s)" % (k[1], k[0]))
    for k in sorted(fb.keys() - fa.keys()):
        add("mid", _T("Apareció el flag prohibido %s (%s)") % (k[1], k[0]))
    for k in sorted(fa.keys() & fb.keys()):
        if str(fa[k].get("value")) != str(fb[k].get("value")):
            add("mid", "Cambió el valor de %s: %s → %s" % (k[1], fa[k].get("value"), fb[k].get("value")))
    ffa = {f["path"]: f for f in a.get("flag_files", [])}
    ffb = {f["path"]: f for f in b.get("flag_files", [])}
    for p_ in sorted(ffa.keys() - ffb.keys()):
        add("high", "Desapareció un archivo de flags de %s: %s" % (ffa[p_]["owner"], p_))
    for p_ in sorted(ffb.keys() - ffa.keys()):
        add("mid", _T("Apareció un archivo de flags de %s (%d flags)") % (ffb[p_]["owner"], ffb[p_]["count"]))
    for p_ in sorted(ffa.keys() & ffb.keys()):
        x, y = ffa[p_], ffb[p_]
        if x["count"] != y["count"]:
            add("high" if y["count"] < x["count"] else "mid",
                "El archivo de flags de %s pasó de %d a %d flags" % (y["owner"], x["count"], y["count"]))
        elif abs((x.get("ep") or 0) - (y.get("ep") or 0)) > 1:
            add("mid", _T("Se modificó el archivo de flags de %s") % y["owner"])
    ra = {(x["name"], x["from"]) for x in a.get("recycle", [])}
    for x in b.get("recycle", []):
        if (x["name"], x["from"]) not in ra:
            add("high" if x.get("strap") else "mid", _T("Se mandó a la papelera: %s") % x["name"])
    ta, tb = a.get("recycle_total") or 0, b.get("recycle_total") or 0
    if tb < ta:
        add("high", "Se vació o se restauró algo de la papelera (%d → %d elementos)" % (ta, tb))
    pa = {p_["name"].lower(): p_["name"] for p_ in a.get("procs", []) + a.get("tools", [])}
    pb = {p_["name"].lower(): p_["name"] for p_ in b.get("procs", []) + b.get("tools", [])}
    for k in sorted(pa.keys() - pb.keys()):
        add("mid", _T("Se cerró %s") % pa[k])
    for k in sorted(pb.keys() - pa.keys()):
        add("high", _T("Se abrió %s") % pb[k])
    ra_ = {r_.get("pid") for r_ in a.get("roblox_procs", [])}
    rb_ = {r_.get("pid") for r_ in b.get("roblox_procs", [])}
    if ra_ and not rb_:
        add("mid", _T("Se cerró Roblox"))
    elif rb_ and ra_ and not (ra_ & rb_):
        add("low", _T("Roblox se reinició"))
    elif rb_ and not ra_:
        add("low", _T("Se abrió Roblox"))
    da, db = set(a.get("dirs", [])), set(b.get("dirs", []))
    for d in sorted(da - db):
        add("high", _T("Se borró o desinstaló la carpeta %s") % d)
    for d in sorted(db - da):
        add("mid", _T("Apareció la carpeta %s") % d)
    xa = {x["path"]: x for x in a.get("exe_ids", []) + a.get("hidden", [])}
    xb = {x["path"] for x in b.get("exe_ids", []) + b.get("hidden", [])}
    for p_ in sorted(xa.keys() - xb):
        if not os.path.exists(p_):
            add("high", _T("Se borró %s (%s)") % (base(p_), xa[p_]["why"]))
    for p_ in sorted(xb - xa.keys()):
        add("mid", _T("Apareció %s") % base(p_))
    ea = {x["path"]: x.get("ep") or 0 for x in a.get("exec", []) + a.get("exec_gone", [])}
    for x in b.get("exec", []) + b.get("exec_gone", []):
        if (x.get("ep") or 0) > ea.get(x["path"], 0) + 1 and (x.get("ep") or 0) >= a.get("now_ep", 0) - 5:
            add("mid" if x.get("kind") != "borrado" else "low", "Se ejecutó %s entre una revisión y otra" % x["name"])
    return {"prev_time": a.get("time"), "minutes": max(1, int((b["now_ep"] - a["now_ep"]) / 60)),
            "prev_score": (a.get("risk") or {}).get("score", 0), "items": out}


def read_log(path, allowed):
    """Lee un log completo. Solo permite rutas que scan() listo."""
    if path not in allowed:
        return "Ruta no permitida."
    with open(path, "rb") as f:
        return f.read().decode("utf-8", errors="replace")
