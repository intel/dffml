dffml dataflow create resize multiply associate_definition -configloader yaml \
    -seed \
      '[280,280,3]'=resize.inputs.old_dim \
      '[28,28]'=resize.inputs.new_dim \
      '{"image": "product"}'=associate_spec \
      0.00392156862=multiplier_def \
    -flow \
      '[{"seed": ["image"]}]'=resize.inputs.data \
      '[{"resize": "result"}]'=multiply.inputs.multiplicand |
    tee resizenorm.yaml
