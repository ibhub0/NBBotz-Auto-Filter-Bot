# SafeLink System Architecture & Flow

This document explains how the SafeLink Bot Integration works, from the moment a user requests a file to the final download.

## 1. The Token Generation (Telegram Bot)
**File**: `forward.py` (or `channel.py` in Auto-Forward-Bot)

When the bot receives a file/video to forward:

1.  **Generate Token**: It creates a unique "Deep Link" token (e.g., `getfile-caption-uuid`).
2.  **Encode Token**: It wraps this token in a Telegram Deep Link format (`https://t.me/BOT?start=TOKEN`) and encodes it using Base64.
3.  **Generate Short Code**: It creates a random 6-character code (e.g., `AbCd12`).
4.  **Save to Database**: It saves the mapping `AbCd12` -> `/#/verify/BASE64_TOKEN` in MongoDB.
5.  **Send Link**: It sends the user a short link: `https://demoby.vercel.app/AbCd12`.

## 2. The Link Resolution (Website Backend)
**File**: `api/resolve.ts` (Vercel Serverless Function)

When the user clicks `https://demoby.vercel.app/AbCd12`:

1.  **Request**: The browser hits the Website.
2.  **Routing**: `App.tsx` sees the short code and renders `ShortLinkPage`.
3.  **API Call**: `ShortLinkPage` calls `/api/resolve?code=AbCd12`.
4.  **Database Lookup**: The API connects to MongoDB, finds `AbCd12`, and returns the real URL (`/#/verify/BASE64_TOKEN`).
5.  **Redirect**: The page redirects the user to the Verification Page.

## 3. The Verification (Website Frontend)
**File**: `pages/VerifyPage.tsx`

When the user lands on `/#/verify/BASE64_TOKEN`:

1.  **Charset Bridge**: The page decodes the Standard Base64 token (from the bot) to get the plain text.
2.  **Re-Encode**: It re-encodes it using the **Custom Scrambled Base64** (defined in `crypto.ts`) used by the SafeLink system.
3.  **Navigation**: It redirects the user to a Random Blog Post (`PostPage`) with the Custom Encoded token.

## 4. The SafeLink Process (Post/SafeLink Page)
**File**: `pages/PostPage.tsx` & `components/SafeLink/SafeLinkOverlay.tsx`

On the Blog Post:

1.  **Timer & Verification**: The user sees the "I am not a robot" check and a countdown timer.
2.  **Step 1**: After the timer, they click "Continue".
3.  **Step 2**: They might be sent to another post (multi-page flow) or the final step.
4.  **Final Generation**: The "Go to Link" button appears.

## 5. The Final Redirect (Decryption)
**File**: `utils/crypto.ts`

When the user clicks "Go to Link":

1.  **Decode**: The site takes the Custom Encoded token and uses `SafeLinkCrypto.decode()` to turn it back into the Telegram Deep Link (`https://t.me/BOT?start=TOKEN`).
2.  **Redirect**: The browser opens the Telegram Bot with this Deep Link.
3.  **File Delivery**: The Bot sees the `start=TOKEN`, finds the file in its database, and sends it to the user.

## System Diagram

```mermaid
graph TD
    User((User))
    Bot[Telegram Bot]
    DB[(MongoDB)]
    WebShort[Website: /ShortCode]
    WebVerify[Website: /#/verify]
    WebPost[Website: Blog Post]
    
    User -- 1. Request Link --> Bot
    Bot -- 2. Generate Token & Code --> DB
    Bot -- 3. Send Short Link --> User
    User -- 4. Click Link --> WebShort
    WebShort -- 5. Resolve Code --> DB
    WebShort -- 6. Redirect --> WebVerify
    WebVerify -- 7. Transcode Token --> WebPost
    WebPost -- 8. Timer & Verify --> User
    User -- 9. Click "Get Link" --> Bot
    Bot -- 10. Send File --> User
```
