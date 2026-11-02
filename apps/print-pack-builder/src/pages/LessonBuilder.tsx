import { useEffect, useId, useMemo, useRef, useState } from "react";
import { LIMITS } from "../../shared/limits.ts";
import { computePlan, describeLine, quantityProblems as checkQuantities, selectedMaterials } from "../../shared/plan.ts";
import type { PlanLine, PrintOptions, Quantities, ResolvedExtension, ResolvedLesson, Selection } from "../../shared/types.ts";
import { MaterialList } from "../components/MaterialList.tsx";
import { NumberField, toWhole } from "../components/NumberField.tsx";
import { type StepIndex, Steps } from "../components/Steps.tsx";
import type { Progress } from "../lib/packet.ts";
import { loadPrefs, savePrefs } from "../lib/prefs.ts";
import { navigate } from "../lib/route.ts";
import { lessonState } from "./LessonList.tsx";

type Status =
  | { kind: "idle" }
  | { kind: "working"; progress: Progress | null }
  | { kind: "done"; pages: number; sheets: number; blanks: number; duplex: boolean; filename: string }
  | { kind: "failed"; message: string };

const validWhole = (n: number, min: number, max: number) => Number.isInteger(n) && n >= min && n <= max;

export function LessonBuilder({ lesson }: { lesson: ResolvedLesson }) {
  const [prefs] = useState(() => loadPrefs());
  const [step, setStep] = useState<StepIndex>(0);
  const [selection, setSelection] = useState<Selection>({ choices: {}, extensions: {} });
  const [students, setStudents] = useState(String(prefs.studentCount ?? lesson.defaults.studentCount));
  const [groupSize, setGroupSize] = useState(String(prefs.groupSize ?? lesson.defaults.groupSize));
  const [copies, setCopies] = useState<Record<string, string>>({});
  const [print, setPrint] = useState<PrintOptions>({ order: prefs.order, duplex: prefs.duplex });
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const [showErrors, setShowErrors] = useState(false);
  const abort = useRef<AbortController | null>(null);
  const heading = useRef<HTMLHeadingElement>(null);

  const picks = useMemo(() => selectedMaterials(lesson, selection), [lesson, selection]);
  const usesGroups = picks.picks.some((p) => p.material.rule === "per_group");

  const quantities: Quantities = {
    studentCount: toWhole(students),
    groupSize: usesGroups ? toWhole(groupSize) : lesson.defaults.groupSize,
    copies: Object.fromEntries(Object.entries(copies).filter(([, v]) => v.trim() !== "").map(([k, v]) => [k, toWhole(v)])),
  };
  const plan = computePlan(lesson, selection, quantities);
  const numbersOk = checkQuantities({ ...quantities, copies: {} }).length === 0;

  // Remember class size and print settings on this device.
  useEffect(() => {
    const studentCount = toWhole(students);
    const size = toWhole(groupSize);
    savePrefs({
      ...print,
      ...(validWhole(studentCount, LIMITS.minStudents, LIMITS.maxStudents) ? { studentCount } : {}),
      ...(validWhole(size, LIMITS.minGroupSize, LIMITS.maxGroupSize) ? { groupSize: size } : {}),
    });
  }, [students, groupSize, print]);

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
          {lesson.statusNote ?? "The student worksheets for this lesson aren't published yet, so there is nothing to download."}
        </p>
      </section>
    );

  const download = async () => {
    setShowErrors(true);
    if (plan.problems.length) return;
    abort.current?.abort();
    const controller = new AbortController();
    abort.current = controller;
    setStatus({ kind: "working", progress: null });
    try {
      // pdf-lib loads only when a teacher downloads, keeping the first screen fast.
      const { buildPacket, packetFilename, saveFile } = await import("../lib/packet.ts");
      const packet = await buildPacket(plan, print, (progress) => setStatus({ kind: "working", progress }), fetch, controller.signal);
      const filename = packetFilename(lesson.title);
      saveFile(packet.bytes, filename);
      setStatus({ kind: "done", pages: packet.pageCount, sheets: packet.sheetCount, blanks: packet.blankPages, duplex: print.duplex, filename });
    } catch (e) {
      setStatus({ kind: "failed", message: e instanceof Error ? e.message : "Something went wrong building the pack." });
    }
  };

  const choiceProblems = picks.problems;

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
                <div className="options">
                  {section.items.map((item) => (
                    <ExtensionCheckbox key={item.id} ext={item} selection={selection} setSelection={setSelection} />
                  ))}
                </div>
              </fieldset>
            );
          })}
          <div className="actions">
            <button type="submit" className="button primary">
              Next: copies
            </button>
          </div>
        </form>
      )}

      {step === 1 && (
        <form
          noValidate
          onSubmit={(e) => {
            e.preventDefault();
            void download();
          }}
        >
          <h2 tabIndex={-1} ref={heading}>
            Copies and download
          </h2>
          <div className="fields">
            <NumberField
              label="Number of students"
              value={students}
              onChange={setStudents}
              min={LIMITS.minStudents}
              max={LIMITS.maxStudents}
              error={
                showErrors && !validWhole(quantities.studentCount, LIMITS.minStudents, LIMITS.maxStudents)
                  ? `Enter a whole number from ${LIMITS.minStudents} to ${LIMITS.maxStudents}.`
                  : undefined
              }
            />
            {usesGroups && (
              <NumberField
                label="Students per group"
                hint={numbersOk ? `${plan.groupCount} groups` : undefined}
                value={groupSize}
                onChange={setGroupSize}
                min={LIMITS.minGroupSize}
                max={LIMITS.maxGroupSize}
                error={
                  showErrors && !validWhole(quantities.groupSize, LIMITS.minGroupSize, LIMITS.maxGroupSize)
                    ? `Enter a whole number from ${LIMITS.minGroupSize} to ${LIMITS.maxGroupSize}.`
                    : undefined
                }
              />
            )}
          </div>

          {plan.lines.length > 0 && (
            <table className="review">
              <caption className="visually-hidden">Copies of each worksheet</caption>
              <thead>
                <tr>
                  <th scope="col">Worksheet</th>
                  <th scope="col">Suggested</th>
                  <th scope="col" className="num">
                    Copies
                  </th>
                </tr>
              </thead>
              <tbody>
                {plan.lines.map((line) => (
                  <CopiesRow
                    key={line.resourceId}
                    line={line}
                    suggested={numbersOk ? describeLine(line, quantities, plan.groupCount) : "Enter your class numbers"}
                    raw={copies[line.resourceId]}
                    showErrors={showErrors}
                    onChange={(v) => setCopies((c) => ({ ...c, [line.resourceId]: v }))}
                    onReset={() =>
                      setCopies((c) => {
                        const next = { ...c };
                        delete next[line.resourceId];
                        return next;
                      })
                    }
                  />
                ))}
              </tbody>
            </table>
          )}

          <fieldset className="section print-options">
            <legend>Arrange the PDF</legend>
            <div className="options">
              <label className={`option option-label${print.order === "worksheet" ? " selected" : ""}`}>
                <input
                  type="radio"
                  name="order"
                  checked={print.order === "worksheet"}
                  onChange={() => setPrint((p) => ({ ...p, order: "worksheet" }))}
                />
                <span>
                  <span className="option-title">One worksheet at a time</span>
                  <span className="option-summary block">All copies of each worksheet together.</span>
                </span>
              </label>
              <label className={`option option-label${print.order === "student" ? " selected" : ""}`}>
                <input
                  type="radio"
                  name="order"
                  checked={print.order === "student"}
                  onChange={() => setPrint((p) => ({ ...p, order: "student" }))}
                />
                <span>
                  <span className="option-title">Student packets</span>
                  <span className="option-summary block">
                    One of each worksheet per student, in lesson order. Group and class copies come after.
                  </span>
                </span>
              </label>
              <label className={`option option-label${print.duplex ? " selected" : ""}`}>
                <input type="checkbox" checked={print.duplex} onChange={(e) => setPrint((p) => ({ ...p, duplex: e.target.checked }))} />
                <span>
                  <span className="option-title">I'm printing double-sided</span>
                  <span className="option-summary block">
                    Adds blank backs where needed so every worksheet starts on its own sheet.
                  </span>
                </span>
              </label>
            </div>
          </fieldset>

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
          {showErrors && plan.problems.some((p) => !p.startsWith("Enter a ")) && (
            <ul className="alert" role="alert">
              {plan.problems
                .filter((p) => !p.startsWith("Enter a "))
                .map((p) => (
                  <li key={p}>{p}</li>
                ))}
            </ul>
          )}
          <div className="actions">
            <button type="button" className="button" onClick={() => go(0)} disabled={status.kind === "working"}>
              Change activities
            </button>
            <button type="submit" className="button primary" disabled={status.kind === "working"}>
              {status.kind === "working" ? "Preparing…" : "Download Print Pack"}
            </button>
          </div>
          <div aria-live="polite" className="status">
            {status.kind === "working" && <ProgressLine progress={status.progress} />}
            {status.kind === "done" && (
              <div className="success">
                <p>
                  Downloaded {status.filename}: {status.pages} pages
                  {status.duplex ? `, ${status.sheets} sheets double-sided` : ""}.
                </p>
                {status.duplex && (
                  <p className="tip">
                    In the print window, choose <strong>Print on both sides</strong> (flip on long edge).
                    {status.blanks > 0 && ` ${status.blanks} blank backs are included on purpose.`}
                  </p>
                )}
              </div>
            )}
          </div>
          {status.kind === "failed" && (
            <p className="alert" role="alert">
              The print pack was not downloaded. {status.message}
            </p>
          )}
        </form>
      )}
    </section>
  );
}

