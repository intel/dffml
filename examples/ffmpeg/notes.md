* dffml service dev create operations ffmpeg
* write operations and definitions
* change setup.py
*
    ```
    pip install -e .

    cat > /tmp/operations/ <<EOF
    convert_to_gif
    EOF

    dffml dataflow create -config yaml $(cat /tmp/operations) > deploy/df/ffmpeg.yaml

    cd ffmpeg
    mkdir -p deploy/mc/http
        ffmpeg.yaml
        path: /ffmpeg
        presentation: json
        asynchronous: false

    dffml service http server -insecure -mc-config deploy

    ```

* curl -s \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{"convert": [{"value":"input.mp4","definition":"input_file"},{"value":"output.gif","definition":"output_file"}]}' \
  http://localhost:8080/ffmpeg

  works!!!

  * docker run -p 8002:8080 -v ~/buffer:/usr/src/app/data -cvt_gif
  * curl -s \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{"convert": [{"value":"./data/input1.mp4","definition":"input_file"},{"value":"./data/output.gif","definition":"output_file"}]}' \
  http://localhost:8002/ffmpeg
