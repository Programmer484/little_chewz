import { useEffect, useId, useRef, useState } from "react";
import { LIMITS } from "../../shared/limits.ts";
import { computePlan, describeLine } from "../../shared/plan.ts";
import type { PlanLine, PrintOptions, Quantities, ResolvedExtension, ResolvedLesson, ResolvedMaterial, Selection } from "../../shared/types.ts";
import { MaterialList } from "../components/MaterialList.tsx";
import { NumberField, toWhole } from "../components/NumberField.tsx";
import type { Progress } from "../lib/packet.ts";
import { loadPrefs, savePrefs } from "../lib/prefs.ts";
import { navigate } from "../lib/route.ts";
import { lessonState } from "./LessonList.tsx";

type Status =
  | { kind: "idle" }
  | { kind: "working"; progress: Progress | null }
  | { kind: "done"; sheets: number; blanks: number; duplex: boolean; filename: string }
  | { kind: "failed"; message: string };

type SetSelection = (f: (s: Selection) => Selection) => void;

const validWhole = (n: number, min: number, max: number) => Number.isInteger(n) && n >= min && n <= max;

/** "4 per group" or "4–5 per group". */
function perGroup(students: number, groups: number) {
  const low = Math.floor(students / groups);
  const high = Math.ceil(students / groups);
  return low === high ? `${low} per group` : `${low}–${high} per group`;
}

