# Pulse runtime bundles

Pulse consumes the complete Headroom CLI and Python proxy through relocatable
runtime bundles built by `scripts/build_pulse_bundle.py`. Each build emits a ZIP
and a JSON manifest containing the exact source revision, host tuple, byte size,
SHA-256, and executable path.

Supported hosts are Windows x64, Linux x64 and ARM64, and macOS ARM64. macOS
Intel is excluded because Headroom requires ONNX Runtime 1.24 or newer and that
project does not publish a compatible wheel. Windows ARM64 is excluded because
`sqlite-vec`, which backs Headroom memory, does not publish a compatible
distribution. Pulse must fail open on those hosts; it must not silently build a
reduced Headroom runtime.

The workflow smoke-tests `headroom --version` before uploading either file.
Pulse additionally verifies the manifest and archive before activation.
