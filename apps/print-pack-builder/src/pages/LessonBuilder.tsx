import { useMemo, useRef, useState } from "react";
import { LIMITS } from "../../shared/limits.ts";
import { computePlan, describeLine, quantityProblems as checkQuantities, selectedMaterials } from "../../shared/plan.ts";
import type { Quantities, ResolvedExtension, ResolvedLesson, Selection } from "../../shared/types.ts";
import { MaterialList } from "../components/MaterialList.tsx";
import { NumberField, toWhole } from "../components/NumberField.tsx";
import { type StepIndex, Steps } from "../components/Steps.tsx";
import type { Progress } from "../lib/packet.ts";
import { navigate } from "../lib/route.ts";
import { lessonState } from "./LessonList.tsx";

type Status =
  | { kind: "idle" }
  | { kind: "working"; progress: Progress | null }
  | { kind: "done"; pages: number; filename: string }
  | { kind: "failed"; message: string };

export function LessonBuilder({ lesson }: { lesson: ResolvedLesson }) {
  const [step, setStep] = useState<StepIndex>(0);
  const [selection, setSelection] = useState<Selection>({ choices: {}, extensions: {} });
  const [students, setStudents] = useState(String(lesson.defaults.studentCount));
  const [groupSize, setGroupSize] = useState(String(lesson.defaults.groupSize));
  const [adjusted, setAdjusted] = useState<Record<string, string>>({});
  const [extra, setExtra] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const [showErrors, setShowErrors] = useState(false);
  const abort = useRef<AbortController | null>(null);
  const heading = useRef<HTMLHeadingElement>(null);

  const picks = useMemo(() => selectedMaterials(lesson, selection), [lesson, selection]);
  const usesGroups = picks.picks.some((p) => p.material.quantity.rule === "per_group");
  const adjustable = picks.picks
    .map((p) => p.material)
    .filter((m, i, all) => m.quantity.rule === "teacher_adjustable" && all.findIndex((x) => x.resourceId === m.resourceId) === i);

  const quantities: Quantities = {
    studentCount: toWhole(students),
    groupSize: usesGroups ? toWhole(groupSize) : lesson.defaults.groupSize,
    adjusted: Object.fromEntries(Object.entries(adjusted).map(([k, v]) => [k, toWhole(v)])),
    extra: Object.fromEntries(Object.entries(extra).filter(([, v]) => v.trim() !== "").map(([k, v]) => [k, toWhole(v)])),
  };
  const plan = computePlan(lesson, selection, quantities);

  const go = (next: StepIndex) => {
    setStep(next);
    setShowErrors(false);
    setStatus({ kind: "idle" });
    requestAnimationFrame(() => heading.current?.focus());
  };

  const state = lessonState(lesson);
  if (lesson.status !== "ready" || !lesson.printable)
    return (
      <section className="panel">
        <BackToLessons />
        <p className="eyebrow">{lesson.questTitle}</p>
        <h1>{lesson.title}</h1>
        <p className={`status-line tone-${state.tone}`}>{state.label}</p>
        <p>
          {lesson.statusNote ??
            "The student worksheets for this lesson are still being reviewed for the pilot, so there is nothing to download yet."}
        </p>
      </section>
    );

  const download = async () => {
    abort.current?.abort();
    const controller = new AbortController();
    abort.current = controller;
    setStatus({ kind: "working", progress: null });
    try {
      // pdf-lib loads only when a teacher downloads, keeping the first screen fast.
      const { buildPacket, packetFilename, saveFile } = await import("../lib/packet.ts");
      const packet = await buildPacket(plan, (progress) => setStatus({ kind: "working", progress }), fetch, controller.signal);
      const filename = packetFilename(lesson.title);
      saveFile(packet.bytes, filename);
      setStatus({ kind: "done", pages: packet.pageCount, filename });
    } catch (e) {
      setStatus({ kind: "failed", message: e instanceof Error ? e.message : "Something went wrong building the pack." });
    }
  };

  const choiceProblems = picks.problems;
  const quantityProblems = checkQuantities(quantities);

  return (
    <section className="panel">
      <BackToLessons />
      <p className="eyebrow">{lesson.questTitle}</p>
      <h1>{lesson.title}</h1>
      <Steps current={step} />

      {step === 0 && (
        <form
          noValidate
          onSubmit={(e) => {
            e.preventDefault();
            if (choiceProblems.length) setShowErrors(true);
            else go(1);
          }}
        >
          <h2 tabIndex={-1} ref={heading}>
            Choose your activities
          </h2>
          {lesson.sections.map((section) => {
            if (section.kind === "core")
              return (
                <div key={section.id} className="section">
                  <h3>{section.title}</h3>
                  <p className="included">
                    <span aria-hidden="true">✓</span> Included automatically
                  </p>
                  <MaterialList materials={section.materials} />
                </div>
              );
            if (section.kind === "choice") {
              const missing = showErrors && !section.options.some((o) => o.id === selection.choices[section.id]);
              return (
                <fieldset key={section.id} className={`section${missing ? " has-error" : ""}`}>
                  <legend>{section.title}</legend>
                  {missing && <p className="field-error">Choose one option.</p>}
                  <div className="options">
                    {section.options.map((option) => {
                      const checked = selection.choices[section.id] === option.id;
                      return (
                        <div key={option.id} className={`option${checked ? " selected" : ""}`}>
                          <label className="option-label">
                            <input
                              type="radio"
                              name={section.id}
                              value={option.id}
                              checked={checked}
                              onChange={() => setSelection((s) => ({ ...s, choices: { ...s.choices, [section.id]: option.id } }))}
                            />
                            <span className="option-letter">{option.label}</span>
                            <span className="option-title">{option.title}</span>
                            {checked && <span className="selected-tag">Selected</span>}
                          </label>
                          {option.summary && <p className="option-summary">{option.summary}</p>}
                          <MaterialList materials={option.materials} />
                          {checked && option.extensions.length > 0 && (
                            <div className="extensions">
                              {option.extensions.map((ext) => (
                                <ExtensionCheckbox key={ext.id} ext={ext} selection={selection} setSelection={setSelection} />
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </fieldset>
              );
            }
            return (
              <fieldset key={section.id} className="section">
                <legend>{section.title}</legend>
                {section.items.map((item) => (
                  <ExtensionCheckbox key={item.id} ext={item} selection={selection} setSelection={setSelection} />
                ))}
              </fieldset>
            );
          })}
          <div className="actions">
            <button type="submit" className="button primary">
              Next: quantities
            </button>
          </div>
        </form>
      )}

      {step === 1 && (
        <form
          noValidate
          onSubmit={(e) => {
            e.preventDefault();
            if (quantityProblems.length) setShowErrors(true);
            else go(2);
          }}
        >
          <h2 tabIndex={-1} ref={heading}>
            Enter your class numbers
          </h2>
          <div className="fields">
            <NumberField
              label="Number of students"
              value={students}
              onChange={setStudents}
              min={LIMITS.minStudents}
              max={LIMITS.maxStudents}
              error={showErrors && !validWhole(quantities.studentCount, LIMITS.minStudents, LIMITS.maxStudents) ? `Enter a whole number from ${LIMITS.minStudents} to ${LIMITS.maxStudents}.` : undefined}
            />
            {usesGroups && (
              <NumberField
                label="Students per group"
                hint={
                  Number.isInteger(quantities.studentCount) && Number.isInteger(quantities.groupSize) && quantities.groupSize > 0
                    ? `${Math.ceil(quantities.studentCount / quantities.groupSize)} groups`
                    : undefined
                }
                value={groupSize}
                onChange={setGroupSize}
                min={LIMITS.minGroupSize}
                max={LIMITS.maxGroupSize}
                error={showErrors && !validWhole(quantities.groupSize, LIMITS.minGroupSize, LIMITS.maxGroupSize) ? `Enter a whole number from ${LIMITS.minGroupSize} to ${LIMITS.maxGroupSize}.` : undefined}
              />
            )}
            {adjustable.map((m) => (
              <NumberField
                key={m.resourceId}
                label={`Copies of ${m.resource.title}`}
                value={adjusted[m.resourceId] ?? String(m.quantity.count ?? 1)}
                onChange={(v) => setAdjusted((a) => ({ ...a, [m.resourceId]: v }))}
                min={0}
                max={LIMITS.maxAdjustedCopies}
              />
            ))}
          </div>
          {plan.lines.length > 0 && (
            <details className="spares">
              <summary>Add spare copies (optional)</summary>
              <div className="fields">
                {plan.lines.map((line) => (
                  <NumberField
                    key={line.resourceId}
                    label={`Extra ${line.cardsPerSheet ? "sheets" : "copies"}: ${line.title}`}
                    value={extra[line.resourceId] ?? ""}
                    onChange={(v) => setExtra((x) => ({ ...x, [line.resourceId]: v }))}
                    min={0}
                    max={LIMITS.maxExtraCopies}
                  />
                ))}
              </div>
            </details>
          )}
          {showErrors && quantityProblems.some((p) => !p.startsWith("Enter a ")) && (
            <ul className="alert" role="alert">
              {quantityProblems.filter((p) => !p.startsWith("Enter a ")).map((p) => (
                <li key={p}>{p}</li>
              ))}
            </ul>
          )}
          <div className="actions">
            <button type="button" className="button" onClick={() => go(0)}>
              Back
            </button>
            <button type="submit" className="button primary">
              Next: review
            </button>
          </div>
        </form>
      )}

      {step === 2 && (
        <div>
          <h2 tabIndex={-1} ref={heading}>
            Review your print pack
          </h2>
          {plan.lines.length > 0 && (
            <table className="review">
              <thead>
                <tr>
                  <th scope="col">Resource</th>
                  <th scope="col">For</th>
                  <th scope="col" className="num">
                    Copies
                  </th>
                </tr>
              </thead>
              <tbody>
                {plan.lines.map((line) => (
                  <tr key={line.resourceId}>
                    <th scope="row">
                      {line.title}
                      <span className="row-sources">{line.sources.join(", ")}</span>
                    </th>
                    <td>
                      {describeLine(line, quantities, plan.groupCount)}
                      {line.extra > 0 && ` + ${line.extra} spare`}
                    </td>
                    <td className="num">
                      {line.copies} {line.cardsPerSheet ? (line.copies === 1 ? "sheet" : "sheets") : line.copies === 1 ? "copy" : "copies"}
                    </td>
                  </tr>
                ))}
              </tbody>
              {plan.totalPages !== null && (
                <tfoot>
                  <tr>
                    <th scope="row" colSpan={2}>
                      Total pages
                    </th>
                    <td className="num">{plan.totalPages}</td>
                  </tr>
                </tfoot>
              )}
            </table>
          )}
          {plan.unavailable.length > 0 && (
            <div className="notice" role="note">
              <strong>Not included in this pack:</strong>
              <ul>
                {plan.unavailable.map((u) => (
                  <li key={u.resourceId}>
                    {u.title} ({u.sources.join(", ")}): {u.reason}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {plan.problems.length > 0 && (
            <ul className="alert" role="alert">
              {plan.problems.map((p) => (
                <li key={p}>{p}</li>
              ))}
            </ul>
          )}
          <div className="actions">
            <button type="button" className="button" onClick={() => go(1)} disabled={status.kind === "working"}>
              Back
            </button>
            <button type="button" className="button" onClick={() => go(0)} disabled={status.kind === "working"}>
              Change activities
            </button>
            <button
              type="button"
              className="button primary"
              onClick={download}
              disabled={plan.problems.length > 0 || status.kind === "working"}
            >
              {status.kind === "working" ? "Preparing…" : "Download Print Pack"}
            </button>
          </div>
          <div aria-live="polite" className="status">
            {status.kind === "working" && <ProgressLine progress={status.progress} />}
            {status.kind === "done" && (
              <p className="success">
                Downloaded {status.filename} ({status.pages} pages).
              </p>
            )}
          </div>
          {status.kind === "failed" && (
            <p className="alert" role="alert">
              The print pack was not downloaded. {status.message}
            </p>
          )}
        </div>
      )}
    </section>
  );
}

const validWhole = (n: number, min: number, max: number) => Number.isInteger(n) && n >= min && n <= max;

function ProgressLine({ progress }: { progress: Progress | null }) {
  if (!progress) return <p>Starting…</p>;
  const verb = progress.stage === "fetching" ? "Getting" : "Combining";
  const n = Math.min(progress.done + 1, progress.total);
  return (
    <p>
      {progress.title ? `${verb} ${progress.title} (${n} of ${progress.total})…` : "Saving your PDF…"}
    </p>
  );
}

function ExtensionCheckbox({
  ext,
  selection,
  setSelection,
}: {
  ext: ResolvedExtension;
  selection: Selection;
  setSelection: (f: (s: Selection) => Selection) => void;
}) {
  const checked = Boolean(selection.extensions[ext.id]);
  return (
    <div className={`extension${checked ? " selected" : ""}`}>
      <label className="option-label">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => setSelection((s) => ({ ...s, extensions: { ...s.extensions, [ext.id]: e.target.checked } }))}
        />
        <span className="option-title">{ext.title}</span>
        {checked && <span className="selected-tag">Added</span>}
      </label>
      {ext.summary && <p className="option-summary">{ext.summary}</p>}
      <MaterialList materials={ext.materials} />
    </div>
  );
}

function BackToLessons() {
  return (
    <a
      className="back"
      href="/"
      onClick={(e) => {
        e.preventDefault();
        navigate("/");
      }}
    >
      ← All lessons
    </a>
  );
}
