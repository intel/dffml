echo "awaiting-forgejo";
until curl -I "${FORGEJO_SERVICE_ROOT}" > /dev/null 2>&1; do sleep 5; done;

echo "checking-if-forgejo-need-first-time-init";
query_params=$(python3 -c 'import sys, urllib.parse, yaml; print(urllib.parse.urlencode(yaml.safe_load(sys.stdin)))' < /usr/src/forgejo-init/requests/init.yaml);
curl -v -X POST --data-raw "${query_params}" "${FORGEJO_SERVICE_ROOT}";
echo "forgejo-first-time-init-complete";

CSRF_TOKEN=$(curl "${FORGEJO_SERVICE_ROOT}/user/sign_up" | grep csrfToken | awk '{print $NF}' | sed -e "s/'//g" -e 's/,//g');
query_params=$(sed -e "s/CSRF_TOKEN/\"${CSRF_TOKEN}\"/g" /usr/src/forgejo-init/requests/sign_up.yaml | python3 -c 'import sys, urllib.parse, yaml; print(urllib.parse.urlencode(yaml.safe_load(sys.stdin)))' <);
curl -v -X POST --data-raw "${query_params}" "${FORGEJO_SERVICE_ROOT}/user/sign_up";
echo "forgejo-user-sign-up-complete";

echo "forgejo-configured";