export function LessonBuilder({ lesson }: { lesson: ResolvedLesson }) {
  const [prefs] = useState(() => loadPrefs());
  const [selection, setSelection] = useState<Selection>({ options: {}, extensions: {} });
  const [students, setStudents] = useState(String(prefs.studentCount ?? lesson.defaults.studentCount));
  const [groups, setGroups] = useState<Record<string, string>>({});
  const [copies, setCopies] = useState<Record<string, string>>({});
  const [print, setPrint] = useState<PrintOptions>({ duplex: prefs.duplex });
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const [showErrors, setShowErrors] = useState(false);
  const abort = useRef<AbortController | null>(null);

  const quantities: Quantities = {
    studentCount: toWhole(students),
    groups: Object.fromEntries(Object.entries(groups).map(([k, v]) => [k, toWhole(v)])),
    copies: Object.fromEntries(Object.entries(copies).filter(([, v]) => v.trim() !== "").map(([k, v]) => [k, toWhole(v)])),
  };
  const plan = computePlan(lesson, selection, quantities);
  const studentsOk = validWhole(quantities.studentCount, LIMITS.minStudents, LIMITS.maxStudents);
  const groupActivities = [...new Map(plan.lines.filter((l) => l.rule === "per_group").map((l) => [l.activityId, l])).values()];

  // Remember class size and print settings on this device.
  useEffect(() => {
    const studentCount = toWhole(students);
    savePrefs({ ...print, ...(validWhole(studentCount, LIMITS.minStudents, LIMITS.maxStudents) ? { studentCount } : {}) });
  }, [students, print]);

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
      setStatus({ kind: "done", sheets: packet.sheetCount, blanks: packet.blankPages, duplex: print.duplex, filename });
    } catch (e) {
      setStatus({ kind: "failed", message: e instanceof Error ? e.message : "Something went wrong building the pack." });
    }
  };

  const tick = (key: "options" | "extensions", id: string, checked: boolean) =>
    setSelection((s) => ({ ...s, [key]: { ...s[key], [id]: checked } }));

  return (
    <section className="panel">
      <BackToLessons />
      <p className="eyebrow">{lesson.questTitle}</p>
      <h1>{lesson.title}</h1>

      <form
        noValidate
        onSubmit={(e) => {
          e.preventDefault();
          void download();
        }}
      >
        <h2>Activities</h2>
        {lesson.sections.map((section, i) => {
          // A step's optional extras sit under the same heading as its worksheets.
          const repeat = i > 0 && lesson.sections[i - 1].title === section.title;
          const className = `section${repeat ? " continued" : ""}`;
          const legend = <legend className={repeat ? "visually-hidden" : undefined}>{section.title}</legend>;
          if (section.kind === "core")
            return (
              <fieldset key={section.id} className={className}>
                {legend}
                <div className="options">
                  {section.materials.map((material) => (
                    <CoreCheckbox key={material.resourceId} sectionId={section.id} material={material}
                      selection={selection} setSelection={setSelection} />
                  ))}
                </div>
              </fieldset>
            );
          if (section.kind === "choice")
            return (
              <fieldset key={section.id} className={className}>
                {legend}
                <div className="options">
                  {section.options.map((option) => {
                    const checked = Boolean(selection.options[option.id]);
                    return (
                      <div key={option.id} className={`option${checked ? " selected" : ""}`}>
                        <label className="option-label">
                          <input type="checkbox" checked={checked} onChange={(e) => tick("options", option.id, e.target.checked)} />
                          <span className="option-letter">{option.label}</span>
                          <span className="option-title">{option.title}</span>
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
                        {!checked && option.extensions.length > 0 && (
                          <p className="option-summary">+ Optional: {option.extensions.map((ext) => ext.title).join(", ")}</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </fieldset>
            );
          return (
            <fieldset key={section.id} className={className}>
              {legend}
              <div className="options">
                {section.items.map((item) => (
                  <ExtensionCheckbox key={item.id} ext={item} selection={selection} setSelection={setSelection} />
                ))}
              </div>
            </fieldset>
          );
        })}

        <h2>Copies</h2>
        <div className="fields">
          <NumberField
            label="Number of students"
            value={students}
            onChange={setStudents}
            min={LIMITS.minStudents}
            max={LIMITS.maxStudents}
            error={showErrors && !studentsOk ? `Enter a whole number from ${LIMITS.minStudents} to ${LIMITS.maxStudents}.` : undefined}
          />
          {groupActivities.map((line) => {
            const value = groups[line.activityId] ?? (Number.isFinite(line.groups) ? String(line.groups) : "");
            const n = toWhole(value);
            return (
              <NumberField
                key={line.activityId}
                label={`Groups for ${line.sources[0]}`}
                hint={studentsOk && validWhole(n, 1, LIMITS.maxGroups) ? perGroup(quantities.studentCount, n) : undefined}
                value={value}
                onChange={(v) => setGroups((previous) => ({ ...previous, [line.activityId]: v }))}
                min={1}
                max={LIMITS.maxGroups}
                error={showErrors && !validWhole(n, 1, LIMITS.maxGroups) ? `Enter 1 to ${LIMITS.maxGroups}.` : undefined}
              />
            );
          })}
        </div>

        {plan.lines.length > 0 && (
          <table className="review">
            <caption className="visually-hidden">Copies of each worksheet</caption>
            <thead>
              <tr>
                <th scope="col">Worksheet</th>
                <th scope="col" className="num">Copies</th>
              </tr>
            </thead>
            <tbody>
              {plan.lines.map((line) => (
                <CopiesRow
                  key={line.id}
                  line={line}
                  raw={copies[line.id]}
                  showErrors={showErrors}
                  onChange={(v) => setCopies((c) => ({ ...c, [line.id]: v }))}
                  onReset={() =>
                    setCopies((c) => {
                      const next = { ...c };
                      delete next[line.id];
                      return next;
                    })
                  }
                />
              ))}
            </tbody>
          </table>
        )}

        <fieldset className="section print-options">
          <legend>Printing</legend>
          <label className="option option-label">
            <input type="checkbox" checked={print.duplex} onChange={(e) => setPrint({ duplex: e.target.checked })} />
            <span className="option-text">
              <span className="option-title">Print double-sided</span>
              <span className="option-summary block">
                Each student's packet starts on a new sheet. Set your printer to two-sided, flip on long edge.
              </span>
            </span>
          </label>
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
        {plan.warnings.length > 0 && (
          <div className="notice" role="status">
            {plan.warnings.length === 1 ? plan.warnings[0] : (
              <ul>{plan.warnings.map((w) => <li key={w}>{w}</li>)}</ul>
            )}{" "}
            You can still download.
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
          <button type="submit" className="button primary" disabled={status.kind === "working"}>
            {status.kind === "working" ? "Preparing…" : "Download Print Pack"}
          </button>
        </div>
        <div aria-live="polite" className="status">
          {status.kind === "working" && <ProgressLine progress={status.progress} />}
          {status.kind === "done" && (
            <div className="success">
              <p>
                Downloaded {status.filename}: {status.sheets} {status.sheets === 1 ? "sheet" : "sheets"} of paper.
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
    </section>
  );
}

function CopiesRow(props: {
  line: PlanLine;
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
          aria-describedby={`${id}-rule`}
          onChange={(e) => props.onChange(e.target.value)}
        />
        <span className="row-sources" id={`${id}-rule`}>{describeLine(line)}</span>
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

/** A core worksheet: ticked by default, untick to leave it out (for example, already printed). */
function CoreCheckbox({ sectionId, material, selection, setSelection }: {
  sectionId: string;
  material: ResolvedMaterial;
  selection: Selection;
  setSelection: SetSelection;
}) {
  const key = `${sectionId}:${material.resourceId}`;
  const checked = selection.core?.[key] !== false;
  return (
    <label className={`option option-label${checked ? " selected" : ""}`}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => setSelection((s) => ({ ...s, core: { ...s.core, [key]: e.target.checked } }))}
      />
      <span className="option-text">
        <span className="option-title">{material.resource.title}</span>
        {material.note && <span className="option-summary block">{material.note}</span>}
        {!material.resource.available && (
          <span className="option-summary block">{material.resource.reason ?? "Not available yet."}</span>
        )}
      </span>
    </label>
  );
}

function ExtensionCheckbox({ ext, selection, setSelection }: {
  ext: ResolvedExtension;
  selection: Selection;
  setSelection: SetSelection;
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
