import React, { useCallback, useEffect, useMemo, useState } from "react";

const API = "/api/review";

const STATUS_STYLE = {
  proposed: { bg: "#3d3d5c", label: "Proposed" },
  validated: { bg: "#1b6b3a", label: "Validated" },
  rejected: { bg: "#7a1f1f", label: "Rejected" },
  held: { bg: "#7a5a12", label: "Hold" },
};

const RECON_STYLE = {
  promoted_gap_fill: { bg: "#2f855a", label: "Promoted" },
  dprr_authoritative: { bg: "#4a5568", label: "DPRR wins" },
  canonical_exists: { bg: "#718096", label: "Exists" },
  unreconciled: { bg: "#805ad5", label: "Unreconciled" },
};

function StatusBadge({ status }) {
  const key = status === "hold" ? "held" : status || "proposed";
  const style = STATUS_STYLE[key] || STATUS_STYLE.proposed;
  return (
    <span
      style={{
        background: style.bg,
        color: "#fff",
        padding: "2px 8px",
        borderRadius: 4,
        fontSize: 11,
        fontWeight: 600,
      }}
    >
      {style.label}
    </span>
  );
}

function ReconBadge({ status }) {
  const key = status || "unreconciled";
  const style = RECON_STYLE[key] || { bg: "#555", label: key };
  return (
    <span
      style={{
        background: style.bg,
        color: "#fff",
        padding: "2px 8px",
        borderRadius: 4,
        fontSize: 10,
        fontWeight: 600,
      }}
    >
      {style.label}
    </span>
  );
}

