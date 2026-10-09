# Phase 2: turning on the real WhatsApp number

Until this is done, the QR opens a WhatsApp-style web chat. After it, the QR opens WhatsApp itself, with
the demo code already typed. The app code is already deployed and waiting (`/api/whatsapp`).

## What you do (about 1 hour of clicks, then Meta's review)

1. **Buy a new SIM** (Jazz, Zong, Telenor or Ufone). It must never have been registered on WhatsApp.
   Do not use 0311 8340514: once a number is on the Cloud API it stops working in the normal WhatsApp app.
2. Go to **business.facebook.com** and create a Business portfolio for NexusPoint (if you do not have one).
3. Go to **developers.facebook.com → My Apps → Create app → Business**, and add the **WhatsApp** product.
4. In **WhatsApp → API Setup**, choose **Add phone number**:
   - display name: **NexusPoint Demo**
   - category: Professional Services
   - verify the new SIM by SMS code
5. **Permanent token:** Business settings → **System users** → Add (Admin) → **Generate token** for your
   app with the permissions `whatsapp_business_messaging` and `whatsapp_business_management`.
6. From **API Setup**, copy: the **Phone number ID**, the **WhatsApp Business Account ID**, and from
   **App settings → Basic**, the **App secret**.
7. Send those four values (phone number ID, WABA ID, token, app secret) plus the new number. I save them
   to `.env` and Vercel. I never paste them back into the chat.

## What I do with them

1. Set on Vercel (production): `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_APP_SECRET`,
   `WHATSAPP_VERIFY_TOKEN` (a random string I generate), `DEMO_WHATSAPP_NUMBER` (e.g. `92300XXXXXXX`).
2. In the Meta app, **WhatsApp → Configuration → Webhook**:
   - callback URL `https://nexuspoint-demo.vercel.app/api/whatsapp`
   - the verify token
   - subscribe to `messages`
3. Redeploy. Every hub's QR switches to `wa.me/<demo number>?text=DEMO-<code> Assalam o alaikum`.
4. Test from 2 real phones on 2 different demos at the same time (routing is by the demo code), and after
   a forced expiry (the "demo ended" reply).

## Limits worth knowing

- The demo number only ever replies; it never starts a conversation. Customer-started chats need no
  message templates and no business verification.
- Meta charges per message in Pakistan (about $0.015 for a service reply from 1 October 2026, per one
  report). A demo conversation costs a few rupees.
- Voice notes get a polite "please type for now" reply until Phase 3 (Urdu transcription).
