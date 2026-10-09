"""Server-side Confluence concept exploration. Credentials never enter outputs."""
import json
import os
import pathlib
import re
import time
import uuid
import urllib.request
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parent
ENV_FILE = ROOT.parents[2] / '.env'
MODEL = 'xai/grok-imagine-image-2.0'
BUDGET = 15.0

BASE = '''An original monumental contemporary sculpture for a premium creative technology studio. Three distinct material languages converge into one open aperture around one small precise cyan-blue point, color #02A1E1: a broad continuous satin-white folded surface with beautiful thickness and smooth sculptural curvature; precision-machined silver frames and tightly spaced lamellae with subtle brushed-metal detail; fine parallel white and silver filaments threading through the structure with clear intentional paths. Extremely restrained black architectural gallery, deep black background, refined studio softbox lighting, realistic specular highlights, gentle contact shadow, physically plausible materials, exceptional art direction. Asymmetric cinematic composition, sculpture occupies the upper and right two-thirds with cropped edges and intentional scale, left third and lower left remain quiet black negative space for website typography. No text, no logo, no letters, no watermark, no interface, no people, no robots, no circuit board, no purple, no rainbow, no broad neon glow, no floating dashboard, no stock technology motifs. 16:9 architectural artwork photograph, precise craft, elegant tension between organic surface and engineered structure.'''
VARIANTS = [
    ('01-convergence', BASE + ' Camera: low three-quarter angle, 50mm perspective. A huge sweeping white folded sheet arcs diagonally from the cropped top-right toward the center, surrounding silver frame ribs and a delicate filament bundle. The blue point is a tiny solid disc at the shared focal point, slightly right of center. A sophisticated gallery installation with a strong silhouette and dramatic controlled light.'),
    ('02-lamellar-aperture', BASE + ' Camera: more frontal with a subtle elevated three-quarter perspective, 65mm lens. The structure creates a tall elliptical opening on the right. A satin-white continuous fold flows around a staggered series of machined square frames with softened corners; fine filaments curve along its inner contour. A tiny blue disc anchors the opening. One dominant sculptural gesture, restrained surface reflections, large clear negative space on the left.'),
    ('03-folded-chamber', BASE + ' Camera: close side-oblique architectural perspective, 45mm lens. A white ribbon with broad elegant planar folds extends from outside the right edge and bends into an open oval chamber. Twelve silver precision frames emerge behind it with carefully spaced parallel filaments running through their center. Tiny cyan-blue center point. Strong spatial depth, immense scale, finely lit edges and physically convincing material joins; calm black space on the left.'),
]

def credentials():
    value = os.environ.get('HF_KEY') or os.environ.get('HF_CREDENTIALS')
    if not value:
        for line in ENV_FILE.read_text(encoding='utf-8-sig').splitlines():
            match = re.match(r'^\s*(?:export\s+)?HF_KEY\s*=\s*(.*?)\s*$', line)
            if match:
                value = match.group(1).strip().strip('"\'')
                break
    if not value or ':' not in value:
        raise RuntimeError('No usable HF_KEY available in the server environment.')
    return value

KEY = credentials()

def request(url, payload=None, idempotency=None):
    headers = {'Authorization': 'Key ' + KEY, 'Content-Type': 'application/json'}
    if idempotency:
        headers['Idempotency-Key'] = idempotency
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            error = json.loads(exc.read())
            message = str(error.get('detail') or error.get('message') or error.get('error') or 'HTTP request failed')
        except Exception:
            message = 'HTTP request failed'
        message = message.replace(KEY, '[redacted]')
        raise RuntimeError(f'HTTP {exc.code}: {message[:300]}') from None

def save(manifest):
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

def main():
    manifest_path = ROOT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {'model': MODEL, 'budget_usd': BUDGET, 'estimated_total_usd': 0, 'successful_estimated_total_usd': 0, 'concepts': []}
    existing_names = {entry['name'] for entry in manifest['concepts']}
    for name, prompt in VARIANTS:
        if name in existing_names:
            continue
        payload = {'prompt': prompt, 'quality': 'medium', 'resolution': '2k', 'aspect_ratio': '16:9'}
        estimate = request('https://api.higgsfield.ai/estimate/' + MODEL, payload)
        amount = float(estimate['usd'])
        if not (0 <= amount <= BUDGET) or manifest['estimated_total_usd'] + amount > BUDGET:
            raise RuntimeError('Account estimate exceeds the approved budget.')
        entry = {'name': name, 'input': payload, 'estimate': {'usd': amount, 'credits': estimate.get('credits')}, 'status': 'estimated'}
        manifest['estimated_total_usd'] += amount
        manifest['concepts'].append(entry)
        save(manifest)
        print(json.dumps({'name': name, 'estimate_usd': amount}), flush=True)
    print(json.dumps({'estimated_total_usd': manifest['estimated_total_usd']}), flush=True)
    for entry in manifest['concepts']:
        if entry.get('files') or entry['status'] in {'failed', 'nsfw', 'canceled'}:
            continue
        if 'request_id' not in entry:
            idem = entry.get('idempotency_key') or str(uuid.uuid4())
            entry['idempotency_key'] = idem
            save(manifest)
            submitted = request('https://api.higgsfield.ai/' + MODEL, entry['input'], idem)
            entry['request_id'] = submitted['request_id']
            entry['status'] = submitted['status']
            save(manifest)
            print(json.dumps({'name': entry['name'], 'request_id': entry['request_id'], 'status': entry['status']}), flush=True)
        poll_url = 'https://api.higgsfield.ai/requests/' + entry['request_id'] + '/status'
        deadline = time.monotonic() + 600
        while entry['status'] not in {'completed', 'failed', 'nsfw', 'canceled'}:
            if time.monotonic() > deadline:
                raise RuntimeError('Generation remains queued or in progress after ten minutes; request ID is saved.')
            time.sleep(5)
            result = request(poll_url)
            entry['status'] = result['status']
            save(manifest)
        if entry['status'] != 'completed':
            print(json.dumps({'name': entry['name'], 'status': entry['status'], 'estimated_charge_usd': 0}), flush=True)
            continue
        if 'result' not in locals() or result.get('request_id') != entry['request_id']:
            result = request(poll_url)
        for index, image in enumerate(result.get('images', []), 1):
            url = image['url']
            if not url.startswith('https://'):
                raise RuntimeError('Unexpected image URL scheme.')
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()
                content_type = response.headers.get_content_type()
            suffix = '.png' if content_type == 'image/png' else '.webp' if content_type == 'image/webp' else '.jpg'
            path = ROOT / (entry['name'] + (f'-{index}' if index > 1 else '') + suffix)
            path.write_bytes(data)
            entry.setdefault('files', []).append(path.name)
        manifest['successful_estimated_total_usd'] += entry['estimate']['usd']
        save(manifest)
        print(json.dumps({'name': entry['name'], 'status': entry['status'], 'files': entry.get('files', []), 'estimated_charge_usd': entry['estimate']['usd']}), flush=True)
    print(json.dumps({'successful_estimated_total_usd': manifest['successful_estimated_total_usd']}), flush=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        message = str(exc).replace(KEY, '[redacted]')
        print(json.dumps({'error_type': type(exc).__name__, 'error': message[:400]}), flush=True)
        raise SystemExit(1)
