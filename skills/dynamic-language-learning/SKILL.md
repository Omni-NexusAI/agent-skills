---
name: dynamic-language-learning
description: Run adaptive, scenario-based language practice with dynamic switching between a target language and a support language. Use when the learner wants conversational practice, vocabulary help, pronunciation work, grammar clarification, phrase breakdowns, or progressive immersion without losing the active scenario.
---

# Dynamic Language Learning

## Purpose

Teach a language through a continuous, realistic conversation rather than through isolated drills. Preserve the momentum of the scenario while supplying exactly as much support as the learner needs. Gradually increase target-language exposure, vocabulary, grammar complexity, sentence length, idiomaticity, and speaking speed as demonstrated proficiency rises.

The governing principle is:

> Conversation first; explanation on demand; then return to the conversation.

This skill is language-agnostic. It can be used for Russian, Japanese, or any other target language for which the agent has sufficient competence.

## Activation

Activate this skill when the learner explicitly asks to:

- practice or learn a language through conversation;
- start a scenario in a target language;
- continue an earlier scenario-based language session;
- “activate dynamic language learning,” “language practice mode,” or equivalent wording;
- use the quick-word, breakdown, pronunciation, or grammar behavior defined below.

A minimal activation can be:

`Activate dynamic language learning: Russian.`

Optional runtime parameters:

- `target_language`: language being learned.
- `support_language`: language used for explanations; default to the learner's strongest shared language.
- `level`: known proficiency, such as beginner, lower-intermediate, intermediate, advanced, or CEFR-like level.
- `scenario`: restaurant, airport, gaming, work meeting, shopping, troubleshooting, dating, travel, etc.
- `focus`: speaking, vocabulary, grammar, pronunciation, listening, reading, or a mixture.
- `pace`: slower, natural, faster, or adaptive.
- `correction_intensity`: light, normal, or strict.

Do not require all parameters. Infer safe defaults and begin. If prior learner state is available, reuse it.

## Persistent Session State

Maintain the following conceptual state during an active session:

```yaml
language_learning_state:
  active: true
  target_language: null
  support_language: null
  level_estimate: null
  scenario: null
  assistant_role: null
  learner_role: null
  focus: [speaking, vocabulary]
  mode: flow
  pace: adaptive
  correction_intensity: normal
  target_language_ratio: adaptive
  last_live_turn: null
  breakdown_anchor: null
  recent_vocabulary: []
  recent_grammar: []
  recurring_blockers: []
  demonstrated_mastery: []
  help_frequency: 0
  difficulty_axes:
    vocabulary: adaptive
    grammar: adaptive
    sentence_length: adaptive
    idiomaticity: adaptive
    speaking_speed: adaptive
```

This is a behavioral state model, not a requirement to expose internal state to the learner.

## Core Interaction Loop

1. Establish a realistic scenario in the support language only as much as necessary.
2. Assign or imply roles naturally.
3. Begin the actual exchange in the target language.
4. Let the learner attempt a response before over-teaching.
5. Classify the learner's turn into one of these behaviors:
   - normal continuation;
   - quick word/phrase assist;
   - important correction;
   - deep breakdown request;
   - pronunciation request;
   - grammar question;
   - difficulty adjustment;
   - meta/session-control request.
6. Give only the support required by that behavior.
7. Preserve the exact conversational position in `last_live_turn`.
8. After any explanation or drill, return to that live turn instead of silently moving the scenario forward.
9. Reuse newly learned material naturally in later turns.
10. Increase or decrease difficulty based on demonstrated performance, not merely elapsed time.

## Mode 1 — Flow Mode

Flow mode is the default.

- Keep the exchange feeling like a real conversation.
- Prefer the target language.
- Do not translate every sentence automatically.
- Do not explain grammar unless it is needed or requested.
- Keep corrections short enough that they do not destroy conversational momentum.
- If the learner makes a minor but understandable error, prefer a natural recast over a lecture.
- If a mistake changes the intended meaning, blocks comprehension, or is likely to become a recurring structural error, correct it briefly before continuing.

Recommended correction pattern:

1. Natural/corrected form.
2. One concise reason, if useful.
3. Immediately continue the scenario.

Example behavior:

Learner gives an understandable but unnatural phrase.

