# UI/UX Design Notes — Podcast Video Creator

This tool's interface follows the **CDD UI/UX Standards Framework v1.0**.
The styles live as a small design system in the CSS block at the top of
`app.py` (CSS custom properties under `:root`), so future changes happen
in one place.

## User journey

1. Upload an audio file.
2. Enter the course name and unit number / unit name (both required).
3. Select **Create video**.
4. Review the generated thumbnail, then **Download** the files and/or
   **Save to Google Drive**.

## Design tokens (in `:root`)

| Token | Value | Use |
|---|---|---|
| `--bg` / `--surface` | `#07191c` / `#0e2d31` | Page and input/card surfaces |
| `--primary` / `--primary-hover` | `#007a80` / `#00666b` | Create / Save (primary actions) |
| `--success` / `--warning` / `--danger` / `--info` | teal-green / amber / red / cyan | Status + messages |
| `--focus-ring` | `#5fe0e8` | Visible keyboard focus outline |
| `--radius`, `--space` | 12px, 1rem | Consistent corners and spacing |

## How it maps to the standards

- **§6 Layout / §7 Typography** — one bold H1 per page, section headings
  (`.sec-head`), body text at 16px, short labels and helper text, max
  content width for scannability.
- **§8 Colour & feedback** — a single primary colour for Create/Save;
  secondary (outlined) style for Download; status shown with **icon +
  text** badges (`✓ Ready`, `✓ Saved to Google Drive`), never colour
  alone. All foreground/background pairs meet **WCAG AA** (verified:
  primary button 5.13:1, body text 16.45:1).
- **§10 Forms** — every field has a visible label; required fields are
  marked with `*` plus a legend; placeholders are examples only;
  validation messages are specific and actionable (e.g. "Please enter a
  valid…" style) and confirmation is shown after success.
- **§11 Buttons** — consistent action wording (Create video, Save to
  Google Drive, Download video / thumbnail) and consistent placement.
- **§13 Accessibility (WCAG 2.2 AA)** — visible `:focus-visible`
  outlines on inputs, buttons and links; labels associated with inputs;
  sufficient contrast; meaning never conveyed by colour alone.
- **§14 Responsive** — fluid max-width container, 48px minimum touch
  targets, images capped to 100% width, mobile breakpoint at 640px.
- **§15 Content** — plain English, short sentences, action-style button
  labels, clear next steps after success or error.

## Known limitations

- Streamlit controls the underlying DOM, so some ARIA attributes and the
  exact focus-ring rendering depend on the Streamlit version.
- Status badges are presentational; the accompanying `st.error` /
  `st.info` messages carry the same meaning in text for assistive tech.
