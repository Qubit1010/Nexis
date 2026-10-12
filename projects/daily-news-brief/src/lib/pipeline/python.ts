import { existsSync } from "fs";
import { resolve } from "path";

/** Use an explicit interpreter, the checkout's environment, or Python on PATH. */
export function pythonExecutable(projectRoot: string, override?: string): string {
  if (override) return override;

  const localPython = resolve(
    projectRoot,
    ".venv",
    process.platform === "win32" ? "Scripts" : "bin",
    process.platform === "win32" ? "python.exe" : "python"
  );
  if (existsSync(localPython)) return localPython;

  return process.platform === "win32" ? "python" : "python3";
}
