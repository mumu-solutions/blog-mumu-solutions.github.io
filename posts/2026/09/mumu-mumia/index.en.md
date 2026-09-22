---
title: Introducing MUMia, our mascot and agent
date: 2026-09-22
description: Meet MUMia — MUMU Solutions' robot mascot, a technology and automation specialist whose hat is an actual screen.
tags: mumia, branding, mascot
image: /posts/2026/09/mumu-mumia/images/mumia-figure.png
---

This is the blog's first post, and it's only fair that it introduces who will show up
in the rest of them: **MUMia**, MUMU Solutions' mascot and agent.

![MUMia, the MUMU Solutions mascot](images/mumia-figure.png)

# Who is MUMia

MUMia is a robotic agent specialised in technology and automation, wrapped in panels
that hide slots, each holding the right tool for the job. His hat is a full graphic
display in cowboy-hat format, and that display carries the whole performance: a mark on
the screen, plus the angle of the brim.

Everything below the hat — the visor, the blue sensor — is identical across all nine
expressions, because a sensor reads the room, it does not perform. One element moves; it
is the biggest one on the head, and it reads at sizes where an eye could not. The brim
is always 1.52× the width of the head, because that's the character's visual joke —
shrink it and he stops being this character.

MUMia has no neck and no shoulders, mitten hands with no fingers, and exactly one
trailing wrap off the right hip, which is where all of his secondary action lives.

# Why he exists

MUMia is the face — and the voice — of MUMU Solutions across content, product and
automation. He is generated from two sources: `brand/tokens.json` (colour, ratios,
limits) and the character's geometry, so the model sheet, the assets and the
documentation can never drift from what actually ships. That's what makes it possible
to use him consistently across this blog, the institutional site, and any other brand
channel.

# Where the colours come from

MUMia's colours derive from `mumu-branding`, where hex is the authority. His eye is the
brand's canonical blue; the hat uses `accent4` from the chart palette, borrowed rather
than invented, so the mascot introduces no colour the brand system doesn't already own.

# What's next

This blog is static — Markdown at the source, HTML at the destination — and every post
lives in its own folder, with its own assets. It's simple to write, simple to review,
and simple to publish: a commit with an updated `VERSION` goes straight live. MUMia will
keep showing up here whenever it makes sense — after all, he's the resident agent behind
a good chunk of what MUMU Solutions automates.
