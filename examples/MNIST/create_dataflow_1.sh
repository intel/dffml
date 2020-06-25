dffml dataflow create resize flatten multiply associate_definition -configloader yaml \
    -seed \
      '[28,28]'=resize.inputs.dsize \
      '{"image": "product"}'=associate_spec \
      0.00392156862=multiplier_def \
    -flow \
      '[{"seed": ["image"]}]'=resize.inputs.src \
      '[{"resize": "result"}]'=flatten.inputs.array \
      '[{"flatten": "result"}]'=multiply.inputs.multiplicand |
    tee resizenorm.yaml