import { useId } from "react";

/** A whole-number input that keeps the raw text while typing. */
export function NumberField(props: {
  label: string;
  hint?: string;
  value: string;
  onChange: (value: string) => void;
  min: number;
  max: number;
  error?: string;
}) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{props.label}</label>
      {props.hint && (
        <span className="hint" id={`${id}-hint`}>
          {props.hint}
        </span>
      )}
      <input
        id={id}
        type="number"
        inputMode="numeric"
        min={props.min}
        max={props.max}
        step={1}
        value={props.value}
        aria-describedby={props.hint ? `${id}-hint` : undefined}
        aria-invalid={props.error ? true : undefined}
        onChange={(e) => props.onChange(e.target.value)}
      />
      {props.error && (
        <span className="field-error" role="alert">
          {props.error}
        </span>
      )}
    </div>
  );
}

export const toWhole = (raw: string): number => (/^\d+$/.test(raw.trim()) ? Number(raw.trim()) : NaN);
