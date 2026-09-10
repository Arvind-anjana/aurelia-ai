# 🎨 Aurélia Design System: "Ivory Atelier"

This document outlines the visual identity, aesthetic philosophy, and UI architecture of Aurélia.

## Brand & Style

Aurélia rejects the cold, sterile, "cyber" aesthetics of conventional AI tools. Instead, she is designed to feel like an intimate, tactile intellectual companion—evoking curated stationery, hand-pressed cotton rag paper, and warm architectural stone.

The aesthetic philosophy marries **Warm Minimalist Editorial** with **Subtle Tactile Glassmorphism**. Every interaction evokes the unhurried authority of a private concierge or classical atelier.

## The Logo

The logo is a custom SVG geometric composition representing a blooming lotus or sprout, symbolizing intellectual growth.
- **Center Leaf**: Solid crisp black (`#111111`)
- **Flanking Leaves**: Outlined with a 6px stroke
- **Stem**: Grounded bottom line
- **Typography**: The word **AURÉLIA** sits directly beside the icon, set in `Playfair Display`, `font-size: 1.9rem`, `letter-spacing: 2px`.

## Color Palette

The palette simulates natural materials: vellum, archival parchment, and deep soft charcoal ink.

- **Background Canvas**: `#F8F5F0` (Pure unbleached silk)
- **Sidebar Background**: `#D4AF37` (Solid Elegant Gold)
- **Sidebar Borders**: `#B8962E` (Deep Gold)
- **Header (Navbar)**: Translucent white `rgba(255, 255, 255, 0.4)` with a `16px` backdrop blur for a frosted glass effect.
- **Ink & Typography**: `#111111` or `#333333` (Softened charcoal/black to prevent optical strain).

## Typography

The typographic hierarchy establishes tension between literary grandeur and contemporary clarity.

- **Playfair Display (Serif)**: Used for headers, the main logo, and sticky titles. It anchors the conversational genesis and imbues the interface with an authorial voice.
- **Inter / Plus Jakarta Sans (Sans-Serif)**: Used for the working engine: conversational prompts, assistant body replies, and the document viewer.

## UI Components (Streamlit Implementation)

Aurélia is built on Streamlit, but heavily modified via Custom CSS injection in `ui.py`:

1. **The Sidebar**: Features the solid `#D4AF37` background, heavily rounded right corners (`28px`), and the custom SVG logo floating cleanly at the top.
2. **Chat Bubbles**: Elevated with glassmorphism (`rgba(255, 255, 255, 0.6)`), a faint gold border, and subtle drop shadows that push them off the page. The shadow deepens slightly on hover to encourage interaction.
3. **Chat Input**: Inverted to a dark `#222222` background to create a visual anchor at the bottom of the screen.
4. **Document Viewer**: Rendered in a dual-pane split layout. PDFs and TXT files are displayed inside an elevated container with heavy rounded corners (`24px`) and subtle shadowing to match the chat interface perfectly.
5. **Interactive Elements**: Buttons and file uploaders share the sweeping `24px` or `16px` border radiuses for a soft, tactile feel.