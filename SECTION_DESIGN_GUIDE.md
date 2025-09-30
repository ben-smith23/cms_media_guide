# Section Title Page Design Options

## How to Use

I've created **3 different designs** for your section title pages. Each has a unique look and feel. To test them:

1. Look at the demo file: `latex/sections/order_events_DEMO.tex`
2. Uncomment the design you want to use (they're all shown at the top)
3. Compile your PDF to see the result

---

## ✨ OPTION A: Full-Page Image with Overlay Banner

**Visual Description:**
```
┌─────────────────────────────────────┐
│                                     │
│     [Action Photo fills entire      │
│      page as background]            │
│                                     │
│ ═══════════════════════════════════ │ ← Gold stripe
│ ███████████████████████████████████ │ ← Maroon banner
│ ███           1                 ███ │ ← Section number (white)
│ ███   MEET INFORMATION         ███ │ ← Title (gold)
│ ███████████████████████████████████ │
│ ═══════════════════════════════════ │ ← Gold stripe
│                                     │
│     [Action Photo continues]        │
│                                     │
└─────────────────────────────────────┘
```

**Characteristics:**
- 🎯 **Most Dramatic** - image dominates the page
- 💪 **Bold & Energetic** - perfect for sports
- 📸 Shows off your best action photos
- 🎨 Maroon banner + gold accents

**Best For:** High-impact sections, championship/records, team highlights

**Usage:**
```latex
\sectionImageOverlay{../assets/highlights/Highlights/DSC06229.jpg}{Meet Information}
```

---

## ✨ OPTION B: Diagonal Split Design

**Visual Description:**
```
┌─────────────────────────────────────┐
│ ███████████████████████             │
│ ███                  ⟋              │
│ ███    1              ⟋             │
│ ███                    ⟋            │
│ ███  MEET              ⟋ [Action    │
│ ███  INFORMATION        ⟋ Photo]    │
│ ███                      ⟋          │
│ ═══════════════════════════⟋══      │ ← Gold diagonal stripe
│                          ⟋   [Photo │
│                         ⟋    cont.] │
│                        ⟋            │
│                       ⟋             │
└─────────────────────────────────────┘
```

**Characteristics:**
- 🚀 **Modern & Dynamic** - angular, high-energy
- ⚡ Creates sense of movement
- 🎨 Maroon top-left, photo bottom-right
- ✨ Bold gold diagonal accent stripe

**Best For:** Contemporary feel, adds visual interest, dynamic sections

**Usage:**
```latex
\sectionDiagonalSplit{../assets/highlights/Highlights/DSC06229.jpg}{Meet Information}
```

---

## ✨ OPTION C: Side-by-Side Split

**Visual Description:**
```
┌─────────────────────────────────────┐
│                 ║                   │
│                 ║                   │
│                 ║                   │
│      80         ║    [Action        │
│                 ║     Photo         │
│  MEET           ║     fills         │
│  INFORMATION    ║     right         │
│                 ║     half]         │
│                 ║                   │
│  [Maroon]       ║                   │
│                 ║                   │
│                 ║                   │
└─────────────────────────────────────┘
       ↑ Gold vertical stripe
```

**Characteristics:**
- ✨ **Clean & Professional** - balanced and elegant
- 📖 Easy to read, clear hierarchy
- 🎨 Left: maroon + title | Right: photo
- 💛 Bold vertical gold stripe divider

**Best For:** Professional/formal sections, meet info, records tables

**Usage:**
```latex
\sectionSideBySide{../assets/highlights/Highlights/DSC06229.jpg}{Meet Information}
```

---

## 🎨 My Recommendation

**For "Meet Information":** I'd go with **Option C (Side-by-Side)** 
- It's clean and professional
- Easy to read
- Sets a formal tone for rules/schedules

**For exciting sections** (like "Championship Results", "Top Performances"): Use **Option A (Image Overlay)**
- Maximum visual impact
- Shows off action shots

**For modern sections** (like "Team Records", "Event Profiles"): Try **Option B (Diagonal Split)**
- Contemporary and dynamic
- Adds energy without being too bold

---

## 📝 Quick Start

1. Open `latex/sections/order_events.tex`
2. Replace the current section title code with one of these three commands
3. Choose a great photo from your `highlights` folder
4. Compile and see the result!

You can use **different styles for different sections** to add visual variety throughout the media guide.

