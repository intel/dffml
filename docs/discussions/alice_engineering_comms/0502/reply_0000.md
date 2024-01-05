- https://pkg.go.dev/plugin#Plugin.Lookup

```golang
package loader

import (
  "plugin"

  "github.com/ossf/scorecard/probes"
)

// PluginProbeLoader loads custom probes built as plugins.
type PluginProbeLoader struct{}

// Load implements the ProbeLoader interface.
// It builds the probe Go code into a plugin and loads it.
func (l *PluginProbeLoader) Load(path string) (probes.Probe, error) {
  plug, err := plugin.Open(path)
  if err != nil {
    return nil, err
  }

  // Lookup the New method of the probe from the plugin
  newFunc, err := plug.Lookup("New")
  if err != nil {
    return nil, err
  }

  // Assert and cast the New func to the expected signature
  newProbe, ok := newFunc.(func() probes.Probe)
  if !ok {
    return nil, fmt.Errorf("invalid probe constructor")
  }

  // Create a new instance of the probe
  return newProbe(), nil
}

loader := &PluginProbeLoader{}

probe, err := loader.Load("/path/to/probe.go") 
if err != nil {
  // handle error
}

func New() probes.Probe {
  return &MyCustomProbe{} 
}

type MyCustomProbe struct{}
```