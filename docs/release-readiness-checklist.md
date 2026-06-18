# Release Readiness Checklist

Track public release work here. Mark items complete only after the change is
implemented and verified.

## Governance

- [x] Move release-readiness tracking into this dedicated document
- [x] Remove public branding, client names, and partner/source names from code, docs, fixtures, and package metadata

## Validation And Contracts

- [x] Enforce strict schema inputs (`extra="forbid"` where appropriate)
- [x] Enforce schema version compatibility explicitly
- [x] Propagate validation warnings into render results
- [x] Align public documentation with implemented behavior

## Rendering Correctness

- [ ] Fail closed on block rendering errors by default
- [x] Enforce template `allowed_blocks`
- [ ] Define and test empty-report behavior
- [ ] Escape and sanitize user-controlled text before ReportLab markup rendering
- [ ] Ensure all input blocks either render or raise a clear failure

## Images And Resource Safety

- [ ] Route image loading through validated utilities
- [ ] Restrict local image access to safe paths and reject traversal
- [ ] Add resource limits for large JSON payloads, large images, and oversized tables/charts
- [ ] Clean up temporary files created during base64 image handling
- [ ] Implement or remove unsupported remote-image claims

## Determinism And Output Quality

- [ ] Reduce non-deterministic PDF output where practical
- [ ] Add parsed-PDF verification beyond file-size/page-count checks
- [ ] Add visual or structural smoke coverage for all built-in components

## Packaging And Release

- [ ] Add a public `LICENSE` file
- [ ] Add release notes or changelog
- [ ] Add project metadata suitable for public PyPI release
- [ ] Verify clean wheel install in an isolated environment
- [ ] Verify supported Python versions in CI
- [ ] Run the full pre-commit pipeline successfully