function CopiesRow(props: {
  line: PlanLine;
  suggested: string;
  raw: string | undefined;
  showErrors: boolean;
  onChange: (value: string) => void;
  onReset: () => void;
}) {
  const id = useId();
  const { line } = props;
  const value = props.raw ?? String(line.defaultCopies);
  const invalid = props.showErrors && !validWhole(toWhole(value), 0, LIMITS.maxCopies);
  return (
    <tr>
      <th scope="row">
        <label htmlFor={id}>{line.title}</label>
        <span className="row-sources">{line.sources.join(", ")}</span>
      </th>
      <td>
        {props.suggested}
        {line.note && <span className="row-sources">Guide: {line.note}</span>}
      </td>
      <td className="num copies-cell">
        <input
          id={id}
          type="number"
          inputMode="numeric"
          min={0}
          max={LIMITS.maxCopies}
          step={1}
          value={value}
          aria-invalid={invalid || undefined}
          onChange={(e) => props.onChange(e.target.value)}
        />
        <span className="unit">{line.cardsPerSheet ? "sheets" : "copies"}</span>
        {line.edited && (
          <button type="button" className="link-button" onClick={props.onReset}>
            Reset to {line.defaultCopies}
          </button>
        )}
        {invalid && (
          <span className="field-error" role="alert">
            0 to {LIMITS.maxCopies}
          </span>
        )}
      </td>
    </tr>
  );
}

function ProgressLine({ progress }: { progress: Progress | null }) {
  if (!progress) return <p>Starting…</p>;
  const verb = progress.stage === "fetching" ? "Getting" : "Combining";
  const n = Math.min(progress.done + 1, progress.total);
  return <p>{progress.title ? `${verb} ${progress.title} (${n} of ${progress.total})…` : "Saving your PDF…"}</p>;
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
      <MaterialList materials={ext.materials.filter((m) => m.resource.title !== ext.title || !m.resource.available)} />
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
