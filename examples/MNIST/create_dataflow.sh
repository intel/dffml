dffml dataflow create multiply associate_definition -configloader yaml \
    -inputs '{"image": "product"}'=associate_spec 0.00392156862=multiplier_def \
    -flow '[{"seed": ["image"]}]'=multiply.inputs.multiplicand |
    tee normalize.yaml