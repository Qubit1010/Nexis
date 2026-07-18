@echo off
REM Scheduled-task target: generate both briefs for today, then log + email the
REM digest. Self-locating (cd to the project root regardless of where it runs).
cd /d "%~dp0.."
echo [%date% %time%] Daily brief run starting...
call npx tsx scripts/daily-cron.ts
call npx tsx scripts/daily-tools.ts
call npx tsx scripts/daily-digest.ts
echo [%date% %time%] Daily brief run finished (exit %errorlevel%).