function IgarPanel({ igar, predicateStatus, researchNotes, claimLayer }) {
  const hasIgar = Boolean(
    igar?.input || igar?.goal || igar?.action || igar?.result || igar?.complete
  );
  const isInterpretation = claimLayer === "interpretation" || claimLayer === "igar";
  if (!hasIgar && predicateStatus !== "tbd" && !researchNotes && !isInterpretation) {
    return (
      <section
        style={{
          marginTop: 12,
          padding: 12,
          background: "#f7f7f8",
          border: "1px solid #ddd",
          borderRadius: 6,
          fontSize: 12,
          color: "#666",
        }}
      >
        <strong>IGAR</strong> — not attached (optional interpretation; atomic Q–P–Q stands alone)
      </section>
    );
  }
  const steps = [
    ["Input", igar?.input, igar?.input_year],
    ["Goal", igar?.goal, null],
    ["Action", igar?.action, igar?.action_year],
    ["Result", igar?.result, igar?.result_year],
  ];
  return (
    <section
      style={{
        marginTop: 12,
        padding: 12,
        background: "#f3eefc",
        border: "1px solid #b39ddb",
        borderRadius: 6,
        fontSize: 13,
      }}
    >
      <h3 style={{ fontSize: 14, margin: "0 0 8px" }}>
        IGAR interpretation (optional)
        {hasIgar && !igar?.complete && (
          <span style={{ marginLeft: 8, color: "#7a5a12", fontSize: 12 }}>incomplete</span>
        )}
        {!hasIgar && (
          <span style={{ marginLeft: 8, color: "#7a5a12", fontSize: 12 }}>not attached</span>
        )}
      </h3>
      {hasIgar ? (
        <div style={{ display: "grid", gap: 8 }}>
          {steps.map(([label, text, year]) => (
            <div key={label} style={{ display: "grid", gridTemplateColumns: "70px 1fr", gap: 8 }}>
              <div style={{ fontWeight: 700, color: "#555" }}>{label}</div>
              <div>
                <div>{text || "—"}</div>
                {year != null && (
                  <div style={{ fontSize: 11, color: "#888", fontFamily: "monospace" }}>
                    year {year}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ fontSize: 12, color: "#666" }}>
          Atomic participation does not need IGAR. Attach only after source-backed
          actor-decision research (Input = trigger, not biography).
        </div>
      )}
      {predicateStatus === "tbd" && (
        <div
          style={{
            marginTop: 10,
            padding: 8,
            background: "#fff3e0",
            border: "1px solid #ffb74d",
            borderRadius: 4,
            fontSize: 12,
          }}
        >
          <strong>Predicate TBD</strong> — do not Validate until research settles the type.
          {researchNotes && <div style={{ marginTop: 6 }}>{researchNotes}</div>}
        </div>
      )}
      {predicateStatus !== "tbd" && researchNotes && (
        <div style={{ marginTop: 8, fontSize: 12, color: "#555" }}>{researchNotes}</div>
      )}
    </section>
  );
}

function ApprovalContext({ ctx }) {
  if (!ctx) return null;
  const rows = [
    ["Person anchor", ctx.person?.label, ctx.person?.lifespan, ctx.person?.qid],
    ["SubjectConcept scope", ctx.scope?.label, ctx.scope?.routing_score != null ? `score ${ctx.scope.routing_score}` : null, ctx.scope?.subject_id],
    ["Target / other", ctx.target?.label, ctx.target?.when, ctx.target?.qid],
    [
      "Relationship",
      ctx.relationship?.type,
      ctx.relationship?.when,
      ctx.relationship?.pred_pid,
    ],
    [
      "Canonical edge",
      ctx.relationship?.canonical_exists ? ctx.relationship?.canonical_rel_type : "none in graph",
      ctx.relationship?.canonical_source,
      null,
    ],
    ["Source", ctx.provenance?.authority_source, ctx.provenance?.harvested_at, null],
    [
      "Agent enrichment",
      ctx.provenance?.enrichment_status || "pending",
      ctx.provenance?.enrichment_notes,
      ctx.date_completeness ? `dates: ${ctx.date_completeness}` : null,
    ],
  ];

  return (
    <section
      style={{
        marginTop: 12,
        padding: 12,
        background: "#eef6ff",
        border: "1px solid #90caf9",
        borderRadius: 6,
        fontSize: 13,
      }}
    >
      <h3 style={{ fontSize: 14, margin: "0 0 8px" }}>Before you approve</h3>
      <div style={{ display: "grid", gap: 8 }}>
        {rows.map(([label, primary, secondary, qid]) => (
          <div
            key={label}
            style={{
              display: "grid",
              gridTemplateColumns: "120px 1fr",
              gap: 8,
              alignItems: "baseline",
            }}
          >
            <div style={{ color: "#555", fontWeight: 600 }}>{label}</div>
            <div>
              <div style={{ fontWeight: 600 }}>{primary || "—"}</div>
              {secondary && (
                <div style={{ color: "#666", fontSize: 12, marginTop: 2 }}>{secondary}</div>
              )}
              {qid && (
                <div style={{ color: "#888", fontSize: 11, fontFamily: "monospace", marginTop: 2 }}>
                  {qid}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      {ctx.date_gaps?.length > 0 && (
        <div
          style={{
            marginTop: 10,
            padding: 8,
            background: "#fff3e0",
            border: "1px solid #ffb74d",
            borderRadius: 4,
            fontSize: 12,
          }}
        >
          <strong>Date gaps</strong> — Hold recommended; you may still validate with notes
          <ul style={{ margin: "6px 0 0", paddingLeft: 18 }}>
            {ctx.date_gaps.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      )}
      {ctx.geo_gaps?.length > 0 && (
        <div
          style={{
            marginTop: 10,
            padding: 8,
            background: "#fce4ec",
            border: "1px solid #f48fb1",
            borderRadius: 4,
            fontSize: 12,
          }}
        >
          <strong>Geo gaps</strong> — Validate blocked until Event has a Place with lat/long
          <ul style={{ margin: "6px 0 0", paddingLeft: 18 }}>
            {ctx.geo_gaps.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      )}
      {ctx.target?.location && (
        <div style={{ marginTop: 8, fontSize: 12, color: "#555" }}>
          <strong>Location:</strong> {ctx.target.location.label || "Place"}{" "}
          <span style={{ fontFamily: "monospace" }}>({ctx.target.location.qid})</span>
          {" · "}
          {Number(ctx.target.location.lat).toFixed(4)}, {Number(ctx.target.location.long).toFixed(4)}
        </div>
      )}
      {ctx.other_gaps?.length > 0 && (
        <div
          style={{
            marginTop: 10,
            padding: 8,
            background: "#fff8e1",
            border: "1px solid #ffcc80",
            borderRadius: 4,
            fontSize: 12,
          }}
        >
          <strong>Other gaps</strong>
          <ul style={{ margin: "6px 0 0", paddingLeft: 18 }}>
            {ctx.other_gaps.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      )}
      {!ctx.date_gaps?.length &&
        !ctx.geo_gaps?.length &&
        !ctx.other_gaps?.length &&
        ctx.warnings?.length > 0 && (
        <div
          style={{
            marginTop: 10,
            padding: 8,
            background: "#fff8e1",
            border: "1px solid #ffcc80",
            borderRadius: 4,
            fontSize: 12,
          }}
        >
          <strong>Gaps to check</strong>
          <ul style={{ margin: "6px 0 0", paddingLeft: 18 }}>
            {ctx.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

export default function ClaimReview() {
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [statusFilter, setStatusFilter] = useState("held");
  const [reconFilter, setReconFilter] = useState("all");
  const [agentFilter, setAgentFilter] = useState(
    "SFA_sc_q17167_military_wars_campaigns_MILITARY"
  );
  const [search, setSearch] = useState("");
  const [proposedOnly, setProposedOnly] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ limit: "500" });
      if (statusFilter !== "all") params.set("status", statusFilter);
      if (reconFilter === "unreconciled") params.set("reconciliation", "unreconciled");
      else if (reconFilter !== "all") params.set("reconciliation", reconFilter);
      if (agentFilter) params.set("source_agent", agentFilter);

      const res = await fetch(`${API}/claims?${params}`);
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setDoc(data);
      const ids = new Set((data.claims || []).map((c) => c.claim_id));
      setSelectedId((prev) =>
        prev && ids.has(prev) ? prev : data.claims?.[0]?.claim_id || null
      );
    } catch (err) {
      setError(
        err.message +
          " — restart review API: python scripts/ui/proposal_review_api.py"
      );
    } finally {
      setLoading(false);
    }
  }, [statusFilter, reconFilter, agentFilter]);

  useEffect(() => {
    load();
  }, [load]);

  // Hold/Validated/Rejected are explicit — do not also force "proposed".
  useEffect(() => {
    if (statusFilter !== "all" && statusFilter !== "proposed" && proposedOnly) {
      setProposedOnly(false);
    }
  }, [statusFilter, proposedOnly]);

  const claims = doc?.claims || [];
  const activeAgent = doc?.source_agent || agentFilter;

  const filtered = useMemo(() => {
    return claims.filter((c) => {
      if (
        agentFilter &&
        agentFilter !== "all" &&
        c.source_agent &&
        c.source_agent !== agentFilter
      ) {
        return false;
      }
      if (
        proposedOnly &&
        (statusFilter === "all" || statusFilter === "proposed") &&
        c.status !== "proposed" &&
        !c.promoted
      ) {
        return false;
      }
      if (search) {
        const q = search.toLowerCase();
        const hay = `${c.label} ${c.claim_id} ${c.subject_qid} ${c.relationship_type} ${c.wd_statement || ""}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [claims, proposedOnly, search, agentFilter, statusFilter]);

  const selected = claims.find((c) => c.claim_id === selectedId) || null;

  useEffect(() => {
    if (selected) setNotes(selected.review_notes || "");
  }, [selectedId, selected?.review_notes]);

  const saveStatus = async (status) => {
    if (!selected) return;

    const ctx = selected.approval_context;
    const dateGaps = ctx?.date_gaps || [];
    const geoGaps = ctx?.geo_gaps || [];
    const predicateTbd =
      (selected.predicate_status || ctx?.predicate_status) === "tbd";
    const claimLayer =
      selected.claim_layer || ctx?.claim_layer || "atomic_participation";
    const igarIncomplete =
      (claimLayer === "interpretation" || claimLayer === "igar") &&
      !(selected.igar?.complete || ctx?.igar?.complete);
    if (status === "validated" && predicateTbd) {
      window.alert(
        "Predicate is TBD. Keep on Hold until research settles the relationship type."
      );
      return;
    }
    if (status === "validated" && igarIncomplete) {
      window.alert(
        "This is an interpretation claim and IGAR is incomplete. Keep on Hold."
      );
      return;
    }
    if (status === "validated" && geoGaps.length > 0) {
      window.alert(
        [
          "Geo required: Event must link to a Place with Wikidata lat/long.",
          ...geoGaps.map((g) => `• ${g}`),
          "",
          "Keep on Hold. Run: python scripts/system/ensure_event_place_geo.py --event-qid <QID>",
        ].join("\n")
      );
      return;
    }
    if (status === "validated" && dateGaps.length > 0) {
      const noteOk = notes.trim().length >= 8;
      const msg = [
        "This claim has date gaps:",
        ...dateGaps.map((g) => `• ${g}`),
        "",
        noteOk
          ? "Review notes are present. Validate anyway?"
          : "Add review notes explaining why dates are acceptable, or use Hold.",
        "",
        noteOk ? "Click OK to validate with gaps acknowledged." : "Validation cancelled.",
      ].join("\n");
      if (!noteOk) {
        window.alert(msg);
        return;
      }
      if (!window.confirm(msg)) return;
    }

    setSaving(true);
    setError("");
    try {
      const res = await fetch(`${API}/claims/${encodeURIComponent(selected.claim_id)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status, review_notes: notes }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setDoc((prev) =>
        prev
          ? {
              ...prev,
              stats: data.stats,
              claims: prev.claims.map((c) =>
                c.claim_id === selected.claim_id ? data.claim : c
              ),
            }
          : prev
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const stats = doc?.stats || {};

  if (loading && !doc) {
    return <div style={{ padding: 24, color: "#555" }}>Loading biographic claims…</div>;
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "calc(100vh - 48px)",
        background: "#f4f5f7",
        color: "#1a1a2e",
      }}
    >
      <header
        style={{
          padding: "12px 16px",
          background: "#1a1a2e",
          color: "#eee",
          borderBottom: "2px solid #c0392b",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16 }}>Claims review</div>
            <div style={{ fontSize: 12, color: "#aaa" }}>
              Neo4j · {activeAgent} · {stats.total ?? 0} total · showing {filtered.length}
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginLeft: "auto" }}>
            <span style={{ fontSize: 11, color: "#ccc" }}>
              Proposed: <strong style={{ color: "#fff" }}>{stats.proposed ?? 0}</strong>
            </span>
            <span style={{ fontSize: 11, color: "#ccc" }}>
              Held: <strong style={{ color: "#fff" }}>{stats.held ?? 0}</strong>
            </span>
            <span style={{ fontSize: 11, color: "#ccc" }}>
              Validated: <strong style={{ color: "#fff" }}>{stats.validated ?? 0}</strong>
            </span>
            <span style={{ fontSize: 11, color: "#ccc" }}>
              Promoted: <strong style={{ color: "#fff" }}>{stats.promoted ?? 0}</strong>
            </span>
            <span style={{ fontSize: 11, color: "#9fd" }}>
              Fischer skipped: <strong>{stats.fischer?.skipped ?? 0}</strong>
            </span>
          </div>
          <button
            onClick={load}
            style={{
              padding: "6px 12px",
              border: "none",
              borderRadius: 4,
              background: "#c0392b",
              color: "#fff",
              cursor: "pointer",
            }}
          >
            Reload
          </button>
        </div>
        {error && (
          <div
            style={{
              marginTop: 8,
              padding: 8,
              background: "#7a1f1f",
              borderRadius: 4,
              fontSize: 12,
            }}
          >
            {error}
          </div>
        )}
      </header>

      <div
        style={{
          padding: "8px 16px",
          display: "flex",
          gap: 8,
          flexWrap: "wrap",
          background: "#fff",
          borderBottom: "1px solid #ddd",
        }}
      >
        <select value={agentFilter} onChange={(e) => setAgentFilter(e.target.value)}>
          <option value="SFA_sc_q17167_military_wars_campaigns_MILITARY">
            Military pilot
          </option>
          <option value="sfa_biographic">Biographic</option>
          <option value="all">All agents</option>
        </select>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">All statuses</option>
          <option value="proposed">Proposed</option>
          <option value="validated">Validated</option>
          <option value="rejected">Rejected</option>
          <option value="held">Hold</option>
        </select>
        <select value={reconFilter} onChange={(e) => setReconFilter(e.target.value)}>
          <option value="all">All reconciliation</option>
          <option value="unreconciled">Unreconciled</option>
          <option value="promoted_gap_fill">Promoted gap-fill</option>
          <option value="dprr_authoritative">DPRR authoritative</option>
          <option value="canonical_exists">Canonical exists</option>
        </select>
        <input
          type="search"
          placeholder="Search label, claim_id, subject_qid…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ flex: 1, minWidth: 200, padding: "6px 8px" }}
        />
        <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}>
          <input
            type="checkbox"
            checked={proposedOnly}
            onChange={(e) => setProposedOnly(e.target.checked)}
          />
          Needs review
        </label>
      </div>

      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <div
          style={{
            width: 360,
            overflowY: "auto",
            borderRight: "1px solid #ddd",
            background: "#fff",
          }}
        >
          {filtered.map((c) => {
            const active = c.claim_id === selectedId;
            return (
              <div
                key={c.claim_id}
                onClick={() => setSelectedId(c.claim_id)}
                style={{
                  padding: "10px 12px",
                  borderBottom: "1px solid #eee",
                  cursor: "pointer",
                  background: active ? "#fdecea" : "#fff",
                  borderLeft: active ? "3px solid #c0392b" : "3px solid transparent",
                }}
              >
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 4 }}>
                  <StatusBadge status={c.status} />
                  <ReconBadge status={c.reconciliation_status} />
                  {c.relationship_type && (
                    <span style={{ fontSize: 10, color: "#666", fontFamily: "monospace" }}>
                      {c.relationship_type}
                    </span>
                  )}
                </div>
                <div style={{ fontWeight: 600, fontSize: 13, lineHeight: 1.3 }}>{c.label}</div>
                {c.fischer_status === "skipped" && (
                  <div style={{ fontSize: 10, color: "#888", marginTop: 4 }}>Fischer skipped (documentary)</div>
                )}
              </div>
            );
          })}
          {!filtered.length && (
            <div style={{ padding: 16, color: "#888", fontSize: 13 }}>No claims match filters.</div>
          )}
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
          {!selected ? (
            <div style={{ color: "#888" }}>Select a claim from the list.</div>
          ) : (
            <>
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <h2 style={{ margin: 0, fontSize: 18 }}>{selected.label}</h2>
                <StatusBadge status={selected.status} />
                <ReconBadge status={selected.reconciliation_status} />
              </div>
              <div style={{ fontSize: 12, color: "#666", marginTop: 4, fontFamily: "monospace" }}>
                {selected.claim_id} · person anchor {selected.person_qid || selected.subject_qid}
                {selected.candidate_qid && ` · candidate ${selected.candidate_qid}`}
                {selected.pred_pid && ` · ${selected.pred_pid}`}
              </div>
              {selected.wd_statement && (
                <div
                  style={{
                    marginTop: 8,
                    padding: "8px 10px",
                    background: "#111827",
                    color: "#e5e7eb",
                    borderRadius: 4,
                    fontFamily: "monospace",
                    fontSize: 13,
                  }}
                >
                  {selected.wd_statement}
                  <div style={{ fontSize: 10, color: "#9ca3af", marginTop: 4 }}>
                    language-neutral Wikidata statement
                  </div>
                </div>
              )}

              {selected.description && (
                <section
                  style={{
                    marginTop: 12,
                    padding: 12,
                    background: "#fff",
                    border: "1px solid #ddd",
                    borderRadius: 6,
                    fontSize: 13,
                    lineHeight: 1.5,
                  }}
                >
                  <h3 style={{ fontSize: 14, margin: "0 0 8px" }}>Description</h3>
                  <p style={{ margin: 0, color: "#333" }}>{selected.description}</p>
                </section>
              )}

              {(selected.routed_subject_label || selected.routed_subject_id) && (
                <section
                  style={{
                    marginTop: 12,
                    padding: 12,
                    background: "#f3e5f5",
                    border: "1px solid #ce93d8",
                    borderRadius: 6,
                    fontSize: 13,
                  }}
                >
                  <h3 style={{ fontSize: 14, margin: "0 0 8px" }}>SubjectConcept scope</h3>
                  <div style={{ fontWeight: 600 }}>{selected.routed_subject_label || selected.routed_subject_id}</div>
                  {selected.scope_description && (
                    <p style={{ margin: "6px 0 0", color: "#555" }}>{selected.scope_description}</p>
                  )}
                  <div style={{ marginTop: 6, color: "#777", fontSize: 11, fontFamily: "monospace" }}>
                    {selected.routed_subject_id}
                    {selected.routing_score != null &&
                      ` · routing ${Number(selected.routing_score).toFixed(2)} (${selected.routing_method || "?"})`}
                  </div>
                </section>
              )}

              <IgarPanel
                igar={selected.igar || selected.approval_context?.igar}
                predicateStatus={
                  selected.predicate_status || selected.approval_context?.predicate_status
                }
                researchNotes={
                  selected.research_notes || selected.approval_context?.research_notes
                }
                claimLayer={
                  selected.claim_layer ||
                  selected.approval_context?.claim_layer ||
                  'atomic_participation'
                }
              />
              <ApprovalContext ctx={selected.approval_context} />

              {(selected.from_qid || selected.to_qid) && (
                <section
                  style={{
                    marginTop: 12,
                    padding: 12,
                    background: "#f8f9fa",
                    border: "1px solid #ddd",
                    borderRadius: 6,
                    fontSize: 13,
                  }}
                >
                  <h3 style={{ fontSize: 14, margin: "0 0 8px" }}>Proposed edge</h3>
                  <div style={{ fontFamily: "monospace", fontSize: 12 }}>
                    ({selected.from_label || "?"}) —[:{selected.relationship_type || "?"}]→ (
                    {selected.to_label || "?"})
                  </div>
                  <div style={{ marginTop: 6, color: "#666", fontSize: 11 }}>
                    FROM {selected.from_qid} → TO {selected.to_qid}
                  </div>
                </section>
              )}

              <div
                style={{
                  marginTop: 12,
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))",
                  gap: 8,
                  fontSize: 12,
                }}
              >
                {[
                  ["Type", selected.claim_type],
                  ["SubjectConcept", selected.routed_subject_label],
                  ["Relationship", selected.relationship_type],
                  ["Person lifespan", selected.person_lifespan],
                  ["Target when", selected.target_when],
                  ["Relation when", selected.relation_when],
                  ["Date completeness", selected.date_completeness],
                  ["Enrichment", selected.enrichment_status],
                  ["Registry", selected.registry_status],
                  ["Wikidata PID", selected.pred_pid],
                  ["Item type", selected.item_type_label],
                  ["Harvested", selected.harvested_at],
                  ["Confidence", selected.confidence?.toFixed?.(3) ?? selected.confidence],
                  ["Posterior", selected.posterior_probability?.toFixed?.(3) ?? selected.posterior_probability],
                  ["Fischer", selected.fischer_status],
                  ["Authority", selected.authority_source],
                  ["Promoted", selected.promoted ? "yes" : "no"],
                  ["Direction fixed", selected.direction_corrected ? "yes" : "no"],
                ].map(([k, v]) => (
                  <div key={k} style={{ background: "#fff", padding: 8, borderRadius: 4, border: "1px solid #ddd" }}>
                    <div style={{ color: "#888" }}>{k}</div>
                    <div style={{ fontWeight: 600 }}>{v ?? "—"}</div>
                  </div>
                ))}
              </div>

              {selected.fallacies_detected?.length > 0 && (
                <div
                  style={{
                    marginTop: 12,
                    padding: 12,
                    background: "#fef9e7",
                    border: "1px solid #f5a623",
                    borderRadius: 6,
                    fontSize: 13,
                  }}
                >
                  <strong>Fischer / fallacy flags</strong>
                  <div style={{ marginTop: 4 }}>{selected.fallacies_detected.join(", ")}</div>
                </div>
              )}

              <section style={{ marginTop: 16, marginBottom: 16 }}>
                <h3 style={{ fontSize: 14, marginBottom: 6 }}>Review notes</h3>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  style={{ width: "100%", padding: 8, fontSize: 13, boxSizing: "border-box" }}
                />
              </section>

              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                {[
                  ["validated", "#1b6b3a", "Validate"],
                  ["held", "#7a5a12", "Hold"],
                  ["rejected", "#7a1f1f", "Reject"],
                  ["proposed", "#555", "Reset to Proposed"],
                ].map(([status, bg, label]) => (
                  <button
                    key={status}
                    disabled={saving}
                    onClick={() => saveStatus(status)}
                    style={{
                      padding: "10px 18px",
                      border: "none",
                      borderRadius: 6,
                      background: bg,
                      color: "#fff",
                      fontWeight: 600,
                      cursor: saving ? "wait" : "pointer",
                      opacity: saving ? 0.7 : 1,
                    }}
                  >
                    {label}
                  </button>
                ))}
                {selected.approval_context?.geo_gaps?.length > 0 && (
                  <span style={{ fontSize: 12, color: "#ad1457" }}>
                    Geo gaps — Validate blocked until Place has lat/long
                  </span>
                )}
                {selected.approval_context?.date_gaps?.length > 0 && (
                  <span style={{ fontSize: 12, color: "#b45309" }}>
                    Date gaps — Hold recommended, or validate with notes
                  </span>
                )}
              </div>

              <div style={{ marginTop: 12, fontSize: 12, color: "#666" }}>
                Agent enrichment:
                <code style={{ display: "block", marginTop: 4, padding: 8, background: "#eee" }}>
                  python -m scripts.agents.biographic.enrich_claims --limit 500 --write
                </code>
              </div>

              <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
                Familial gap-fill promotion:
                <code style={{ display: "block", marginTop: 4, padding: 8, background: "#eee" }}>
                  python -m scripts.agents.biographic.reconcile_familial --write
                </code>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
