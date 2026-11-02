export const STEPS = ["Activities", "Copies & download"] as const;
export type StepIndex = 0 | 1;

export function Steps({ current }: { current: StepIndex }) {
  return (
    <ol className="steps" aria-label="Progress">
      {STEPS.map((label, i) => (
        <li key={label} className={i === current ? "current" : i < current ? "done" : ""} aria-current={i === current ? "step" : undefined}>
          <span className="step-num">{i < current ? "✓" : i + 1}</span> {label}
        </li>
      ))}
    </ol>
  );
}
