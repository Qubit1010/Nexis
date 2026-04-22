// One-time script to generate a Google OAuth2 refresh token (Web application client).
// Run: node scripts/get-refresh-token.js <CLIENT_ID> <CLIENT_SECRET>

const { google } = require("googleapis");
const http = require("http");
const url = require("url");

const CLIENT_ID = process.argv[2];
const CLIENT_SECRET = process.argv[3];

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error("Usage: node scripts/get-refresh-token.js <CLIENT_ID> <CLIENT_SECRET>");
  process.exit(1);
}

const REDIRECT_URI = "http://localhost:3333/callback";
const SCOPES = [
  "https://www.googleapis.com/auth/documents",
  "https://www.googleapis.com/auth/drive.file",
];

const oAuth2Client = new google.auth.OAuth2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI);

const authUrl = oAuth2Client.generateAuthUrl({
  access_type: "offline",
  scope: SCOPES,
  prompt: "consent",
});

console.log("\n1. Open this URL in your browser:\n");
console.log(authUrl);
console.log("\n2. Sign in as hassanaleem86@gmail.com and click Allow.");
console.log("3. The token will be printed here automatically.\n");

const server = http.createServer(async (req, res) => {
  const qs = new url.URL(req.url, "http://localhost:3333").searchParams;
  const code = qs.get("code");
  if (!code) { res.end("No code found."); return; }
  res.end("Done! Check your terminal for the env vars.");
  server.close();
  try {
    const { tokens } = await oAuth2Client.getToken(code);
    console.log("\n✓ Add these to .env.local and Vercel:\n");
    console.log(`GOOGLE_CLIENT_ID=${CLIENT_ID}`);
    console.log(`GOOGLE_CLIENT_SECRET=${CLIENT_SECRET}`);
    console.log(`GOOGLE_REFRESH_TOKEN=${tokens.refresh_token}`);
  } catch (e) {
    console.error("Failed:", e.message);
  }
});

server.listen(3333, () => {
  console.log("Waiting for Google redirect on http://localhost:3333...\n");
});
