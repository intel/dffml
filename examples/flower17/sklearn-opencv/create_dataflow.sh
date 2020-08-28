dffml dataflow \
    create \
        resize \
        calcHist \
        Haralick \
        HuMoments \
        gray=convert_color \
        hsv=convert_color \
        flatten \
        normalize \
        get_single \
    -configloader yaml \
    -inputs \
        '[500,500,3]'=resize.inputs.dsize \
        '[0,1,2]'=calcHist.inputs.channels \
        'None'=calcHist.inputs.mask \
        '[8,8,8]'=calcHist.inputs.histSize \
        '[0,256,0,256,0,256]'=calcHist.inputs.ranges \
        BGR2GRAY=convert_color.inputs.code=gray \
        BGR2HSV=convert_color.inputs.code=hsv \
        '[{"Histogram": "flatten.outputs.result"},{"HuMoments": "HuMoments.outputs.result"},{"Haralick": "Haralick.outputs.result"}]'=get_single_spec \
    -flow \
        '[{"seed": ["image"]}]'=resize.inputs.src \
        '[{"resize": "result"}]'=hsv.inputs.src \
        '["hsv"]'=hsv.inputs.code \
        '[{"hsv": "result"}]'=calcHist.inputs.images \
        '[{"calcHist": "result"}]'=normalize.inputs.src \
        '[{"normalize": "result"}]'=flatten.inputs.array \
        '[{"resize": "result"}]'=gray.inputs.src \
        '["gray"]'=gray.inputs.code \
        '[{"gray": "result"}]'=HuMoments.inputs.m \
        '[{"resize": "result"}]'=Haralick.inputs.f |
    tee features.yaml