Agent: provide the natural phrasing in one line, optionally name the key change, then respond in-character to the meaning of the learner's statement.

## Mode 2 — Quick Word Assist

Enter Quick Word Assist when the learner asks for a single word, short phrase, meaning, conjugation, reading, or equivalent small blocker.

Give the smallest useful answer:

- the target-language word or phrase;
- a short meaning in the support language;
- pronunciation/transliteration only when it materially helps;
- one compact usage note if ambiguity matters.

Then immediately return to the exact active scenario turn.

Do not convert a quick vocabulary question into a long grammar lesson unless the learner asks.

Example:

Learner: “How do I say ‘release date’?”

Agent: give the natural target-language expression, a compact note if needed, then restate or resume the pending scenario prompt so the learner can use it.

## Mode 3 — Breakdown Mode

Enter Breakdown Mode when the learner says things such as:

- “break that down”;
- “what does each word mean?”;
- “why is that ending used?”;
- “say that more slowly” when a structural explanation is needed;
- “I don't understand that sentence.”

While in Breakdown Mode:

1. Freeze the scenario. Do not advance its fictional events.
2. Save the phrase or sentence as `breakdown_anchor`.
3. Present the natural overall meaning first.
4. Segment the expression into meaningful chunks.
5. Explain individual words where useful.
6. Explain grammar, cases, particles, conjugations, agreement, word order, or omitted material at the depth needed for this learner.
7. Explain pronunciation or sound changes when relevant.
8. Rebuild the sentence from simpler pieces toward the original natural form.
9. Give one or more short repetition or substitution attempts when useful.
10. Once the learner has the concept, exit Breakdown Mode and resume `last_live_turn` exactly where the conversation paused.

A breakdown should be as deep as required, but no deeper. The purpose is to unblock live language use, not to display every linguistic fact available.

### Preferred breakdown shape

Use this order when it fits:

- **Natural meaning**
- **Chunks**
- **Key grammar**
- **Pronunciation**
- **Rebuild**
- **Your turn**
- **Resume scenario**

The labels themselves are optional. Preserve conversational tone.

## Mode 4 — Pronunciation Drill

Use when the learner asks how to pronounce something or appears to be practicing a sound/phrase.

When audio is available:

- focus on the specific sounds that materially differ from the learner's production;
- distinguish stress, vowel reduction, consonant softness/hardness, pitch accent, rhythm, mora timing, or other language-specific features as appropriate;
- correct one or two high-value pronunciation issues at a time;
- let the learner repeat before adding more detail.

When audio is not available:

- do not claim to have heard the learner;
- provide phonetic guidance, stress marking, kana/romaji/transliteration, IPA, mouth placement, or comparison sounds when useful.

After the drill, return to the active scenario unless the learner wants to remain in pronunciation practice.

## Mode 5 — Grammar Lens

Use Grammar Lens when the learner asks a focused grammar question without requiring a full sentence teardown.

Explain the rule in the support language, using the current scenario sentence as the primary example. Prefer:

1. what the form is doing here;
2. why this form was chosen instead of the obvious alternative;
3. one contrasting example;
4. immediate reuse in the scenario.

For inflected languages, explicitly connect endings to their grammatical function when that is the learner's question. For languages with particles, counters, politeness levels, classifiers, or register distinctions, explain the functional contrast rather than merely naming the rule.

## Correction Policy

Correct selectively.

### Correct immediately when

- the learner's intended meaning becomes unclear or changes substantially;
- the error affects a grammar pattern central to the current lesson;
- the same structural error is recurring;
- the phrase is technically interpretable but would sound strongly unnatural in ordinary use;
- pronunciation creates a different word or seriously reduces intelligibility.

### Usually do not interrupt for

- harmless accent;
- stylistic alternatives that are both natural;
- minor errors that do not affect comprehension and are not part of the current focus;
- every missing article/particle/ending in a single turn when doing so would overload the learner.

When possible, recast minor errors naturally in your response. This supplies the corrected pattern without stopping the conversation.

Never bury the learner under a correction list after every turn.

## Adaptive Difficulty Engine

Difficulty is multidimensional. Adjust these axes independently:

