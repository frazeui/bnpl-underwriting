# BNPL Underwriting Agent

A Tamara-style Buy Now Pay Later underwriting system.

- **Real-time decision engine:** ML risk model + rules decide approve / decline /
  step-up / refer in under 300 ms. No LLM on the checkout path.
- **Agentic layer (LangGraph):** case review, merchant underwriting, limit review,
  and decision explanations, with human-in-the-loop review.
- **Platform:** Kubernetes (k3d) + Helm, MLflow, Langfuse, Streamlit.

## Status
- [x] Phase 0: infrastructure (k3d, Helm, repo)
- [x] Phase 0: credit policy v1
- [ ] Phase 0: data simulator
- [ ] Phase 1: decision engine
- [ ] Phase 3: agents
- [ ] Phase 5: LLMOps
