# Little Chewz — Teacher Guide Editorial Instructions

**Scope:** These instructions apply to AI and editors creating or revising Little Chewz Teacher Guides, including AI working on the generator.

Use existing approved Teacher Guides and teacher companion resources as the editorial baseline. Use the latest approved lesson content and lesson-specific slideshow for instructional accuracy.

This document governs editorial decisions not clearly enforced by code. Source authority, technical requirements, and workflow are defined in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md), [RESOURCE_GUIDELINES.md](RESOURCE_GUIDELINES.md), and [EDIT.md](EDIT.md).

## 1. Primary editorial rule

**Tell teachers only what they need to do next.**

Write concise, practical, classroom-ready instructions consistent with approved guides. Prioritize clarity, usefulness, and ease of scanning. Preserve the established section structure, terminology, instructional approach, and tone.

Include information that helps teachers prepare, make decisions, or deliver the lesson. Use approved guides to judge the appropriate level of detail.

## 2. Learning design: goal, outcomes, focus, and assessment

**Learning goal**
- State the central educational purpose in one concise sentence.
- Describe student learning rather than listing activities.
- Align with the lesson's approved instructional intent.

**Learning outcomes**
- Normally include three short, observable, student-centred statements.
- Begin with meaningful action verbs.
- Reflect learning students can demonstrate through the lesson's actual activities.
- Match the lesson's scope and progression.

**Teaching focus**
- Identify one central instructional priority in a short, direct sentence.
- Give teachers a practical focus while delivering the lesson.
- Complement the outcomes without repeating them.

**Assessment — optional**
- Include assessment when it adds useful guidance beyond Teaching focus.
- Identify observable evidence from activities, discussions, or student materials already in the Teaching Flow.
- For choice-based lessons, tailor indicators to the selected activities.
- Keep guidance formative, concise, and proportionate to the lesson.

Follow approved Teacher Guides for the appropriate depth and use of each section.

## 3. Resources, descriptions, and preparation

**Resource references**
- Use approved resource titles and verified destinations from the resource catalogue.
- Follow the established linked-title and short-description presentation.
- Describe what the resource is for or what the teacher should do with it.
- Place supporting materials in their companion resources and link them where used.
- Verify slide references against the current approved lesson-specific slideshow.

**Preparation**

Preparation covers decisions and actions that need to happen before students arrive.

- Identify meaningful advance reading, setup, printing, materials, and safety considerations.
- Link the approved lesson slideshow and relevant preparation resources.
- Use brief, action-oriented descriptions.
- Place in-class resources at the relevant Teaching Flow steps.
- Keep preparation proportional to the lesson's complexity.

Use the established Core Resources and Print Your Choices structure where applicable.

## 4. Teaching Flow action labels

Use the approved action vocabulary defined in [action_labels.json](action_labels.json).

| Label | Editorial purpose |
| --- | --- |
| **SHOW** | Display slides or slide-based media. |
| **KEEP** | Maintain a slide during a related action. |
| **READ** | Direct a reading or read-aloud. |
| **LISTEN** | Use a standalone audio resource. |
| **ASK** | Present a focused discussion question. |
| **DO** | Give a practical classroom direction. |
| **GIVE** | Direct students to a resource or material. |
| **MORE** | Provide optional supporting resources. |

Choose the label that best describes the teacher's action. Follow established patterns for slide continuity, reading alternatives, and activity choices. Keep labelled instructions brief and purposeful.

## 5. Writing Teaching Flow steps

Follow the structure and instructional style of approved Teacher Guides.

**Step structure**
- Use the established step number, title, duration, and labelled action rows.
- Present actions in classroom sequence.
- Begin instructions with clear, practical verbs.
- Give one meaningful direction per row.
- Use realistic, rounded time estimates.
- Keep steps easy to scan while teaching.

**Instructional content**
- Include the essential information needed to conduct each activity.
- Choose focused discussion questions suited to the learning goal.
- Reference approved slides, readings, student materials, and companion resources at their point of use.
- Maintain a natural progression between activities.
- Let the slideshow and supporting resources carry details already available there.

**Choice-based activities**
- Preserve the established choice structure and presentation.
- Make alternatives easy to distinguish and follow.
- Give each choice the instructions and resources relevant to that activity.
- Refer to approved guides and companion activity resources for the right level of detail.

**Timing and flow**
- Fit activities to the intended lesson duration.
- Balance instructional time across the lesson.
- Clarify transitions when they change what the teacher needs to do.

## 6. Reading passages and excerpts

Use the established Teacher Guide approach to readings and excerpts.

- Include short approved passages where access within the guide supports teaching.
- Link longer readings to their complete resources.
- Preserve approved wording, story details, characters, and terminology.
- Retain meaningful paragraph breaks and selective emphasis.
- Follow existing approved excerpt formatting conventions.

The Teacher Guide supports classroom delivery; companion resources carry fuller material.

## 7. MORE resources and companion materials

Use **MORE** for optional resources that support, extend, or provide alternatives to the main Teaching Flow.

- Place resources beside the activity they support, as the **last** row of that step or option: MORE always comes after every other action row. `scripts/validate.py` enforces this.
- Group related resources for convenient access.
- Use approved resource titles and concise, functional descriptions.
- Distinguish optional resources from the main classroom sequence.
- Link companion materials for detailed instructions, question banks, extensions, and supporting content.

Follow [RESOURCE_GUIDELINES.md](RESOURCE_GUIDELINES.md) and approved companion resources for their editorial content and organization.

## 8. Editorial and engineering responsibilities

**Editorial instructions govern**
- Tone, clarity, and concision.
- Instructional priorities and learning alignment.
- Selection and organization of teaching content.
- Appropriate detail for goals, outcomes, focus, and assessment.
- Practical classroom directions.
- Resource descriptions and editorial consistency.
- Faithfulness to approved learning materials.

**Generator code governs**
- PDF layout, typography, colours, and spacing.
- Rendering and pagination.
- Hyperlinks and resource resolution.
- Supported data structures and technical validation.
- Other requirements explicitly implemented in code.

Use existing source structures and shared rendering conventions. Keep editorial instructions focused on written content and teacher usefulness.

## 9. Editorial review

Before finalizing, confirm that:
- The guide follows established Little Chewz editorial conventions.
- Goals, outcomes, and Teaching focus align with the actual lesson.
- Assessment, when included, identifies useful evidence from existing activities.
- Preparation names meaningful advance requirements.
- Teaching Flow is concise, practical, and easy to follow.
- Instructions and resources appear where teachers need them.
- Choices and alternatives are clear.
- Resource titles, slide references, and supporting content are accurate.
- Approved story details, terminology, and educational intent are preserved.
- The result is consistent with approved Teacher Guides and teacher companion resources.

**Final editorial standard:** A teacher should be able to follow the guide confidently, with enough information to deliver the lesson and minimal unnecessary reading.
