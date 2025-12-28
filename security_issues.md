# Security Review Report

**Date:** December 25, 2025
**Branch:** productionready
**Reviewer:** Automated Security Analysis

---

## Summary

| Severity | Count |
|----------|-------|
| HIGH     | 2     |
| MEDIUM   | 1     |

---

## Vuln 1: Hardcoded Instagram Credentials in `Backend/app.py:53-54`

* **Severity:** HIGH
* **Category:** `hardcoded_credentials`
* **Confidence:** 9/10
* **Description:** Instagram account credentials (email and password) are hardcoded directly in the main application file. These credentials are used in production code paths - specifically as a fallback mechanism when Instagram accounts lack stored cookies (line 286). There is no environment variable override mechanism.
* **Exploit Scenario:** Any developer or attacker with repository access immediately obtains valid Instagram credentials. The password `Maverick15#` and email `jigglyphilcam@gmail.com` can be used to compromise the Instagram account, perform unauthorized actions, and access private data. Since these are committed to git history, the credentials remain exposed even if later removed.
* **Recommendation:**
  1. Move credentials to environment variables
  2. Add `INSTAGRAM_EMAIL` and `INSTAGRAM_PASSWORD` to the `Settings` class in `config.py`
  3. Rotate the exposed Instagram account password immediately
  4. Consider scrubbing git history if repository is or becomes public

---

## Vuln 2: Hardcoded Credentials and API Key in `Backend/Scripts/remote_cookie_updater.py:18-27`

* **Severity:** HIGH
* **Category:** `hardcoded_credentials`
* **Confidence:** 8/10
* **Description:** The remote cookie updater script contains hardcoded API key (`_SqyioaT9ItcqTEoJmqU38y_PHOeN5fk12asrMKC3Qs`) and Instagram credentials (`jigglyphilcam@gmail.com` / `Maverick15#`). The file is not gitignored and contains no environment variable mechanism. The API key grants access to admin cookie management endpoints.
* **Exploit Scenario:**
  1. Attacker with repository access obtains the API key
  2. Uses API key to authenticate to `/api/admin/instagram-accounts/{id}/cookies` endpoint
  3. Can update, list, or manipulate all Instagram account cookies in the system
  4. The Instagram credentials provide full access to post content, access messages, and control the account
* **Recommendation:**
  1. Create a `.env` file approach or template version of this script
  2. Add the script to `.gitignore` or create a `.example` version without real credentials
  3. Rotate the exposed API key using `generate_api_key.py`
  4. Change the Instagram account password immediately

---

## Vuln 3: Stored XSS via innerHTML in `Frontend/script.js:317-326`

* **Severity:** MEDIUM
* **Category:** `xss`
* **Confidence:** 8/10
* **Description:** User-provided Instagram usernames are inserted directly into the DOM via `innerHTML` without HTML escaping. The `updateUsernamesList()` function uses template literals that directly interpolate the `username` variable into both HTML content and onclick attributes. Notably, other files in the codebase (`groups.js`, `analytics.js`) implement proper `escapeHtml()` functions, but `script.js` does not use any escaping.
* **Exploit Scenario:**
  1. User enters malicious username: `test<img src=x onerror=alert(document.cookie)>`
  2. Username is stored and rendered via `innerHTML`
  3. XSS payload executes in victim's browser context
  4. Attacker can steal `authToken` from localStorage, enabling session hijacking
  5. If saved to a group, becomes persistent/stored XSS affecting anyone who loads the group
* **Recommendation:**
  1. Use `textContent` instead of `innerHTML` for the username display
  2. Implement and use an `escapeHtml()` function (already exists in `groups.js` lines 250-254)
  3. Sanitize the onclick attribute or use `addEventListener` with proper escaping
  4. Add server-side validation in `schemas.py` to reject usernames containing HTML special characters

---

## Remediation Priority

1. **IMMEDIATE:** Rotate all exposed credentials (Instagram password, API key)
2. **HIGH:** Move all credentials to environment variables
3. **HIGH:** Scrub git history to remove committed secrets
4. **MEDIUM:** Implement XSS protections in Frontend/script.js

---

## Files Requiring Changes

| File | Issue | Priority |
|------|-------|----------|
| `Backend/app.py` | Hardcoded credentials | IMMEDIATE |
| `Backend/Scripts/remote_cookie_updater.py` | Hardcoded credentials + API key | IMMEDIATE |
| `Backend/config.py` | Add credential config options | HIGH |
| `Frontend/script.js` | XSS via innerHTML | MEDIUM |
| `.gitignore` | Add sensitive scripts | HIGH |
