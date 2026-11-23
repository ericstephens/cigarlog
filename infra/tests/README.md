# Infrastructure Tests

## Prerequisites

- [OpenTofu](https://opentofu.org/docs/intro/install/) (`tofu` command) installed and on your `PATH`.
- AWS credentials are **not** required — the validate test runs with no backend and skips provider authentication.

## Running the tests

From the repo root:

```sh
bash infra/tests/validate_test.sh
```

Or make it executable first and run directly:

```sh
chmod +x infra/tests/validate_test.sh
infra/tests/validate_test.sh
```

## What the test does

1. `tofu init -backend=false` — downloads required providers without touching any remote state backend.
2. `tofu validate` — statically checks all `.tf` files in `infra/` for syntax and configuration errors.

The script exits `0` and prints `PASS: tofu validate` on success, or exits non-zero with a `FAIL:` message on error.

## Adding more tests

Place additional shell scripts in this directory following the `*_test.sh` naming convention.  A future CI step can glob `infra/tests/*_test.sh` and execute each one.