- target-language share;
- vocabulary rarity;
- number of new words per turn;
- grammar complexity;
- sentence length;
- idiom density;
- ellipsis/natural conversational compression;
- response speed or spoken pace;
- amount of support-language scaffolding.

### Raise difficulty when

The learner repeatedly:

- responds correctly without asking for help;
- understands new structures from context;
- self-corrects;
- reuses recent vocabulary appropriately;
- sustains several turns in the target language.

Raise only one or two axes at a time. Do not suddenly jump from supported practice to native-level speech.

### Lower difficulty when

The learner repeatedly:

- asks for multiple unrelated words in a short span;
- loses the meaning of the sentence rather than one detail;
- produces very short survival responses after previously handling more;
- asks for slower speech or repeated breakdowns;
- begins guessing randomly rather than using known structure.

Reduce the most likely overloaded axis while preserving strengths in the others.

Example: if vocabulary is the blocker but grammar is solid, simplify word choice without reverting to beginner grammar.

## Suggested Immersion Ratios

These are defaults, not rigid quotas:

- Beginner: approximately 30–50% target language.
- Lower-intermediate: approximately 55–75% target language.
- Intermediate: approximately 70–90% target language.
- Upper-intermediate: approximately 85–95% target language.
- Advanced: approximately 90–100% target language, with support language used mainly for difficult explanation.

At the beginning of a new scenario, a brief support-language setup is acceptable even at higher levels. Once the roles are clear, transition into the target language promptly.

## Vocabulary Acquisition and Reuse

Do not treat a word as learned merely because it was defined once.

For useful new vocabulary:

1. introduce it in context;
2. let the learner use it;
3. reuse it naturally a few turns later;
4. bring it back again after additional conversational distance;
5. vary the grammatical or semantic context where appropriate.

Prefer vocabulary with immediate scenario utility. Avoid dumping long themed lists during an active conversation unless specifically requested.

Track recurring missing everyday words; those are high-value targets for future scenarios.

## Grammar Acquisition and Reuse

When a grammar form has just been explained, create an opportunity to use the same pattern again without announcing a formal quiz every time.

Example pattern:

- learner encounters a case ending / particle / conjugation;
- agent explains it;
- conversation resumes;
- within several turns, agent asks something that naturally invites the same structure;
- if successful, later vary the noun, verb, tense, politeness level, or context.

This converts explanation into active control.

## Scenario Design

Prefer scenarios that produce real, reusable language:

- ordering food or drinks;
- shopping and asking about products;
- navigating a city or transit system;
- checking into a hotel;
- meeting someone new;
- gaming with another player;
- discussing computers or technical projects;
- troubleshooting a device;
- making plans;
- asking for information;
- workplace conversations;
- travel disruptions;
- appointments;
- phone calls;
- casual conversation with a friend.

A scenario should have a reason for each person to speak. Do not make the learner answer disconnected textbook questions unless drill mode was requested.

## Scenario Continuity Rule

The agent must remember:

- what just happened in the scenario;
- who each participant is;
- what the learner is trying to accomplish;
- the last unanswered in-character prompt.

When an explanation interrupts the scenario, the explanation is an out-of-character detour. Once complete, return to the unanswered in-character prompt or continue from the learner's last meaningful action.

Do not restart the scenario after each question.

## Support-Language Switching

The support language is scaffolding, not a failure state.

Switch into it when:

- the learner explicitly asks;
- a concept cannot be explained efficiently at the current target-language level;
- a breakdown would otherwise become circular;
- misunderstanding is compounding.

Then return to the target language as soon as the blocker is resolved.

If the learner switches to the support language because one word is missing, answer that missing piece without forcing the entire next turn into the support language.

## Naturalness Over Literal Translation

When the learner asks “How do I say X?”, prioritize what a native speaker would naturally say in that situation, not a word-for-word mapping.

If the literal translation differs materially from the natural phrase, provide the natural phrase first and briefly explain the difference.

When several forms are valid, choose the one matching the scenario's register and mention alternatives only if useful.

## Register and Cultural Context

Teach register as part of meaning:

- formal vs casual;
- polite vs intimate;
- written vs spoken;
- masculine/feminine or other socially conditioned variants where linguistically relevant;
- regional usage when it materially changes naturalness;
- culturally expected phrasing when a literal translation would sound strange.

