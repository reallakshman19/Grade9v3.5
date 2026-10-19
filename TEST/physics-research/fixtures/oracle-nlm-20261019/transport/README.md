# PHY-NLM-P1-INPUTS-v1 transport

The ZIP in this directory is the exact 6,933,900-byte handoff. SHA-256: fbac2b680425802ce920008f71bebd1a6d6dffacb1605b8d3ab35a4fab78bd85.

It supplies runnable pinned bank-validator inputs, original PDFs, the original uploaded HTML and partial main context. It is NOT a full checkout or a replacement implementation.

## Download

Use the ZIP file's GitHub Raw/download URL at this exact commit. If the local container cannot resolve GitHub, use the connected GitHub app instead of repeating container DNS attempts.

## Connector-only fallback

Read manifest.json, then fetch the eleven base64/part-NNN.b64 files in manifest order with the GitHub file reader using this exact commit as ref. Each part is below 1 MB. Preserve the complete structured content in orchestration/local-file transfer; do not copy a truncated chat rendering or print the full base64 into the conversation.

Check each ASCII part's SHA-256 against the manifest. Concatenate parts in numeric order WITHOUT separators, then base64-decode the combined text once to PHY-NLM-P1-INPUTS-v1.zip. Check ZIP size and SHA-256 and ZIP integrity before extraction. The manifest identifies the exact member order and fragment lengths.

If the reader returns an outer base64 encoding for a part file, decode that outer transport first to recover the ASCII part; the assembled parts themselves encode the ZIP. Default UTF-8 file reads avoid this extra wrapper.

Successful blob upload and part readback establish input transport, not that the coding agent received it. The agent must record its own verified local receipt. All earlier P1 boundaries remain unchanged.
