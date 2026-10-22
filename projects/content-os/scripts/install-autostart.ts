// Start Content OS at Windows sign-in, hidden, with no admin rights needed: a small .vbs
// in the per-user Startup folder runs scripts\content-os.cmd with no console window.
// (`schtasks /SC ONLOGON` would also work but usually needs an elevated prompt.)
//
//   node scripts/install-autostart.ts           # install (also starts it now)
//   node scripts/install-autostart.ts --remove  # uninstall
//   node scripts/install-autostart.ts --print   # show what would be written
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const launcher = path.join(HERE, "content-os.cmd");
const startup = path.join(process.env.APPDATA || "", "Microsoft", "Windows", "Start Menu", "Programs", "Startup");
const target = path.join(startup, "Content OS.vbs");
const vbs = `' Content OS: start the local server hidden at sign-in (installed by projects/content-os/scripts/install-autostart.ts)\r\nCreateObject("WScript.Shell").Run """${launcher}""", 0, False\r\n`;

const arg = process.argv[2];
if (arg === "--print") {
  console.log(`${target}\n\n${vbs}`);
} else if (arg === "--remove") {
  fs.rmSync(target, { force: true });
  console.log(`removed ${target}`);
} else {
  if (!fs.existsSync(startup)) throw new Error(`Startup folder not found: ${startup}`);
  fs.writeFileSync(target, vbs);
  console.log(`installed ${target}`);
  // Start it now too, detached, so there is no need to sign out and back in.
  spawn("wscript.exe", [target], { detached: true, stdio: "ignore", windowsHide: true }).unref();
  console.log("started: http://127.0.0.1:4600 (logs in data/logs/server.log)");
}
