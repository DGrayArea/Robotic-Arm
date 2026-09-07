# Drawing Set — Worklist

Four defects across the 11-sheet set. All from auto-dimensioning and one stray
component; the geometry itself is fine. Mark `[x]` as you go.

**Do task 1 first.** Deleting the stray component renumbers the balloons, so
doing it after the others means redoing them.

| # | Task | Sheet | Time | Status |
|---|---|---|---|---|
| 1 | Close the parts-list gap | 1 | 15 min | ❌ |
| 2 | Reattach balloon 1 | 1 | 5 min | ❌ |
| 3 | Separate overlapping dimensions | Base, Jaw, 11 | 20 min | ❌ |
| 4 | Delete the duplicated 306.51 | Jaw | 2 min | ❌ |
| 5 | Verify and re-export | all | 10 min | ❌ |

---

## 0 — Before you start

- [ ] **File → Save As** a copy, or work knowing you can `Ctrl+Z`. Task 1
      deletes a component, which is the only irreversible step here.
- [ ] Note the current sheet count (11) so you can confirm nothing is lost.

---

## 1 — Close the parts-list gap · sheet 1 · 15 min

The list runs 1–8 then jumps to 10. Balloon 10 exists; balloon 9 does not.
`Jaw_6 (1) (1)` is hidden, so Fusion allocates it item 9 and then omits it from
the displayed list.

**Verify it is redundant before deleting:**

- [ ] Expand `Jaw_6 (1) (1):1` in the DESIGN browser
- [ ] Confirm it carries **no joints** anything else depends on
- [ ] Confirm the gripper uses `Jaw_6 (1)` + `Jaw_6 (1)(Mirror)` only

*Evidence it is a leftover from mirroring: it is hidden and has stayed hidden;
its volume is 35232.034 mm³, identical to `Jaw_6 (1)`; every 3D view shows a
two-finger gripper with no third finger anywhere.*

**Then:**

- [ ] Right-click `Jaw_6 (1) (1):1` → **Delete**
- [ ] Switch to the DRAWING tab — the view will flag as out of date
- [ ] Right-click the sheet-1 view → **Update**
- [ ] Confirm the parts list now reads **1–9 with no gap**

> **If it turns out not to be redundant:** tick it visible instead. It then
> appears as item 9 with its own balloon and the numbering is continuous — but
> you are showing a part that is not in the assembly, which is worse.

---

## 2 — Reattach balloon 1 · sheet 1 · 5 min

Balloon 1 sits low and right of the arm with a leader ending in empty space.
Every other balloon lands on its component.

- [ ] Click balloon 1 to select it
- [ ] Drag the **arrowhead end** of the leader — not the balloon — onto the Base
      casting at the bottom of the view
- [ ] Confirm the arrowhead snaps to an edge (it fills in when attached)

> **If it will not attach**, the leader has lost its reference. Delete the
> balloon and re-place it with **ANNOTATE → Balloon**, clicking the Base.

---

## 3 — Separate overlapping dimensions · 20 min

Auto Dimension places values without collision checking. Each of these is two
dimensions printing on top of each other.

| Sheet | Looks like | Actually is |
|---|---|---|
| 11/11 Jaw_6 (1)(Mirror) | `129.0489` | `129.04` + `129.89` |
| 11/11 Jaw_6 (1)(Mirror) | `1.928` stacked | two vertical dimensions |
| Base | `R4 Ø1180` | `R4` + `Ø180` |
| Jaw | `3θ` lower left | `35` + `30` |

For each:

- [ ] `129.04` / `129.89` on sheet 11
- [ ] stacked vertical pair on sheet 11
- [ ] `R4` / `Ø180` on the Base sheet
- [ ] `35` / `30` on the Jaw sheet

Click the dimension **text** once to select, then drag it clear. Extension lines
follow, so it stays attached to the geometry it measures. Nothing is deleted.

> **Faster if there are more than these four:** delete the auto-dimension set on
> the sheet and place what you need by hand with **DIMENSION → Dimension**.
> Twelve chosen dimensions read better than thirty-five automatic ones — a
> detail drawing only needs what a machinist would use to make the part.

---

## 4 — Delete the duplicated 306.51 · Jaw sheet · 2 min

`306.51` appears twice on the same view, once above and once below. Auto
Dimension offered both Baseline and Ordinate recipes and both include the
overall width.

- [ ] Click the redundant one — keep whichever has clearer extension lines,
      normally the lower
- [ ] Delete it

*A dimension appearing twice invites the reader to check whether the two
disagree, which is wasted attention on a drawing.*

---

## 5 — Verify and re-export · 10 min

- [ ] Sheet 1 parts list reads **1–9**, unbroken
- [ ] Every balloon lands on a component, balloon 1 included
- [ ] No overlapping text on any of the 11 sheets — page through them
- [ ] Sheet count still 11
- [ ] Title block still reads correctly
- [ ] Re-export the PDF if the report embeds it
- [ ] Log it as **week 17 Tuesday** in the logbook

---

## Definition of done

- [ ] Parts list continuous, no gap at 9
- [ ] All balloons attached to geometry
- [ ] No dimension text overlapping another
- [ ] No duplicated dimensions
- [ ] PDF re-exported
- [ ] Logbook entry written listing what was wrong

---

## Note for the report

None of this changes an engineering result. `Jaw_6 (1) (1)` was already excluded
from the mass table, and at 0.277 kg it would move the 411 N·m bound by 0.6% —
well inside the safety factor. So the drive selection stands either way.

Worth writing up as week 17 Tuesday regardless: listing what an auto-dimensioned
set got wrong shows you can read a drawing critically rather than accepting
whatever the tool produced. That reads better than a set with no defects
recorded.
