dffml dataflow create multiply associate_definition -configloader yaml \
    -seed '{"image": "product"}'=associate_spec 0.00392156862=multiplier_def | \
    sed -ze 's/multiplicand:\n      - seed/multiplicand:\n      - seed:\n        - image/g' | \
    tee normalize.yaml