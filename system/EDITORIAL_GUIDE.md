# Little Chewz — Teacher Guide editorial guide

## Purpose and source material

This guide owns the **editorial judgment** used to draft and revise Little Chewz Teacher Guides: what to say, how much detail to include, and how to make a lesson easy to teach. It applies to human editors, AI writers, and AI-assisted revisions.

Use the **current accepted lesson source, approved lesson-specific slideshow, and relevant Teacher Guides and teacher companion resources** as the baseline for lesson content, terminology, activity choices, and level of detail. **Full Guide Revised.pdf** is the broader editorial and visual benchmark. Where examples differ, follow the current authoritative sources rather than older exported guides. Source precedence and file ownership are in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md).

Keep responsibilities separate: [EDIT.md](EDIT.md) governs editing, [WORKFLOW.md](WORKFLOW.md) governs review and checks, [RESOURCE_GUIDELINES.md](RESOURCE_GUIDELINES.md) governs companions, and [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md) governs slides. The [Teacher Guide template](../templates/teacher_guide/TEMPLATE.json) defines the starting data structure; the [renderer](../scripts/renderers/teacher_guide.py) owns visual layout.

## 1. Editorial standard

**Tell teachers what they need to do next.** A teacher should be able to scan the guide, prepare the lesson, and teach it without decoding long explanations.

- Write in the practical, welcoming Little Chewz voice: clear, encouraging, and confident, with the story and student experience at the centre.
- Prefer short, action-led directions. Retain detail when it changes preparation, teaching, a meaningful choice, or student understanding.
- Use the existing Teacher Guides and companion resources as models for how much explanation an activity needs. Concise means complete enough to teach, rather than the fewest possible words.
- Preserve approved story facts, character names, mission language, learning-cycle terminology, and the intended progression of the quest.
- Keep the main guide focused on the teachable route. Supporting explanations, extended prompts, examples, and reference material belong in linked companion resources.

## 2. Lesson framing

Retain the familiar sections and their purposes: **At a Glance, Learning goal, Learning outcomes, Preparation, Teaching focus, Teaching Flow**, and useful optional extensions. **Assessment** is optional and, when useful, stands below Teaching focus.

**At a Glance** gives a teacher the lesson's basic scope, audience, time, and practical setup needs. Match the approved lesson rather than adding generic context.

**Learning goal** is one concise sentence describing the central learning purpose, not an inventory of activities.

**Learning outcomes** are usually three short, student-centred statements describing observable learning. Choose verbs that fit what students actually do, and align the outcomes with the lesson's available evidence and level of demand.

**Preparation** identifies decisions and work that genuinely need to happen before class. Prioritize the lesson's slideshow, advance reading or setup, and selected printing. Let linked steps handle resources that can be opened while teaching. Make important constraints visible without turning preparation into a full materials inventory.

**Teaching focus** is one clear instructional priority, phrased as useful guidance for what to notice or encourage during the lesson.

**Assessment**, when it adds value, points to evidence already produced through the Teaching Flow: student thinking, discussion, notes, work, or the selected challenge. Keep it brief, formative, and specific to the activity or resource. If Teaching focus already provides enough guidance, leave Assessment out. It is guidance for observing existing work, not an added lesson task.

**Curriculum connections** should reflect actual opportunities in the lesson, using the program's established wording.

## 3. Teaching Flow

The Teaching Flow is a workable classroom sequence, not a script for every moment.

- Keep each step's **number, title, and practical duration**, followed by only the action rows needed to run it. Use a sensible single time estimate where possible; use a range when choices meaningfully change timing.
- Start directions with the teacher's action. Give the essential instruction, then any necessary prompt, resource, or transition.
- Make each row earn its place. A short instruction or one strong discussion question is often enough; additional questions can be linked for teachers who want them.
- Align wording with the actual slideshow and activity resources. Slides provide the student-facing content; the guide tells the teacher what to do with it.
- Respect the lesson's intended choices and pacing. For Small Bites or other alternatives, present clear option labels and enough information to choose and run one path. Follow established lesson-source patterns rather than inventing a new format.
- Use the repository's defined Teaching Flow action labels and row types in [action_labels.json](action_labels.json). Choose labels for their instructional meaning; the validator and renderer own the allowable values and formatting.
- Keep any significant slide-continuity instruction, reading or listening alternative, and classroom transition clear. Verify slide references against the current lesson-specific deck under the source rules in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md).

Preserve a clear distinction between **core teaching steps**, **choices**, and **optional extensions**. Make the default path easy to follow without burying useful alternatives.

## 4. Resources and preparation links

Resource links should help a teacher reach the right material at the moment it is needed.

- Use the approved resource identities and destinations in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md) and the catalogue. Resource titles should match their linked materials.
- Pair a linked title with a short functional description when it helps: for example, a reading, printable student page, question bank, or teacher reference. The renderer owns link typography and visual presentation.
- Place advance-review and setup resources in Preparation; place activity-specific readings, handouts, media alternatives, and supporting references at their Teaching Flow steps.
- Keep full chapters, extended questions, answer keys, student materials, and detailed activity instructions in their own resources. Link to them from the relevant lesson step.
- Refer to the current printing workflow in [content/AGENTS.md](../content/AGENTS.md) for how linked worksheets and options feed the Print Pack Builder.
- Treat a slideshow as the lesson's teaching companion: note what the teacher needs to show or play, while relying on the slide itself for visual and student-facing explanation.

Use concise resource descriptions consistently across the guide. Check whether a teacher can locate every necessary item without searching through unrelated sections.

## 5. Activities, choices, and companion material

Little Chewz lessons offer teacher choice while maintaining the same learning purpose. Make choices understandable without presenting every possible extension as required work.

For each activity, provide its purpose through the surrounding lesson context, then its classroom action, timing, and materials at the level the teacher needs. Where an option has substantial setup or specialized instructions, link the relevant teacher companion rather than expanding the core flow.

Use existing [companion guidance](RESOURCE_GUIDELINES.md) and comparable approved resources for question sets, activity guides, answer keys, and option overviews. The Teacher Guide provides the route; companion materials provide the depth.

Optional extensions should be inviting, clearly additional, and relevant to the lesson goal. Choose a few valuable options over a long catalogue of ideas.

## 6. Story, read-alouds, and excerpts

The Chewlandia story is part of the learning experience. Preserve approved narration, dialogue, lore, and character intent when using an excerpt.

A short, purposeful read-aloud can appear in the Teaching Flow when it helps a teacher lead the moment. Longer readings belong in a linked source. Use the existing guide's passage treatment and preserve natural paragraph breaks; the renderer handles its visual style.

Teacher prompts should invite observation, evidence, curiosity, interpretation, perspective-taking, and reflection as appropriate to the lesson. They should draw on information students have encountered rather than imply a predetermined answer.

## 7. Final editorial check

Read the lesson once as a teacher preparing and once as a teacher delivering it. Check that:

- The goal, outcomes, focus, and Teaching Flow describe the same learning experience.
- Preparation makes the necessary decisions and setup apparent.
- The main route is easy to scan, with concise, actionable steps and useful timings.
- Resource links, slide references, choices, and supporting materials are positioned where a teacher needs them.
- Story details and approved language remain accurate.
- Optional assessment adds practical evidence guidance, and extensions remain optional.
- The resulting page feels consistent with the current Teacher Guides and **Full Guide Revised.pdf**.

For schema validation, PDF checks, review copies, and release safeguards, follow [WORKFLOW.md](WORKFLOW.md) and [PUBLISH.md](PUBLISH.md). Rendering and objective checks belong in code; this guide supplies the human editorial standard.
