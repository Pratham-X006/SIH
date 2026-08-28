"""SETU command-centre dashboard. Every control here calls a real backend endpoint — there
are no hardcoded numbers or buttons that don't do anything (see docs/LIMITATIONS.md for what
IS still a placeholder, e.g. accessibility_score, which is honestly labeled ASSUMPTION
in the UI itself, not hidden).

Run with: streamlit run app.py   (backend must be running at BACKEND_URL below)
"""
from __future__ import annotations

import math

import httpx
import pandas as pd
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="SETU — Disaster Early Warning & Relief Tracking", layout="wide", page_icon="🌊")

CUSTOM_CSS = """
<style>
.setu-badge { display:inline-block; padding:2px 10px; border-radius:10px; font-size:0.75rem;
  font-weight:600; margin-right:4px; }
.badge-real { background:#1b4332; color:#95d5b2; }
.badge-derived { background:#1a3a5c; color:#90caf9; }
.badge-synthetic { background:#5c3a1a; color:#ffcc80; }
.badge-simulated { background:#3a1a5c; color:#ce93d8; }
.badge-critical { background:#5c1a1a; color:#ff8a80; }
.badge-high { background:#5c3a1a; color:#ffcc80; }
.badge-moderate { background:#5c5a1a; color:#fff59d; }
.badge-low { background:#1b4332; color:#95d5b2; }
.setu-card { background:#161b22; border:1px solid #30363d; border-radius:8px; padding:14px 16px; margin-bottom:10px; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

BADGE_CLASS = {
    "REAL": "badge-real", "DERIVED": "badge-derived", "SYNTHETIC": "badge-synthetic",
    "SIMULATED": "badge-simulated", "critical": "badge-critical", "severe": "badge-critical",
    "high": "badge-high", "moderate": "badge-moderate", "low": "badge-low",
}


def badge(text: str, kind: str | None = None) -> str:
    css_class = BADGE_CLASS.get(kind or text, "badge-derived")
    return f'<span class="setu-badge {css_class}">{text}</span>'


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 1)


def api_get(path: str, token: str | None = None, **params):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = httpx.get(f"{BACKEND_URL}{path}", params=params, headers=headers, timeout=15)
        if resp.status_code >= 400:
            return None, f"{resp.status_code}: {resp.json().get('detail', resp.text)}"
        return resp.json(), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def api_post(path: str, json: dict, token: str | None = None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = httpx.post(f"{BACKEND_URL}{path}", json=json, headers=headers, timeout=20)
        if resp.status_code >= 400:
            return None, f"{resp.status_code}: {resp.json().get('detail', resp.text)}"
        return resp.json(), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


# ---------------------------------------------------------------------------
# Sidebar: auth + system status
# ---------------------------------------------------------------------------
st.session_state.setdefault("token", None)
st.session_state.setdefault("role", None)
st.session_state.setdefault("username", None)

with st.sidebar:
    st.markdown("## 🌊 SETU")
    st.caption("SIH 2026 · IHSIH027 · Team Optimistic Braincells")

    if st.session_state["token"]:
        st.success(f"Logged in as **{st.session_state['username']}** ({st.session_state['role']})")
        if st.button("Log out"):
            st.session_state["token"] = None
            st.session_state["role"] = None
            st.session_state["username"] = None
            st.rerun()
    else:
        with st.form("login_form"):
            st.markdown("**Login**")
            u = st.text_input("Username", value="district_officer")
            p = st.text_input("Password", value="demo-pass-1", type="password")
            if st.form_submit_button("Log in"):
                result, err = api_post("/api/auth/login", {"username": u, "password": p})
                if err:
                    st.error(err)
                else:
                    st.session_state["token"] = result["token"]
                    st.session_state["role"] = result["role"]
                    st.session_state["username"] = u
                    st.rerun()
        st.caption("Demo accounts: district_officer/demo-pass-1, warehouse_mgr/demo-pass-2, "
                   "ngo_coordinator/demo-pass-3, relief_centre/demo-pass-4, auditor/demo-pass-5. "
                   "See docs/DEMO.md. SYNTHETIC accounts — not real credentials.")

    st.divider()
    st.markdown("**System status**")
    status, err = api_get("/api/system/status")
    if err:
        st.error(f"Backend unreachable: {err}")
    else:
        icon = {"ok": "🟢", "degraded": "🟠"}.get(status["overall"], "🔴")
        st.write(f"{icon} Overall: {status['overall']}")
        st.caption(f"DB: {status['database']}")
        st.caption(f"ML: {status['ml_model']}")
        st.caption(f"Blockchain: {status['blockchain']}")

TOKEN = st.session_state["token"]
ROLE = st.session_state["role"]

st.title("AI-Powered Disaster Early Warning, Impact Assessment & Relief Management")
st.caption("PREDICT → ASSESS → ESTIMATE → PRIORITIZE → ALLOCATE → TRACK → VERIFY → AUDIT")

districts, err = api_get("/impact/districts")
if err:
    st.error(f"Can't reach backend at {BACKEND_URL} — start it first. {err}")
    st.stop()
district_names = [d["name"] for d in districts]

(tab_overview, tab_hazard, tab_predict, tab_requirements, tab_allocation,
 tab_deliveries, tab_audit) = st.tabs(
    ["🎯 Command Dashboard", "🌧️ Live Hazard Feed", "📈 Predict & Assess",
     "📦 Requirements & Priority", "🚚 Allocation", "✅ Deliveries & Discrepancies",
     "🔍 Audit & Data Sources"]
)

# ---------------------------------------------------------------------------
# TAB: Command Dashboard — "what is happening, where, who's affected, what's needed,
# what's allocated, did it arrive, are there discrepancies" in one screen.
# ---------------------------------------------------------------------------
with tab_overview:
    st.subheader("What is happening right now")
    priorities, _ = api_get("/api/priorities")
    allocations, _ = api_get("/api/allocations")
    discrepancies, _ = api_get("/api/deliveries/discrepancies")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Zones with a priority score", len({p["zone_id"] for p in priorities}) if priorities else 0)
    c2.metric("Allocations recorded", len(allocations) if allocations else 0)
    open_disc = [d for d in (discrepancies or []) if d["status"] == "OPEN"]
    c3.metric("Open discrepancies", len(open_disc), delta=None if not open_disc else "needs review", delta_color="inverse")
    unverified = [a for a in (allocations or []) if a["status"] not in ("VERIFIED", "DISCREPANCY")]
    c4.metric("Pending / unverified deliveries", len(unverified))

    st.markdown("#### High-priority zones")
    if priorities:
        df = pd.DataFrame(priorities)[["zone_id", "disaster_label", "priority_score", "created_at"]]
        st.dataframe(df.sort_values("priority_score", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No priority scores computed yet — go to 'Requirements & Priority' to compute some.")

    st.markdown("#### Recent allocations")
    if allocations:
        df = pd.DataFrame(allocations)[["id", "zone_id", "warehouse_id", "resource_type", "quantity_recommended", "status", "chain_tx_hash"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No allocations yet — go to 'Allocation' to recommend and approve one.")

    if open_disc:
        st.markdown("#### 🚩 Flagged discrepancies")
        st.dataframe(pd.DataFrame(open_disc), use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# TAB: Live Hazard Feed (existing, real)
# ---------------------------------------------------------------------------
with tab_hazard:
    st.subheader("Live weather + seismic + multi-hazard feed")
    st.caption("Calls Open-Meteo / USGS / GDACS directly — needs normal outbound internet.")
    st.markdown(badge("REAL") + " these three sources are live third-party APIs, not mocked.", unsafe_allow_html=True)
    district = st.selectbox("District", district_names, key="live_district")
    d = next(x for x in districts if x["name"] == district)
    if st.button("Fetch live hazard data"):
        data, err = api_get("/hazards/live", lat=d["centroid"]["lat"], lon=d["centroid"]["lon"])
        if err:
            st.error(err)
        else:
            if data["errors"]:
                st.warning(f"Some sources failed: {data['errors']}")
            if data["weather"]:
                st.line_chart(pd.Series(data["weather"]["hourly_precipitation_mm"], name="precip_mm"))
            st.metric("Earthquakes (30 days, India)", data["earthquakes_count_30d"])

# ---------------------------------------------------------------------------
# TAB: Predict & Assess (existing "Early Warning -> Impact", kept + labeled)
# ---------------------------------------------------------------------------
with tab_predict:
    st.subheader("Predict risk, then assess impact")
    st.markdown(badge("DERIVED") + " risk score from a trained/fallback model; population exposure is an ESTIMATE, not a census count.", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        rain_24h = st.number_input("Rainfall last 24h (mm)", 0.0, 500.0, 60.0)
        rain_72h = st.number_input("Rainfall last 72h (mm)", 0.0, 1000.0, 180.0)
        rain_7d = st.number_input("Rainfall last 7d (mm)", 0.0, 2000.0, 320.0)
        intensity = st.number_input("Max rain intensity (mm/h)", 0.0, 100.0, 12.0)
        district2 = st.selectbox("District", district_names, key="impact_district")
        if st.button("Run prediction → impact"):
            risk, err = api_post("/predict/flood-risk", {
                "rain_24h_mm": rain_24h, "rain_72h_mm": rain_72h, "rain_7d_mm": rain_7d,
                "rain_intensity_max_mm_h": intensity,
            })
            if err:
                st.error(err)
            else:
                st.session_state["last_risk"] = risk
                impact, err2 = api_post("/impact/assessment", {"district": district2, "risk_score": risk["risk_score"]})
                st.session_state["last_impact"] = impact if not err2 else None
                st.session_state["last_zone"] = district2
    with col2:
        if "last_risk" in st.session_state:
            r = st.session_state["last_risk"]
            st.markdown(f"**Risk level:** {badge(r['risk_level'], r['risk_level'])}  (score {r['risk_score']})", unsafe_allow_html=True)
            st.caption(f"Model: {r['model_source']}")
            st.json(r)
        if st.session_state.get("last_impact"):
            st.json(st.session_state["last_impact"])

# ---------------------------------------------------------------------------
# TAB: Requirements & Priority (NEW)
# ---------------------------------------------------------------------------
with tab_requirements:
    st.subheader("Relief requirement engine — gross minus existing inventory")
    st.markdown(badge("DERIVED") + " formula-based, not a black box — every response includes the assumptions used.", unsafe_allow_html=True)

    req_zone = st.selectbox("Zone", district_names, key="req_zone")
    exposed = st.number_input("Exposed population", 0, 5_000_000,
                               st.session_state.get("last_impact", {}).get("estimated_exposed_population", 5000)
                               if st.session_state.get("last_impact") else 5000)
    days = st.slider("Relief duration (days)", 1, 14, 3)
    if st.button("Calculate net requirement"):
        result, err = api_post("/api/requirements/calculate", {
            "zone_name": req_zone, "exposed_population": exposed, "relief_days": days,
            "disaster_label": "DASHBOARD-SESSION",
        })
        if err:
            st.error(err)
        else:
            st.session_state["last_requirements"] = result

    if "last_requirements" in st.session_state:
        reqs = st.session_state["last_requirements"]["requirements"]
        cols = st.columns(len(reqs))
        for col, r in zip(cols, reqs):
            col.metric(r["resource_type"], f"{r['net_requirement']:,.0f} {r['unit']}",
                       help=r["assumptions"]["formula"])
        with st.expander("Why these quantities? (full formula)"):
            for r in reqs:
                st.markdown(f"**{r['resource_type']}**: {r['assumptions']['formula']}")

    st.divider()
    st.subheader("Priority engine — explainable zone ranking")
    st.caption("Add 2+ zones to compare, then compute. Requires DISTRICT_OFFICER or SUPER_ADMIN login.")

    st.session_state.setdefault("priority_zone_rows", [])
    with st.form("add_priority_zone"):
        c1, c2, c3, c4, c5 = st.columns(5)
        z_name = c1.selectbox("Zone", district_names, key="pz_name")
        z_risk = c2.selectbox("Risk level", ["low", "moderate", "high", "severe"], key="pz_risk")
        z_pop = c3.number_input("Population exposed", 0, 5_000_000, 10000, key="pz_pop")
        z_gross = c4.number_input("Gross requirement", 0.0, value=1000.0, key="pz_gross")
        z_net = c5.number_input("Net requirement", 0.0, value=500.0, key="pz_net")
        c6, c7 = st.columns(2)
        z_urgency = c6.slider("Urgency (ASSUMPTION — no forecast-horizon feed)", 0.0, 1.0, 0.5, key="pz_urgency")
        z_access = c7.slider("Accessibility (ASSUMPTION — no road-network feed)", 0.0, 1.0, 0.5, key="pz_access")
        if st.form_submit_button("Add zone to comparison"):
            st.session_state["priority_zone_rows"].append({
                "zone_name": z_name, "risk_level": z_risk, "population_exposed": z_pop,
                "gross_requirement": z_gross, "net_requirement": z_net,
                "urgency": z_urgency, "accessibility_score": z_access,
            })

    if st.session_state["priority_zone_rows"]:
        st.dataframe(pd.DataFrame(st.session_state["priority_zone_rows"]), use_container_width=True, hide_index=True)
        col_a, col_b = st.columns(2)
        if col_a.button("Clear zones"):
            st.session_state["priority_zone_rows"] = []
            st.rerun()
        if col_b.button("Compute priorities", type="primary"):
            if not TOKEN:
                st.error("Log in as district_officer or admin first (sidebar).")
            else:
                result, err = api_post(
                    "/api/priorities/compute",
                    {"disaster_label": "DASHBOARD-SESSION", "zones": st.session_state["priority_zone_rows"]},
                    token=TOKEN,
                )
                if err:
                    st.error(err)
                else:
                    st.session_state["last_priorities"] = result

    if "last_priorities" in st.session_state:
        for p in st.session_state["last_priorities"]:
            with st.container():
                st.markdown(f'<div class="setu-card"><b>#{p["rank"]} {p["zone_name"]}</b> — '
                            f'priority score <b>{p["priority_score"]}</b></div>', unsafe_allow_html=True)
                term_df = pd.DataFrame(p["explanation"]["terms"])
                st.dataframe(term_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# TAB: Allocation (NEW)
# ---------------------------------------------------------------------------
with tab_allocation:
    st.subheader("Resource allocation recommendation")
    st.caption("Not just nearest-warehouse — accessibility can make a farther warehouse win. "
               "Requires DISTRICT_OFFICER/SUPER_ADMIN login to recommend or approve.")

    warehouses, werr = api_get("/api/warehouses")
    if werr:
        st.error(werr)
    elif not warehouses:
        st.warning("No warehouses seeded yet — run `python scripts/seed_demo.py`.")
    else:
        if not st.session_state.get("last_priorities"):
            st.info("Compute priorities in the previous tab first, so zones here have a zone_id and priority_score.")
        else:
            zone_options = {f'{p["zone_name"]} (priority {p["priority_score"]})': p for p in st.session_state["last_priorities"]}
            chosen_label = st.selectbox("Zone needing resources", list(zone_options.keys()))
            chosen_zone = zone_options[chosen_label]
            resource_type = st.selectbox("Resource type", ["water_litres", "food_kg", "medical_kits", "shelter_units"])
            quantity_needed = st.number_input("Quantity needed (net requirement)", 0.0, value=1000.0)

            zone_meta = next((d for d in districts if d["name"] == chosen_zone["zone_name"]), None)

            st.markdown("**Warehouses** (accessibility is an ASSUMPTION slider — no live road-closure feed in this prototype)")
            warehouse_rows = []
            for w in warehouses:
                distance = haversine_km(w["lat"], w["lon"], zone_meta["centroid"]["lat"], zone_meta["centroid"]["lon"]) if zone_meta else 0
                stock = next((i["quantity_available"] for i in w["inventory"] if i["resource_type"] == resource_type), 0)
                c1, c2, c3, c4 = st.columns([3, 1, 1, 2])
                c1.write(f"**{w['name']}**")
                c2.write(f"{distance} km")
                c3.write(f"stock: {stock:,.0f}")
                access = c4.slider("accessibility", 0.0, 1.0, 0.6, key=f"acc_{w['id']}", label_visibility="collapsed")
                warehouse_rows.append({"warehouse_id": w["id"], "resource_type": resource_type, "distance_km": distance, "accessibility_score": access})

            if st.button("Get allocation recommendation", type="primary"):
                if not TOKEN:
                    st.error("Log in as district_officer or admin first (sidebar).")
                else:
                    result, err = api_post("/api/allocations/recommend", {
                        "resource_type": resource_type,
                        "zones": [{"zone_id": chosen_zone["zone_id"], "quantity_needed": quantity_needed, "priority_score": chosen_zone["priority_score"]}],
                        "warehouses": warehouse_rows,
                    }, token=TOKEN)
                    if err:
                        st.error(err)
                    else:
                        st.session_state["last_recommendation"] = result

            if "last_recommendation" in st.session_state:
                rec = st.session_state["last_recommendation"]
                st.markdown(f"**Method used:** `{rec['method']}`")
                for line in rec["lines"]:
                    with st.container():
                        st.markdown(f'<div class="setu-card">'
                                    f'<b>{line["quantity"]:,.0f} {line["resource_type"]}</b> '
                                    f'FROM warehouse #{line["warehouse_id"]} TO zone #{line["zone_id"]}<br>'
                                    f'<i>WHY: {line["reasoning"]}</i></div>', unsafe_allow_html=True)
                        if st.button(f"✅ Approve this allocation", key=f"approve_{line['warehouse_id']}_{line['zone_id']}"):
                            approval, aerr = api_post("/api/allocations/approve", {
                                "warehouse_id": line["warehouse_id"], "zone_id": line["zone_id"],
                                "resource_type": resource_type, "quantity": line["quantity"],
                                "distance_km": line["distance_km"], "accessibility_score": line["accessibility_score"],
                                "reasoning": line["reasoning"], "allocation_method": rec["method"],
                            }, token=TOKEN)
                            if aerr:
                                st.error(aerr)
                            else:
                                st.success(f"Allocation #{approval['allocation_id']} approved — {approval['blockchain_note']}")
                for excl in rec["excluded_warehouses"]:
                    st.warning(f"Excluded: {excl['warehouse_name']} — {excl['reason']}")

# ---------------------------------------------------------------------------
# TAB: Deliveries & Discrepancies (NEW)
# ---------------------------------------------------------------------------
with tab_deliveries:
    st.subheader("Dispatch → receipt → verification")
    allocations, aerr = api_get("/api/allocations")
    if aerr:
        st.error(aerr)
    elif not allocations:
        st.info("No allocations yet.")
    else:
        for a in allocations:
            with st.container():
                status_kind = {"ALLOCATED": "moderate", "DISPATCHED": "moderate", "VERIFIED": "low", "DISCREPANCY": "critical"}.get(a["status"], "moderate")
                st.markdown(f'<div class="setu-card">Allocation #{a["id"]} — {a["resource_type"]} — '
                            f'{badge(a["status"], status_kind)} '
                            f'(recommended {a["quantity_recommended"]:,.0f}, dispatched {a["quantity_dispatched"] or "-"}, received {a["quantity_received"] or "-"})'
                            f'</div>', unsafe_allow_html=True)
                cols = st.columns(3)
                if a["status"] == "ALLOCATED":
                    qty = cols[0].number_input("Quantity to dispatch", 0.0, value=float(a["quantity_recommended"]), key=f"dispatch_qty_{a['id']}")
                    if cols[0].button("Dispatch", key=f"dispatch_{a['id']}"):
                        result, err = api_post("/api/deliveries/dispatch", {"allocation_id": a["id"], "quantity_dispatched": qty}, token=TOKEN)
                        if err:
                            st.error(err)
                        else:
                            st.success(f"Dispatched. {result['blockchain_note']}")
                            st.rerun()
                elif a["status"] == "DISPATCHED":
                    qty = cols[1].number_input("Quantity received", 0.0, value=float(a["quantity_dispatched"] or 0), key=f"confirm_qty_{a['id']}")
                    if cols[1].button("Confirm receipt", key=f"confirm_{a['id']}"):
                        result, err = api_post("/api/deliveries/confirm", {"allocation_id": a["id"], "quantity_received": qty}, token=TOKEN)
                        if err:
                            st.error(err)
                        else:
                            if result["status"] == "VERIFIED":
                                st.success(f"VERIFIED. {result['blockchain_note']}")
                            else:
                                st.warning(f"DISCREPANCY detected — difference {result['difference']}. {result['blockchain_note']}")
                            st.rerun()

    st.divider()
    st.subheader("Discrepancies")
    discrepancies, derr = api_get("/api/deliveries/discrepancies")
    if derr:
        st.error(derr)
    elif not discrepancies:
        st.info("No discrepancies recorded.")
    else:
        for d in discrepancies:
            kind = "critical" if d["status"] == "OPEN" else "low"
            st.markdown(f'<div class="setu-card">Discrepancy #{d["id"]} (allocation #{d["allocation_id"]}) — {badge(d["status"], kind)}<br>'
                        f'expected {d["expected_quantity"]:,.0f}, received {d["received_quantity"]:,.0f}, '
                        f'difference {d["difference"]:,.0f} — reported by {d["reported_by"]}</div>', unsafe_allow_html=True)
            if d["status"] == "OPEN":
                note = st.text_input("Resolution note", key=f"resolve_note_{d['id']}")
                if st.button("Resolve", key=f"resolve_{d['id']}"):
                    if not TOKEN:
                        st.error("Log in as district_officer/auditor/admin first.")
                    else:
                        result, err = api_post("/api/deliveries/discrepancies/resolve", {"discrepancy_id": d["id"], "resolution_note": note or "Resolved via dashboard"}, token=TOKEN)
                        if err:
                            st.error(err)
                        else:
                            st.success("Resolved.")
                            st.rerun()

# ---------------------------------------------------------------------------
# TAB: Audit & Data Sources (NEW)
# ---------------------------------------------------------------------------
with tab_audit:
    st.subheader("Blockchain transaction mirror")
    chain_txs, cerr = api_get("/api/audit/blockchain/transactions")
    if cerr:
        st.error(cerr)
    elif chain_txs:
        st.dataframe(pd.DataFrame(chain_txs), use_container_width=True, hide_index=True)
    else:
        st.info("No on-chain transactions recorded yet.")

    st.subheader("Internal audit log")
    st.caption("Requires DISTRICT_OFFICER/AUDITOR/SUPER_ADMIN login.")
    if not TOKEN:
        st.warning("Log in to view the audit log.")
    else:
        audit_log, aerr = api_get("/api/audit", token=TOKEN)
        if aerr:
            st.error(aerr)
        elif audit_log:
            st.dataframe(pd.DataFrame(audit_log), use_container_width=True, hide_index=True)
        else:
            st.info("No audit events yet.")

    st.divider()
    st.subheader("Data provenance — what's REAL vs. SYNTHETIC")
    sources, serr = api_get("/api/data-sources")
    if serr:
        st.error(serr)
    else:
        for s in sources:
            st.markdown(f'<div class="setu-card">{badge(s["category"])} <b>{s["name"]}</b><br>'
                        f'<span style="color:#8b949e">{s["source"]}</span><br>'
                        f'{s["limitations"]}</div>', unsafe_allow_html=True)
