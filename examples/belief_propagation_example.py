"""
Production belief propagation demo for Ranked Programming

What this demo shows
--------------------
- A diagnostic network (Disease→{Fever,Cough} with Fever↔Cough confounding)
    to illustrate how evidence updates beliefs under Ranking Theory (Spohn κ):
    κ=0 means not disbelieved (expected), higher κ means more disbelieved.
- The production Shenoy-style message passing implementation and its caches:
    messages_fv (factor→var) and messages_vf (var→factor).
- Convergence metadata via `_message_cache` (iterations, converged, edge counts).

Why this is demo'd
------------------
- To give users a small, concrete example of κ-based inference where evidence
    (Fever=fever, Cough=cough) increases belief in Disease=infected as expected.
- To show the exact production data exposed by the algorithm for debugging
    and observability (message caches and iteration counts).
- To provide a quick chain network “smoke test” of convergence behavior.

How to read the output
----------------------
- Lines like `value→κ` show the disbelief rank κ for that value. Lower is better;
    0 is the minimum after normalization (most plausible). Higher κ means more
    surprising/less plausible.
- `_message_cache`: `iterations` is how many sweeps the schedule ran; `converged`
    indicates messages stabilized before hitting the cap; `fv_edges`/`vf_edges` are
    the number of message edges.
- Message caches:
    - messages_fv[(factor_vars, var)] is the factor→variable message: the factor
        sends evidence about the variable's values.
    - messages_vf[(var, factor_vars)] is the variable→factor message: the variable
        aggregates other inbound messages and sends to the factor.
"""

from ranked_programming.ranking_class import Ranking
from ranked_programming.ranking_combinators import nrm_exc
from ranked_programming.belief_propagation import BeliefPropagationNetwork, create_chain_network


def show_marginal(r: Ranking, limit: int = 4) -> str:
    """Render the first few value→κ pairs of a Ranking for compact display.

    κ (kappa) is Spohn’s disbelief rank. 0 is minimal disbelief (not surprising),
    higher is more disbelieved. We normalize marginals so their min κ is 0.
    """
    items = list(r)
    parts = [f"{v}→{k}" for v, k in items[:limit]]
    if len(items) > limit:
        parts.append("…")
    return " ".join(parts)


def demo_diagnostic_with_caches():
    """Demonstrate inference, evidence effects, and caches on a small diagnostic model.

    Model:
    - Disease prior is neutral (healthy vs infected both κ=0 before evidence).
    - Two symptom factors (Fever, Cough) depend on Disease with complete tables.
    - A confounding factor links Fever and Cough (they tend to co-occur).

    What to look for:
    - With evidence Fever=fever and Cough=cough, Disease=infected should have κ=0
      (higher plausibility) while healthy is more disbelieved (higher κ).
    - `_message_cache` shows the iteration count and convergence status.
    - Sample messages show actual factor→var and var→factor message contents.
    """
    print("=== Diagnostic network with caches ===\n")

    # Disease → {Fever, Cough}; Fever↔Cough confounding; neutral prior
    def disease_fever():
        yield (("healthy", "no_fever"), 0)
        yield (("infected", "fever"), 0)
        yield (("healthy", "fever"), 2)
        yield (("infected", "no_fever"), 2)

    def disease_cough():
        yield (("healthy", "no_cough"), 0)
        yield (("infected", "cough"), 0)
        yield (("healthy", "cough"), 2)
        yield (("infected", "no_cough"), 2)

    def fever_cough():
        yield (("no_fever", "no_cough"), 0)
        yield (("fever", "cough"), 0)
        yield (("no_fever", "cough"), 1)
        yield (("fever", "no_cough"), 1)

    factors = {
        ("Disease",): Ranking(lambda: nrm_exc("healthy", "infected", 0)),
        ("Disease", "Fever"): Ranking(disease_fever),
        ("Disease", "Cough"): Ranking(disease_cough),
        ("Fever", "Cough"): Ranking(fever_cough),
    }

    net = BeliefPropagationNetwork(factors)

    # No evidence: inspect baseline marginals and runtime metadata.
    marg = net.propagate_beliefs()
    print("No evidence marginals:")
    for v in ["Disease", "Fever", "Cough"]:
        print(f"  {v}: {show_marginal(marg[v])}")
    print("Cache summary:")
    print(f"  iterations={net._message_cache.get('iterations')} converged={net._message_cache.get('converged')}")
    print(f"  fv_edges={net._message_cache.get('fv_count')} vf_edges={net._message_cache.get('vf_count')}")
    print()

    # Evidence: fever and cough observed (hard conditioning via observe).
    # Interpretation: Disease=infected becomes less disbelieved (κ small/0)
    # than healthy, reflecting expected causal influence.
    ev = {"Fever": lambda x: x == "fever", "Cough": lambda x: x == "cough"}
    marg = net.propagate_beliefs(ev)
    print("With evidence (Fever=fever, Cough=cough):")
    for v in ["Disease", "Fever", "Cough"]:
        print(f"  {v}: {show_marginal(marg[v])}")

    # Inspect a couple of messages from caches
    # Factor→Var: message from a factor node into a variable node.
    # Read as: how the factor's constraints/evidence weigh the variable's values.
    if net.messages_fv:
        (ft, var), msg = next(iter(net.messages_fv.items()))
        print(f"Sample f→v message {ft}→{var}: {show_marginal(msg)}")
    # Var→Factor: message from a variable node into a factor node.
    # Read as: the variable aggregates all other inbound messages (except the
    # recipient factor) and sends its current belief to that factor.
    if net.messages_vf:
        (var, ft), msg = next(iter(net.messages_vf.items()))
        print(f"Sample v→f message {var}→{ft}: {show_marginal(msg)}")

    print()


def demo_chain_with_metadata():
    """Quick smoke test: chain topology + convergence metadata.

    Why a chain?
    - Simple, sparse structure where propagation converges quickly.
    - Useful to sanity check the schedule and iteration behavior.

    What is shown:
    - `_message_cache` iterations and convergence flag after propagation.
    - A few variable marginals to confirm the pipeline is producing output.

    How to read:
    - Iterations is typically small for short chains; `Converged=True` indicates
      messages stabilized before `max_iterations`.
    - Marginal lines are trimmed; κ=0 is most plausible after normalization.
    """
    print("=== Chain network with convergence metadata ===\n")
    net = create_chain_network(5)
    marg = net.propagate_beliefs(max_iterations=10)
    print("Variables:", ", ".join(sorted(net.variables)))
    print(f"Iterations={net._message_cache.get('iterations')} Converged={net._message_cache.get('converged')}")
    # Helper to focus on values for the specific variable
    def head_for_var(var: str, r: Ranking, limit: int = 4) -> str:
        items = [(v, k) for v, k in list(r) if isinstance(v, str) and v.startswith(f"{var}_")]
        if not items:  # fallback to generic view
            return show_marginal(r, limit)
        parts = [f"{v}→{k}" for v, k in items[:limit]]
        if len(items) > limit:
            parts.append("…")
        return " ".join(parts)

    # Show head of a couple marginals
    for v in ["X0", "X2", "X4"]:
        if v in marg:
            print(f"  {v}: {head_for_var(v, marg[v])}")
    print()


def main():
    print("Ranked Programming belief propagation (production demo)\n")
    demo_diagnostic_with_caches()
    demo_chain_with_metadata()


if __name__ == "__main__":
    main()
