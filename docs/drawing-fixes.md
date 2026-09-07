# Drawing set — defects and how to fix them

Four defects in the 11-sheet set, all from auto-dimensioning and a stray
component. None is a modelling error; the geometry is fine. They are the sort of
thing a marker notices in ten seconds, so they are worth an hour.

Work top to bottom: fixing 1 first means the balloons renumber before you touch
anything else.

---

## 1. Parts list skips item 9 · sheet 1

**What you see.** The list runs 1–8 then jumps to 10. Balloon 10 exists on the
drawing; balloon 9 does not.

**Why.** `Jaw_6 (1) (1)` is unchecked in the browser. Fusion allocated it item 9
but excludes hidden components from the displayed list, so the number is
consumed and never shown.

**The likely intent: delete it.** The evidence says it is a leftover from
creating the mirrored finger, not a part of the design:

- it is hidden, and has been left hidden
- it has the same volume as `Jaw_6 (1)`, 35232.034 mm³ — an exact duplicate
- every 3D view shows a **two**-finger gripper; a third finger appears nowhere
- the two fingers actually used are `Jaw_6 (1)` and `Jaw_6 (1)(Mirror)`

**Check before deleting**, because it is irreversible in a way the others are
not: expand `Jaw_6 (1) (1)` in the browser and look for joints. If it carries a
joint that something else depends on, do not delete — hide-and-renumber instead.

Then, in the DESIGN workspace:

1. Right-click `Jaw_6 (1) (1):1` in the browser → **Delete**
2. Return to the DRAWING tab. The view will flag as out of date.
3. Right-click the sheet-1 view → **Update** (or the update prompt in the toolbar)
4. The parts list should now read 1–9 with no gap

**If you would rather keep it**, tick it visible instead. It then appears as
item 9 with its own balloon, and the numbering is continuous — but you are
showing a part that is not in the assembly, which is worse than deleting it.

---

## 2. Balloon 1 points at nothing · sheet 1

**What you see.** Balloon 1 sits low and right of the arm, with a short leader
ending in empty space. Every other balloon lands on its component.

**Fix.** Click the balloon to select it, then drag the **arrowhead end** of the
leader — not the balloon itself — onto the Base casting at the bottom of the
view. The arrowhead should snap to an edge and turn into a filled dot or arrow
when it has attached to geometry.

If it will not attach, the leader has lost its reference: delete the balloon and
re-place it with **ANNOTATE → Balloon**, clicking the Base directly.

---

## 3. Overlapping dimension text · several sheets

Auto Dimension places values without checking whether they collide. Each of
these is two separate dimensions printing on top of each other, so the text is
unreadable and in one case looks like a wrong number.

| Sheet | What it looks like | What it actually is |
|---|---|---|
| Jaw_6 (1)(Mirror), 11/11 | `129.0489` | `129.04` and `129.89` overlapping |
| Jaw_6 (1)(Mirror), 11/11 | `1.928` stacked | two vertical dimensions overlapping |
| Base | `R4 Ø1180` | `R4` and `Ø180` overlapping |
| Jaw | `3θ` near lower left | `35` and `30` overlapping |

**Fix, per instance.** Click the dimension text once to select it, then drag it
clear of its neighbour. The extension lines follow, so the dimension stays
attached to the geometry it measures. Nothing is deleted.

Where two dimensions genuinely measure the same thing, delete one rather than
moving it — see 4.

**Faster alternative if there are many.** Delete the auto-dimension set on the
sheet and place the dimensions you actually need by hand with **DIMENSION →
Dimension**. A drawing with twelve chosen dimensions reads better than one with
thirty-five automatic ones, and a detail drawing only needs what a machinist
would use to make the part.

---

## 4. Duplicated overall dimension · Jaw sheet

**What you see.** `306.51` appears twice on the same view, once above and once
below.

**Why.** Auto Dimension produced an overall width in two recipes — it was
offering both Baseline and Ordinate sets, and both include the overall.

**Fix.** Click the redundant one and delete it. Keep the one whose extension
lines are clearer, normally the lower. A dimension appearing twice invites the
reader to check whether they disagree, which is wasted attention on a drawing.

---

## Then

Re-check sheet 1: the parts list should read 1–9 unbroken, and every balloon
should land on a component. Re-export the PDF if the report embeds it.

Worth recording in the logbook as week 17 Tuesday — cleaning up an
auto-dimensioned set is real drawing work, and listing what was wrong with it
shows you can read a drawing critically rather than accepting whatever the tool
produced.
