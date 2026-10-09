# The 8-minute demo: "Your business, already running on NexusPoint"

For in-person meetings in Quetta. You show the owner their own business, not a sample.

## The night before (5 minutes per prospect)

1. Make the demo from their Google Maps link (or placeId or name):
   ```
   python projects/quetta-local-market/scripts/make_demo.py "<maps link>" --reset
   ```
   It prints the hub link, the chat link and the demo code, and writes two printouts:
   `deliverables/Health-Check-<slug>-en.pdf` and `-ur.pdf`.
2. Read the Review X-ray on the hub yourself. Know their top complaint and top praise by heart.
3. Make the offline copy, in case mobile internet is cut:
   ```
   python projects/nexuspoint-demo/scripts/snapshot.py <slug>
   ```
   Copy `deliverables/Offline-Demo-<slug>-en.html` and `-ur.html` to your phone.
4. Print the Health Check in the language the owner reads (Urdu for most traditional owners).

## Pre-flight (at their door, 2 minutes)

- Phone charged, hotspot on, the hub open. Opening it wakes the server, so the first reply is fast.
- Send one message in the hub's chat, then clear it: `python projects/nexuspoint-demo/scripts/reset_demo.py <slug>`
  (or leave it: it shows the dashboard is not empty and fake).
- Offline copy saved on the phone. If there is no signal, you run the meeting from it.

## The meeting

| Min | Do | Say (English / Roman Urdu) |
|---|---|---|
| 0-1 | Hand over the printed Health Check. | "This is what your customers see when they search for you." / "Yeh woh hai jo aap ke customer Google par dekhte hain." Point at the score and the red crosses. |
| 1-2 | Open **Your reviews** on the hub. | "We read your last 80 Google reviews. Customers love X. The complaint that keeps coming back is Y." Then the reply-rate box: "You replied to none of them. People read the replies before they choose." Pause. Let them read. |
| 2-4 | **Your assistant.** Ask them to scan the QR with their own phone. | "Message it the way your customers do. Ask for a booking, ask the price, ask anything." / "Jaise aap ke customer poochte hain, waise poochein." Stay quiet while they type. |
| 4-5 | Turn your phone to them: **Your dashboard**. | "Everything they just asked appears here for you: the booking, the summary, and a flag when your staff should step in." Point at the price question going to staff: "It never guesses prices. Your team confirms them." |
| 5-6 | **Your website.** | "This is a draft of your website, built from your Google listing. The button opens the same assistant." Show the two posts: "Ready to publish, in Urdu and English." |
| 6-7 | **Your numbers.** Hand them the phone. | "How many customers do you lose a week to missed calls or slow replies? What does one spend?" Let them move the sliders. Read the monthly number out loud. |
| 7-8 | **Your plan.** | "We would start with Growth. The first three businesses in each sector get 40% off setup in return for a short case study. Live in 14 days, or you pay nothing more until it is." Then stop talking. |

**The close:** "If you want to go ahead, press the YES button. It messages me directly. Or keep the link. It
works for 14 days, so show your partner." Leave the printout.

## If something goes wrong

| Problem | Move |
|---|---|
| WhatsApp QR slow or not live yet | The QR opens the web chat instead. It is the same assistant. |
| A reply takes more than 10 seconds | "The first message wakes it up." Send the next one. Replies after that take about 3 seconds. |
| No internet at all | Open the offline copy. It has their reviews, a played conversation, the dashboard layout and the website draft. |
| They ask a medical or legal question in the chat | That is the point: it hands over to staff and never guesses. Show the dashboard flag. |
| They ask "is this real AI?" | Ask them to try to trick it. Then show the honest "I am an automated assistant" answer. |

## After the meeting

- `https://nexuspoint-demo.vercel.app/admin?key=<DEMO_ADMIN_TOKEN from .env>` shows views, chats and YES clicks
  for every demo. A reopen two days later is your follow-up signal.
- Demos expire after 14 days on their own. The assistant then answers "this demo has ended" with your number.