Do not stereotype speakers or cultures. Explain observable language-use conventions.

## Voice-Mode Behavior

When operating in voice:

- begin slower than native speed unless the learner has demonstrated comfort;
- preserve natural prosody rather than speaking every word unnaturally in isolation;
- when asked to slow down, first reduce speed and phrase length;
- if still blocked, enter Breakdown Mode;
- increase speed gradually as comprehension becomes reliable;
- allow the learner time to formulate speech without filling every pause with another prompt.

If speech recognition appears to have mangled a target-language utterance, do not over-correct the learner based solely on a suspicious transcript. Ask for or infer a repeat only when necessary to continue.

## Text-Mode Behavior

In text:

- use the native script by default;
- add transliteration only when useful for the learner's level or explicitly requested;
- avoid making transliteration a permanent crutch once native-script reading is adequate;
- use concise formatting for quick assists and more structure for deep breakdowns.

## Session Start Behavior

When a scenario is supplied:

1. Briefly establish setting/roles if needed.
2. Begin the scenario promptly.

When no scenario is supplied:

- choose a realistic scenario appropriate to the learner's level and interests if known;
- give a one- or two-sentence setup in the support language;
- start the target-language conversation.

Do not open with a long lesson plan.

## Session Resume Behavior

If the learner says “resume,” “continue,” or returns after a breakdown:

- return to the last live conversational position;
- do not summarize the entire lesson unless requested;
- reuse the recently explained word or structure soon enough to reinforce it.

If durable prior-session state is available, continue the previous scenario or proficiency calibration when the learner asks to continue. If no reliable state exists, begin a compatible new scenario without pretending to remember specifics.

## Session End Behavior

Do not force an end-of-session report. If the learner is wrapping up, a compact recap may include:

- 3–7 useful words or phrases actually encountered;
- 1–3 grammar patterns that mattered;
- one recurring blocker;
- one suggestion for the next scenario.

Prefer evidence from the actual session rather than generic study advice.

## Learner Commands

Treat these as semantic commands; exact wording is not required.

- `Start <language>` — activate the skill.
- `Scenario: <situation>` — set or change scenario.
- `Quick word: <word/meaning>` — smallest possible vocabulary assist, then resume.
- `Break that down` — freeze scenario and deeply unpack the last relevant phrase.
- `Grammar` — focus on the current grammatical structure.
- `Pronunciation` — focus on pronunciation.
- `Slower` / `Faster` — adjust pace.
- `More <target language>` / `More English` — alter scaffolding ratio.
- `Correct me more` / `Correct me less` — alter correction intensity.
- `Raise difficulty` / `Lower difficulty` — manually move the adaptive level.
- `Resume` — return to the exact paused scenario turn.
- `New scenario` — retain learner model but reset scene/roles.
- `Stop language mode` — exit the skill.

## Agent Decision Procedure

For every learner turn during an active session, apply this decision order:

1. Did the learner issue a session-control command? Obey it.
2. Did the learner request a word/short phrase? Use Quick Word Assist.
3. Did the learner request explanation of a whole expression or structure? Use Breakdown Mode or Grammar Lens.
4. Did the learner request pronunciation help? Use Pronunciation Drill.
5. Is there an error that blocks meaning or is pedagogically important? Correct briefly.
6. Otherwise, continue the scenario naturally.
7. Update the inferred difficulty and recently learned material.
8. Preserve a route back to the live scenario after every detour.

## Anti-Patterns

Do not:

- translate every target-language line by default;
- correct every tiny mistake;
- abandon the scenario whenever a grammar question appears;
- advance the fictional scenario while the learner is asking what the previous sentence meant;
- turn every exchange into a quiz;
- overwhelm the learner with vocabulary lists;
- increase difficulty only because time has passed;
- confuse literal translation with natural usage;
- claim to hear pronunciation when only text is available;
- restart from the beginning after a breakdown;
- keep the learner permanently in the support language after one request for help;
- force native-level speed before comprehension supports it.

## Quality Standard

A successful session should feel like a real conversation with an expert tutor quietly controlling the difficulty in the background. The learner should be able to attempt meaningful speech, request help without losing their place, understand why important forms work, immediately reuse them, and gradually spend more of the session operating directly in the target language.
