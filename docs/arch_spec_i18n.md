# Architectural Specification — Frontend Internationalization (i18n)

This specification describes the requirements for adding multi-language support to the BambuDash frontend, with German as the default language and English as secondary.

---

## 🏗️ Requirements

### 1. i18n Infrastructure Setup (`next-intl`)
- Install `next-intl` as the i18n library for Next.js 14 App Router.
- Use **"without i18n routing" mode** — locale is stored in a `NEXT_LOCALE` cookie, no `[locale]` URL segments.
- Create the i18n configuration:
  - `src/i18n/config.ts` — exports `locales: ['de', 'en']` and `defaultLocale: 'de'`.
  - `src/i18n/request.ts` — reads locale from the `NEXT_LOCALE` cookie (or `Accept-Language` header), falls back to `'de'`.
- Wrap `next.config.mjs` with `createNextIntlPlugin`.
- Add `NextIntlClientProvider` to the root layout (`src/app/layout.tsx`).
- Set `<html lang="...">` dynamically based on the active locale.

### 2. Translation Files
- Create `src/messages/de.json` and `src/messages/en.json`.
- Organize strings by namespace:
  - `common` — shared strings (Loading, Processing, Save, Cancel, etc.)
  - `login` — login/register page strings
  - `navigation` — sidebar, header, status indicators
  - `dashboard` — KPI cards, sections, telemetry labels
  - `settings` — settings page strings
- **German is the primary language.** All existing English strings are moved into `en.json`; German translations are written fresh into `de.json`.
- All ~65+ currently hardcoded strings must be covered.

### 3. String Extraction & Replacement
- **All 4 existing TSX files must be modified:**
  - `src/app/page.tsx` — replace 1 hardcoded string with `useTranslations('common')`.
  - `src/app/login/page.tsx` — replace ~16 strings with `useTranslations('login')`.
  - `src/app/dashboard/layout.tsx` — replace ~14 strings with `useTranslations('navigation')`.
  - `src/app/dashboard/page.tsx` — replace ~35 strings with `useTranslations('dashboard')`.
- Use `t('key')` for simple strings and `t('key', { variable })` for interpolated strings.
- Metadata (`title`, `description`) in root layout must also use translations via `getTranslations()`.

### 4. Settings Page with Language Picker
- Create `src/app/dashboard/settings/page.tsx`.
- Must include a **Language Selector** (Dropdown or segmented control: `Deutsch` / `English`).
- On language change:
  1. Set cookie `NEXT_LOCALE` to the selected locale (`de` or `en`).
  2. Trigger a full page reload (`window.location.reload()`) to apply the new locale server-side.
- The selected language must persist across browser sessions (cookie-based).
- Style consistently with the existing dashboard design (dark mode, glassmorphism, `lucide-react` icons).
- Include placeholder sections for future settings (profile, notifications) to make the page feel complete.

### 5. Constraints & Quality Gates
- **No URL changes.** Routes stay as-is (`/dashboard`, `/login`, etc.). No `[locale]` segment.
- **No backend changes required.** i18n is purely frontend.
- **TypeScript safety.** All translation keys must be type-safe via next-intl's TypeScript integration.
- **Build must pass.** `npm run build` must succeed with zero errors.
- **Cookie name:** `NEXT_LOCALE` (next-intl convention).
