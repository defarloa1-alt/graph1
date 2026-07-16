import React, { useCallback, useEffect, useMemo, useState } from "react";

const FACET_COLORS = {
  military: "#E74C3C",
  political: "#3F51B5",
  religious: "#795548",
  social: "#FF5722",
  economic: "#2ECC71",
  intellectual: "#1ABC9C",
  scientific: "#00BCD4",
  linguistic: "#F39C12",
  communication: "#3498DB",
  artistic: "#9B59B6",
  archaeological: "#8B4513",
  cultural: "#E91E63",
  demographic: "#FF9800",
  biographic: "#C0392B",
  geographic: "#16A085",
  diplomatic: "#607D8B",
  environmental: "#4CAF50",
  technological: "#9C27B0",
};

const STATUS_STYLE = {
  proposed: { bg: "#3d3d5c", label: "Proposed" },
  approved: { bg: "#1b6b3a", label: "Approved" },
  rejected: { bg: "#7a1f1f", label: "Rejected" },
  held: { bg: "#7a5a12", label: "Hold" },
};

const RESOLUTION_STYLE = {
  novel: { bg: "#2c5282", label: "Novel" },
  merge: { bg: "#6b46c1", label: "Merge" },
  additive: { bg: "#2f855a", label: "Additive" },
  conflict: { bg: "#c53030", label: "Conflict" },
  hold: { bg: "#975a16", label: "SCA Hold" },
  skip: { bg: "#4a5568", label: "Skip" },
};

const API = "/api/review";

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

