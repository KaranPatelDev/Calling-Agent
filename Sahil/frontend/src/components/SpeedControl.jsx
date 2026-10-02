const MIN_RATE = 40;
// Polly's hard ceiling is 200%, but only for standard voices (neural caps near 150%) and
// Polly.Aditi — the only Hindi voice Plivo reliably supports — turns clipped/chipmunky past
// ~150, so cap there even though the provider would accept more.
const MAX_RATE = 150;

function describe(rate) {
  if (rate === "" || rate == null) return "Using default";
  const n = Number(rate);
  if (!Number.isFinite(n)) return "";
  const delta = n - 100;
  if (delta === 0) return "normal speed";
  return `${Math.abs(delta)}% ${delta > 0 ? "faster" : "slower"}`;
}

export default function SpeedControl({ value, onChange }) {
  // Clamp the max only. Clamping the min mid-keystroke rewrites "4" to "40" under the
  // cursor, which makes "45" untypeable; under-minimum input is caught by the API instead.
  function handleChange(raw) {
    if (raw === "") return onChange("");
    const n = Number(raw);
    if (Number.isFinite(n) && n > MAX_RATE) return onChange(String(MAX_RATE));
    onChange(raw);
  }

  const belowMin = value !== "" && Number(value) < MIN_RATE;

  return (
    <div className="field-group">
      <label className="field-label">Speaking speed (optional)</label>
      <p className="field-hint">
        Leave blank to use your default speed from Settings. 100% is normal — below is slower,
        above is faster.
      </p>
      <div className="row">
        <input
          type="number"
          min={MIN_RATE}
          max={MAX_RATE}
          placeholder="Default"
          value={value ?? ""}
          onChange={(e) => handleChange(e.target.value)}
          style={{ width: "6rem" }}
        />
        <span>%</span>
        {value !== "" && (
          <span className="field-hint">{describe(value)}</span>
        )}
      </div>
      {belowMin && (
        <p className="field-hint">
          Minimum is {MIN_RATE}%. Calls below that will be rejected.
        </p>
      )}
    </div>
  );
}