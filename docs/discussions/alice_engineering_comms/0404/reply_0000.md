- https://docs.deno.com/runtime/manual/tools/jupyter
- https://docs.deno.com/runtime/manual/tools/vendor
- https://docs.deno.com/runtime/manual/tools/compiler

```bash
set -x
mkdir -p src/
cat > src/main.ts <<'EOF'
const inputs = await Deno.readTextFile(Deno.args[0]);
console.log(JSON.parse(inputs));
EOF
cat > action.yml <<'EOF'
name: 'My Cool Action'
description: 'My Cool Action'
inputs:
  key:
    description: 'description'
    required: false
    default: "value"
runs:
  using: "composite"
  steps:
    - if: runner.os == 'Windows' && runner.arch == 'X64'
      shell: ${{ github.action_path }}/dist/x86_64-pc-windows-msvc.exe {0}
      run: ${{ toJSON(inputs) }}
    - if: runner.os == 'Linux' && runner.arch == 'X64'
      shell: ${{ github.action_path }}/dist/x86_64-unknown-linux-gnu {0}
      run: ${{ toJSON(inputs) }}
    - if: runner.os == 'macOS' && runner.arch == 'X64'
      shell: ${{ github.action_path }}/dist/x86_64-apple-darwin {0}
      run: ${{ toJSON(inputs) }}
    - if: runner.os == 'macOS' && runner.arch == 'ARM64'
      shell: ${{ github.action_path }}/dist/aarch64-apple-darwin {0}
      run: ${{ toJSON(inputs) }}
EOF
mkdir -p .github/workflows/
cat > .github/workflows/test.yml <<'EOF'
name: "Test My Cool Action"

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os:
        - ubuntu-latest
        - windows-latest
        - macos-latest
    steps:
    - uses: actions/checkout@v4
    - uses: './'
EOF
export DENO_TARGETS=( $(deno compile --help 2>&1 | grep x86_ | sed -e 's/.*possible values: //' -e 's/]//' -e 's/,//g') )
for target in ${DENO_TARGETS[@]}; do deno compile --allow-all --target "${target}" --output "dist/${target}" src/main.ts; done
git commit -sm 'Initial Commit'
git add src/ .github/ action.yml
gh act -s GITHUB_TOKEN="$(gh auth token)" --job test -W .github/workflows/test.yml
```