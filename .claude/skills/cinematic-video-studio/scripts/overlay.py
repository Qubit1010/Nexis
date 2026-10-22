"""HTML -> PNG overlays for the cut (captions, titles, labels, placeholder slots, end card).

wkhtmltoimage renders them because its Qt WebKit shapes Arabic (and other RTL scripts)
correctly, which Pillow without libraqm and ffmpeg drawtext without harfbuzz do not.
Layouts are authored in a 720x1280 space and rendered at 1.5x zoom to 1080x1920.

Old-WebKit gotchas this module already works around (do not "modernize" them away):
  * gradients need the -webkit-linear-gradient form, or the element renders transparent;
  * an <img> pointing at an SVG ignores CSS width/height; logos must be raster (PNG);
  * --transparent must be off for opaque cards (the end card), on for overlays.
"""
import re, shutil, subprocess, sys, tempfile
from pathlib import Path

W, H, ZOOM = 1080, 1920, 1.5
RTL = re.compile(r"[\u0590-\u08FF\uFB1D-\uFEFF]")


def find_wkhtml():
    for c in (shutil.which("wkhtmltoimage"), r"C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe",
              "/usr/local/bin/wkhtmltoimage", "/usr/bin/wkhtmltoimage"):
        if c and Path(c).exists():
            return c
    sys.exit("wkhtmltoimage not found. Install wkhtmltopdf (it ships wkhtmltoimage).")