function ResolutionBadge({ action }) {
  const key = action || "novel";
  const style = RESOLUTION_STYLE[key] || RESOLUTION_STYLE.novel;
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

function FacetPill({ facet }) {
  const color = FACET_COLORS[facet] || "#666";
  return (
    <span
      style={{
        background: color + "22",
        color,
        border: `1px solid ${color}`,
        padding: "2px 8px",
        borderRadius: 4,
        fontSize: 11,
        fontWeight: 600,
        textTransform: "capitalize",
      }}
    >
      {facet}
    </span>
  );
}

export default function ProposalReview() {
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [facetFilter, setFacetFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [bioOnly, setBioOnly] = useState(false);
  const [scaOnly, setScaOnly] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API}/document`);
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setDoc(data);
      setSelectedId((prev) => prev || data.proposals?.[0]?.subject_id || null);
    } catch (err) {
      setError(
        err.message +
          " — start the review API: python scripts/ui/proposal_review_api.py"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const proposals = doc?.proposals || [];

  const facets = useMemo(() => {
    const set = new Set(proposals.map((p) => p.source_facet).filter(Boolean));
    return ["all", ...Array.from(set).sort()];
  }, [proposals]);

  const filtered = useMemo(() => {
    return proposals.filter((p) => {
      if (facetFilter !== "all" && p.source_facet !== facetFilter) return false;
      const st = p.status || "proposed";
      if (statusFilter !== "all" && st !== statusFilter) return false;
      if (bioOnly && !p.bio_conflict_hint) return false;
      if (scaOnly) {
        const tier = p.resolution_tier || p.resolution?.tier;
        const action = p.resolution_action || p.resolution?.action;
        if (tier !== "sca_llm" && !["conflict", "hold"].includes(action)) return false;
      }
      if (search) {
        const q = search.toLowerCase();
        const hay = `${p.label} ${p.description} ${p.subject_id}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [proposals, facetFilter, statusFilter, bioOnly, scaOnly, search]);

  const selected = proposals.find((p) => p.subject_id === selectedId) || null;

  useEffect(() => {
    if (selected) {
      setNotes(selected.review_notes || "");
    }
  }, [selectedId, selected?.review_notes]);

  const saveStatus = async (status) => {
    if (!selected) return;
    setSaving(true);
    setError("");
    try {
      const res = await fetch(`${API}/proposals/${encodeURIComponent(selected.subject_id)}`, {
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
              proposals: prev.proposals.map((p) =>
                p.subject_id === selected.subject_id ? data.proposal : p
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
    return (
      <div style={{ padding: 24, color: "#555" }}>Loading review queue…</div>
    );
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
          borderBottom: "2px solid #4361ee",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16 }}>Proposal Review Queue</div>
            <div style={{ fontSize: 12, color: "#aaa" }}>
              {doc?.seed_label} ({doc?.seed_qid}) · {doc?.path}
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginLeft: "auto" }}>
            {Object.entries(STATUS_STYLE).map(([key, s]) => (
              <span key={key} style={{ fontSize: 11, color: "#ccc" }}>
                {s.label}: <strong style={{ color: "#fff" }}>{stats[key] ?? 0}</strong>
              </span>
            ))}
            <span style={{ fontSize: 11, color: "#f5a623" }}>
              Bio flags: <strong>{stats.bio_conflict_flags ?? 0}</strong>
            </span>
            {doc?.resolution_pass?.summary && (
              <span style={{ fontSize: 11, color: "#9fd" }}>
                SCA: {JSON.stringify(doc.resolution_pass.summary)}
              </span>
            )}
          </div>
          <button
            onClick={load}
            style={{
              padding: "6px 12px",
              border: "none",
              borderRadius: 4,
              background: "#4361ee",
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
        <select value={facetFilter} onChange={(e) => setFacetFilter(e.target.value)}>
          {facets.map((f) => (
            <option key={f} value={f}>
              {f === "all" ? "All facets" : f}
            </option>
          ))}
        </select>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">All statuses</option>
          <option value="proposed">Proposed</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="held">Hold</option>
        </select>
        <input
          type="search"
          placeholder="Search label, description, subject_id…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ flex: 1, minWidth: 200, padding: "6px 8px" }}
        />
        <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}>
          <input
            type="checkbox"
            checked={scaOnly}
            onChange={(e) => setScaOnly(e.target.checked)}
          />
          SCA review only
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}>
          <input
            type="checkbox"
            checked={bioOnly}
            onChange={(e) => setBioOnly(e.target.checked)}
          />
          Bio overlap only
        </label>
      </div>

      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <div
          style={{
            width: 340,
            overflowY: "auto",
            borderRight: "1px solid #ddd",
            background: "#fff",
          }}
        >
          {filtered.map((p) => {
            const active = p.subject_id === selectedId;
            return (
              <div
                key={p.subject_id}
                onClick={() => setSelectedId(p.subject_id)}
                style={{
                  padding: "10px 12px",
                  borderBottom: "1px solid #eee",
                  cursor: "pointer",
                  background: active ? "#eef1ff" : "#fff",
                  borderLeft: active ? "3px solid #4361ee" : "3px solid transparent",
                }}
              >
                <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 4, flexWrap: "wrap" }}>
                  <FacetPill facet={p.source_facet} />
                  <StatusBadge status={p.status} />
                  {p.resolution_action && <ResolutionBadge action={p.resolution_action} />}
                </div>
                <div style={{ fontWeight: 600, fontSize: 13, lineHeight: 1.3 }}>{p.label}</div>
                {p.bio_conflict_hint && (
                  <div style={{ fontSize: 10, color: "#c0392b", marginTop: 4 }}>⚠ Bio overlap</div>
                )}
              </div>
            );
          })}
          {!filtered.length && (
            <div style={{ padding: 16, color: "#888", fontSize: 13 }}>No proposals match filters.</div>
          )}
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
          {!selected ? (
            <div style={{ color: "#888" }}>Select a proposal from the list.</div>
          ) : (
            <>
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <h2 style={{ margin: 0, fontSize: 20 }}>{selected.label}</h2>
                <FacetPill facet={selected.source_facet} />
                <StatusBadge status={selected.status} />
                {selected.resolution_action && (
                  <ResolutionBadge action={selected.resolution_action} />
                )}
              </div>
              <div style={{ fontSize: 12, color: "#666", marginTop: 4, fontFamily: "monospace" }}>
                {selected.subject_id}
              </div>

              {selected.resolution_rationale && (
                <div
                  style={{
                    marginTop: 12,
                    padding: 12,
                    background: "#eef6ff",
                    border: "1px solid #4361ee",
                    borderRadius: 6,
                    fontSize: 13,
                    lineHeight: 1.5,
                  }}
                >
                  <strong>
                    SCA resolution ({selected.resolution_tier || "?"})
                  </strong>
                  <div style={{ marginTop: 4 }}>{selected.resolution_rationale}</div>
                  {selected.resolution_merge_target && (
                    <div style={{ marginTop: 6, fontFamily: "monospace", fontSize: 12 }}>
                      merge_target: {selected.resolution_merge_target}
                    </div>
                  )}
                  {selected.bio_primary_note && (
                    <div style={{ marginTop: 6, color: "#c0392b" }}>
                      {selected.bio_primary_note}
                    </div>
                  )}
                </div>
              )}

              {selected.bio_conflict_hint && (
                <div
                  style={{
                    marginTop: 12,
                    padding: 12,
                    background: "#fdecea",
                    border: "1px solid #e74c3c",
                    borderRadius: 6,
                    fontSize: 13,
                    lineHeight: 1.5,
                  }}
                >
                  <strong>Biographic primary-owner check</strong>
                  <div style={{ marginTop: 4 }}>{selected.bio_conflict_hint}</div>
                </div>
              )}

              <p style={{ marginTop: 12, lineHeight: 1.5, color: "#333" }}>
                {selected.description}
              </p>

              {selected.validation && (
                <div
                  style={{
                    padding: 10,
                    background: selected.validation.ccs_pass ? "#eafaf1" : "#fef9e7",
                    borderRadius: 6,
                    fontSize: 13,
                    marginBottom: 12,
                  }}
                >
                  <strong>CCS:</strong> {selected.validation.ccs_pass ? "PASS" : "FAIL"}
                  {!selected.validation.ccs_pass &&
                    selected.validation.failures?.map((f, i) => (
                      <div key={i} style={{ marginTop: 4, color: "#7a5a12" }}>
                        {f}
                      </div>
                    ))}
                </div>
              )}

              {selected.scholarly_overview && (
                <section style={{ marginBottom: 16 }}>
                  <h3 style={{ fontSize: 14, marginBottom: 6 }}>Scholarly overview</h3>
                  <div
                    style={{
                      fontSize: 13,
                      lineHeight: 1.6,
                      whiteSpace: "pre-wrap",
                      background: "#fff",
                      padding: 12,
                      borderRadius: 6,
                      border: "1px solid #ddd",
                      maxHeight: 280,
                      overflowY: "auto",
                    }}
                  >
                    {selected.scholarly_overview}
                  </div>
                </section>
              )}

              {selected.supporting_works?.length > 0 && (
                <section style={{ marginBottom: 16 }}>
                  <h3 style={{ fontSize: 14, marginBottom: 6 }}>
                    Supporting works ({selected.supporting_works.length})
                  </h3>
                  <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13, lineHeight: 1.5 }}>
                    {selected.supporting_works.slice(0, 12).map((w, i) => (
                      <li key={i}>
                        {w.source_url ? (
                          <a href={w.source_url} target="_blank" rel="noreferrer">
                            {w.title || w.work_id}
                          </a>
                        ) : (
                          w.title || w.work_id
                        )}
                        {w.year ? ` (${w.year})` : ""}
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              <section style={{ marginBottom: 16 }}>
                <h3 style={{ fontSize: 14, marginBottom: 6 }}>Review notes</h3>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  style={{ width: "100%", padding: 8, fontSize: 13, boxSizing: "border-box" }}
                  placeholder="Why approved, rejected, or on hold…"
                />
              </section>

              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {[
                  ["approved", "#1b6b3a", "Approve"],
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
              </div>

              <div style={{ marginTop: 16, fontSize: 12, color: "#666" }}>
                After review, write approved items to Neo4j:
                <code style={{ display: "block", marginTop: 4, padding: 8, background: "#eee" }}>
                  python scripts/agents/domain_initiator/propose.py --write-from output/di_proposals/Q17167_proposals_enriched.json --write
                </code>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
