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


https://developer.github.com/v3/activity/events/types/#pushevent

*
    ```
    pip install -e .

    cat > /tmp/operations/ <<EOF
    get_payload
    get_url_from_payload
    check_if_default_branch
    get_image_tag
    docker_build_image
    restart_running_containers_by_tag
    EOF



    cd ffmpeg
    mkdir  deploy/webhook/mc/http
    mkdir deploy/webhook/df

    dffml dataflow create -config yaml $(cat /tmp/operations) > deploy/webhook/df/webhook.yaml


    dffml service http server -insecure -mc-config deploy/webhook

  ```
aghinsa/deploy_test_cvt_gif

  curl -s \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{"ref":"refs/master","repository":{"clone_url":"https://github.com/aghinsa/deploy_test_cvt_gif.git","default_branch":"master","html_url":"https://github.com/aghinsa/deploy_test_cvt_gif"}}' \
  http://localhost:8082/webhook/github

    curl -s \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{"tag":"aghinsa/deploy_test_cvt_gif"}' \
  http://localhost:8082/webhook/github