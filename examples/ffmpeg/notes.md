* dffml service dev create operations ffmpeg
* write operations and definitions
* change setup.py
* 
    ```
    pip install -e .

    cat > /tmp/operations/ <<EOF
    convert_to_gif
    EOF

    dffml dataflow create -config yaml $(cat /tmp/operations) > dataflow.yaml

    

    ```