def run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED: {' '.join(map(str, cmd))[:400]}\n{r.stderr[-2500:]}")
    return r


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Overlays:
    """Renders overlays in one client's brand. `profile` is the client profile dict."""

    def __init__(self, profile, profile_dir):
        self.p, self.dir = profile, Path(profile_dir)
        self.tmp = Path(tempfile.mkdtemp(prefix="cvs_"))
        self.wk = find_wkhtml()
        self.n = 0
        b = profile["brand"]
        self.primary, self.accent, self.dark = b["primary"], b["accent"], b["dark"]
        faces = ""
        for weight, key in (("normal", "font_latin_regular"), ("bold", "font_latin_bold")):
            if b.get(key):
                faces += (f"@font-face{{font-family:Brand;font-weight:{weight};"
                          f"src:url('{self.path(b[key]).as_uri()}');}}")
        rtl = b.get("font_rtl_family", "'Segoe UI',Tahoma,Arial")
        self.css = f"""{faces}
html,body{{margin:0;padding:0;width:720px;height:1280px;background:transparent;overflow:hidden;}}
.rtl{{font-family:{rtl};direction:rtl;}}
.ltr{{font-family:Brand,'Segoe UI',Arial;}}
.tag{{position:absolute;top:22px;left:22px;font:600 15px 'Segoe UI';color:#fff;
  background:rgba(0,0,0,.45);padding:5px 10px;border-radius:4px;letter-spacing:.3px}}
.grad{{position:absolute;left:0;right:0;bottom:0;height:430px;
  background:-webkit-linear-gradient(top,rgba(0,0,0,0),rgba(0,0,0,.62))}}
.c2{{position:absolute;left:46px;right:46px;bottom:150px;text-align:center}}
.c2 .p{{color:#fff;font-size:29px;font-weight:600;line-height:1.5;text-shadow:0 2px 10px rgba(0,0,0,.9)}}
.c2 .s{{color:#dbe7f4;font-size:19px;line-height:1.4;margin-top:8px;letter-spacing:.3px;text-shadow:0 2px 8px rgba(0,0,0,.9)}}
.c2 .who{{font:600 13px Brand,'Segoe UI';color:{self.accent};letter-spacing:3px;text-transform:uppercase;
  margin-bottom:6px;text-shadow:0 2px 8px rgba(0,0,0,.9)}}
"""

    def path(self, p):
        p = Path(p)
        return p if p.is_absolute() else (self.dir / p).resolve()

    @staticmethod
    def cls(text):
        return "rtl" if RTL.search(text or "") else "ltr"

    def png(self, body, extra_css="", transparent=True):
        self.n += 1
        html = self.tmp / f"o{self.n}.html"
        html.write_text(f"<html><head><meta charset='utf-8'><style>{self.css}{extra_css}</style></head>"
                        f"<body>{body}</body></html>", encoding="utf-8")
        out = self.tmp / f"o{self.n}.png"
        run([self.wk, "--quiet", "--enable-local-file-access", *(["--transparent"] if transparent else []),
             "--zoom", ZOOM, "--width", W, "--height", H, "--format", "png", html, out])
        return out

    # -- building blocks ---------------------------------------------------------
    def tag(self, text):
        return self.png(f"<div class='tag'>{esc(text)}</div>")

    def caption(self, primary, secondary="", who=""):
        w = f"<div class='who'>{esc(who)}</div>" if who else ""
        s = f"<div class='s {self.cls(secondary)}'>{esc(secondary)}</div>" if secondary else ""
        return self.png(f"<div class='grad'></div><div class='c2'>{w}"
                        f"<div class='p {self.cls(primary)}'>{esc(primary)}</div>{s}</div>")

    def title(self, primary, secondary=""):
        css = (".tt{position:absolute;top:890px;left:0;right:0;text-align:center;color:#fff}"
               ".tt .a{font-size:50px;font-weight:300;text-shadow:0 2px 14px rgba(0,0,0,.9)}"
               ".tt .b{font-size:15px;letter-spacing:10px;margin-top:10px;color:#f1e3c8;"
               "text-transform:uppercase;text-shadow:0 2px 10px rgba(0,0,0,.9)}")
        b = f"<div class='b {self.cls(secondary)}'>{esc(secondary)}</div>" if secondary else ""
        return self.png(f"<div class='tt'><div class='a {self.cls(primary)}'>{esc(primary)}</div>{b}</div>", css)

    def label(self, primary, secondary="", top=150):
        css = (f".lb{{position:absolute;top:{top}px;left:40px;right:40px;text-align:center;color:#fff}}"
               ".lb .a{font-weight:bold;font-size:30px;letter-spacing:8px;text-shadow:0 2px 12px rgba(0,0,0,.9)}"
               f".lb .b{{font-size:30px;font-weight:600;color:{self.accent};margin-top:4px;"
               "text-shadow:0 2px 12px rgba(0,0,0,.9)}")
        b = f"<div class='b {self.cls(secondary)}'>{esc(secondary)}</div>" if secondary else ""
        return self.png(f"<div class='lb'><div class='a {self.cls(primary)}'>{esc(primary)}</div>{b}</div>", css)

    def placeholder(self, heading, sub, note, line_primary="", line_secondary="", who=""):
        """A dashed card marking footage that must be filmed for real (e.g. a doctor's answer)."""
        css = (f".dc{{position:absolute;top:240px;left:70px;right:70px;border:2px dashed {self.accent};"
               "border-radius:14px;background:rgba(0,0,0,.55);padding:26px 22px;text-align:center;color:#fff}"
               ".dc .t{font-weight:bold;font-size:30px;line-height:1.25} .dc .u{font-size:23px;margin-top:10px}"
               f".dc .n{{font-size:14px;color:{self.accent};margin-top:14px;line-height:1.5}}")
        cap = ""
        if line_primary:
            w = f"<div class='who'>{esc(who)}</div>" if who else ""
            s = f"<div class='s {self.cls(line_secondary)}'>{esc(line_secondary)}</div>" if line_secondary else ""
            cap = (f"<div class='grad'></div><div class='c2'>{w}"
                   f"<div class='p {self.cls(line_primary)}'>{esc(line_primary)}</div>{s}</div>")
        return self.png(f"<div class='dc'><div class='t {self.cls(heading)}'>{esc(heading)}</div>"
                        f"<div class='u {self.cls(sub)}'>{esc(sub)}</div>"
                        f"<div class='n ltr'>{esc(note).replace(chr(10), '<br>')}</div></div>{cap}", css)

    def html(self, body, css=""):
        return self.png(body, css)

    def end_card(self, extra_primary="", extra_secondary="", qr=False):
        e = self.p["end_card"]
        logo = self.path(self.p["brand"]["logo_png"]).as_uri()
        lines = "".join(f"<div class='q {self.cls(t)}'>{esc(t)}</div>" for t in e.get("lines", []))
        foot = "<br>".join(f"<span class='{self.cls(t)}'>{esc(t)}</span>" for t in e.get("footer", []))
        extra = ""
        if extra_primary:
            extra = (f"<div class='x {self.cls(extra_primary)}'>{esc(extra_primary)}</div>"
                     f"<div class='x2 {self.cls(extra_secondary)}'>{esc(extra_secondary)}</div>")
            if qr:
                extra += "<div class='qr ltr'>QR code</div>"
        css = (f"html,body{{background:#fff !important}}"
               f".ec{{position:absolute;top:0;left:0;width:720px;height:1280px;background-color:#F3F8FD;"
               f"background:-webkit-linear-gradient(top,#ffffff,{e.get('bg_bottom', '#E6F0FA')});text-align:center}}"
               f".ec img{{width:{e.get('logo_width', 360)}px;margin-top:280px}}"
               f".q{{font-weight:bold;font-size:38px;color:{self.primary};margin-top:14px}}"
               f".q:first-of-type{{margin-top:60px}}"
               f".x{{font-weight:bold;font-size:26px;color:{self.dark};margin-top:34px}}"
               f".x2{{font-size:26px;color:{self.dark};margin-top:2px}}"
               f".qr{{width:120px;height:120px;margin:14px auto 0;border:3px dashed {self.accent};font-size:15px;"
               f"color:{self.accent};line-height:120px}}"
               ".foot{position:absolute;bottom:70px;left:0;right:0;font-size:18px;color:#55607a;line-height:1.7}")
        return self.png(f"<div class='ec'><img src='{logo}'>{lines}{extra}<div class='foot'>{foot}</div></div>",
                        css, transparent=False)
