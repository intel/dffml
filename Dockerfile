FROM python:3.11-buster@sha256:3a19b4d6ce4402d11bb19aa11416e4a262a60a57707a5cda5787a81285df2666

# ========================== BEGIN DOCKER SETUP ================================
#
# Docker related setup

# Tell apt that we can't answer it's questions if it has any (time zone is a
# common one)
ENV DEBIAN_FRONTEND noninteractive

# The version of python we're using in pyXY format (changes with base image)
ARG PYTHON_SHORT_VERSION=py37
ENV PYTHON_SHORT_VERSION ${PYTHON_SHORT_VERSION}

# Set current working directory
WORKDIR /usr/src/dffml

# Update existing packages
RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# ==========================  END  DOCKER SETUP ================================


# ========================== BEGIN GLOBAL DEPENDENCIES =========================
#
# Dependencies that are applicable to the main package and plugins, or just must
# be installed first.

# Install and upgrade
# pip and setuptools, which are used to install other packages
# twine, which is used to upload released packages to PyPi
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install --upgrade twine

# ==========================  END  GLOBAL DEPENDENCIES =========================


# ====================== BEGIN NON PYTHON DEPENDENCIES =========================
#
# Dependencies for specific plugins that cannot be installed with pip

# feature/git
# operations/deploy
RUN curl -o /tmp/tokei.tar.gz -L 'https://github.com/XAMPPRocky/tokei/releases/download/v12.0.4/tokei-x86_64-unknown-linux-gnu.tar.gz' && \
  sha384sum /tmp/tokei.tar.gz | grep "^60ea048eca4d5e9f413400a561c775ccd21ffb63e3d15cc60703156bd634eb4c3ddec3bd8e8b8aabdaf97bb9b8d0ec11" && \
  tar xvzf /tmp/tokei.tar.gz -C "/usr/bin/" && \
  rm /tmp/tokei.tar.gz && \
  apt-get update && \
  apt-get install -y \
    git \
    subversion \
    cloc \
    openssl && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# ======================  END  NON PYTHON DEPENDENCIES =========================


# ========================== BEGIN INSTALL DEPENDENCIES ========================
#
# Dependencies which must be installed prior to installing a plugin. If a plugin
# requires something be installed, it must also ensure that those dependencies
# get installed when we are running the tests for the main package (.) or the
# docs (docs). Each if statement seen here will check if we are running tests
# for the plugin, main package, or docs, and install if any of those conditions
# are true.

# model/autosklearn
# .
# docs
RUN apt-get update && \
  apt-get install -y \
    build-essential \
    swig && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  python -m pip install pyrfr==0.9.0 cython==3.0.10 --hash=sha256:bc6e758317cf79579fe6b7ce5f01dd42f77c991bf707e33646e8c6a9112c186b --hash=sha256:dcc96739331fb854dcf503f94607576cfe8488066c61ca50dfd55836f132de99 --hash=sha256:fcbb679c0b43514d591577fd0d20021c55c240ca9ccafbdb82d3fb95e5edfee2 --hash=sha256:81f356c1c8c0885b8435bfc468025f545c5d764aa9c75ab662616dd1193c331e --hash=sha256:0bac3ccdd4e03924028220c62ae3529e17efa8ca7e9df9330de95de02f582b26 --hash=sha256:8c9c4c4f3ab8f8c02817b0e16e8fa7b8cc880f76e9b63fe9c010e60c1a6c2b13 --hash=sha256:4f610964ab252a83e573a427e28b103e2f1dd3c23bee54f32319f9e73c3c5499 --hash=sha256:d10fc9aa82e5e53a0b7fd118f9771199cddac8feb4a6d8350b7d4109085aa775 --hash=sha256:651a15a8534ebfb9b58cb0b87c269c70984b6f9c88bfe65e4f635f0e3f07dfcd --hash=sha256:64f1f8bba9d8f37c0cffc934792b4ac7c42d0891077127c11deebe9fa0a0f7e4 --hash=sha256:077b61ee789e48700e25d4a16daa4258b8e65167136e457174df400cf9b4feab --hash=sha256:950c0c7b770d2a7cec74fb6f5ccc321d0b51d151f48c075c0d0db635a60ba1b5 --hash=sha256:35f6ede7c74024ed1982832ae61c9fad7cf60cc3f5b8c6a63bb34e38bc291936 --hash=sha256:fc6e0faf5b57523b073f0cdefadcaef3a51235d519a0594865925cadb3aeadf0 --hash=sha256:2c9c1e3e78909488f3b16fabae02308423fa6369ed96ab1e250807d344cfffd7 --hash=sha256:8adcde00a8a88fab27509b558cd8c2959ab0c70c65d3814cfea8c68b83fa6dcd --hash=sha256:acfbe0fff364d54906058fc61f2393f38cd7fa07d344d80923937b87e339adcf --hash=sha256:0e9a885ec63d3955a08cefc4eec39fefa9fe14989c6e5e2382bd4aeb6bdb9bc3 --hash=sha256:f43a58bf2434870d2fc42ac2e9ff8138c9e00c6251468de279d93fa279e9ba3b --hash=sha256:40fac59c3a7fbcd9c25aea64c342c890a5e2270ce64a1525e840807800167799 --hash=sha256:d4e83a8ceff7af60064da4ccfce0ac82372544dd5392f1b350c34f1b04d0fae6 --hash=sha256:269f06e6961e8591d56e30b46e1a51b6ccb42cab04c29fa3b30d3e8723485fb4 --hash=sha256:076e9fd4e0ca33c5fa00a7479180dbfb62f17fe928e2909f82da814536e96d2b --hash=sha256:b74b700d6a793113d03fb54b63bdbadba6365379424bac7c0470605672769260 --hash=sha256:a181144c2f893ed8e6a994d43d0b96300bc99873f21e3b7334ca26c61c37b680 --hash=sha256:15b6d397f4ee5ad54e373589522af37935a32863f1b23fa8c6922adf833e28e2 --hash=sha256:206e803598010ecc3813db8748ed685f7beeca6c413f982df9f8a505fce56563 --hash=sha256:a9bb402674788a7f4061aeef8057632ec440123e74ed0fb425308a59afdfa10e --hash=sha256:a9c976e9ec429539a4367cb4b24d15a1e46b925976f4341143f49f5f161171f5 --hash=sha256:90e2f514fc753b55245351305a399463103ec18666150bb1c36779b9862388e9 --hash=sha256:32fbad02d1189be75eb96456d9c73f5548078e5338d8fa153ecb0115b6ee279f --hash=sha256:f4780d0f98ce28191c4d841c4358b5d5e79d96520650910cd59904123821c52d --hash=sha256:9fa9e7786083b6aa61594c16979d621b62e61fcd9c2edd4761641b95c7fb34b2 --hash=sha256:4fadb84193c25641973666e583df8df4e27c52cdc05ddce7c6f6510d690ba34a --hash=sha256:5f465443917d5c0f69825fca3b52b64c74ac3de0143b1fff6db8ba5b48c9fb4a --hash=sha256:6c5af936940a38c300977b81598d9c0901158f220a58c177820e17e1774f1cf1 --hash=sha256:2d29e617fd23cf4b83afe8f93f2966566c9f565918ad1e86a4502fe825cc0a79 --hash=sha256:f8a2b8fa0fd8358bccb5f3304be563c4750aae175100463d212d5ea0ec74cbe0 --hash=sha256:a5e14a8c6a8157d2b0cdc2e8e3444905d20a0e78e19d2a097e89fb8b04b51f6b --hash=sha256:9cc6a0e7e23a96dec3f3c9d39690d4281beabd5297855140d0d30855f950275e --hash=sha256:5a036d00caa73550a3a976432ef21c1e3fa12637e1616aab32caded35331ae96 --hash=sha256:407840c56385b9c085826fe300213e0e76ba15d1d47daf4b58569078ecb94446 --hash=sha256:8f2864ab5fcd27a346f0b50f901ebeb8f60b25a60a575ccfd982e7f3e9674914 --hash=sha256:3919a55ec9b6c7db6f68a004c21c05ed540c40dbe459ced5d801d5a1f326a053 --hash=sha256:09f2000041db482cad3bfce94e1fa3a4c82b0e57390a164c02566cbbda8c4f12 --hash=sha256:bcc9795990e525c192bc5c0775e441d7d56d7a7d02210451e9e13c0448dba51b --hash=sha256:e8df79b596633b8295eaa48b1157d796775c2bb078f32267d32f3001b687f2fd --hash=sha256:5bd49a3a9fdff65446a3e1c2bfc0ec85c6ce4c3cad27cd4ad7ba150a62b7fb59 --hash=sha256:38d40fa1324ac47c04483d151f5e092406a147eac88a18aec789cf01c089c3f2 --hash=sha256:712760879600907189c7d0d346851525545484e13cd8b787e94bfd293da8ccf0 --hash=sha256:051069638abfb076900b0c2bcb6facf545655b3f429e80dd14365192074af5a4 --hash=sha256:9ea31184c7b3a728ef1f81fccb161d8948c05aa86c79f63b74fb6f3ddec860ec --hash=sha256:3cffb666e649dba23810732497442fb339ee67ba4e0be1f0579991e83fcc2436 --hash=sha256:d092c0ddba7e9e530a5c5be4ac06db8360258acc27675d1fc86294a5dc8994c5 --hash=sha256:86998b01f6a6d48398df8467292c7637e57f7e3a2ca68655367f13f66fed7734 --hash=sha256:541fbe725d6534a90b93f8c577eb70924d664b227a4631b90a6e0506d1469591 --hash=sha256:401aba1869a57aba2922ccb656a6320447e55ace42709b504c2f8e8b166f46e1 --hash=sha256:adc377aa33c3309191e617bf675fdbb51ca727acb9dc1aa23fc698d8121f7e23 --hash=sha256:e876272548d73583e90babda94c1299537006cad7a34e515a06c51b41f8657aa --hash=sha256:687c32f83e98894df296cf7fd5460f48e5c1dfa300b1d02f81cd71c0a282f185 --hash=sha256:b869b9bcf62d6df61bb2368c57f87db6113c5b6d468409292f3615dbe22f246c --hash=sha256:1d7697fffbcc6d1cf5787d082c52fe977eb08270d86540b8a5c0a38745d45338 --hash=sha256:eea6e82d44fb0509271b787553bd09d6c4424a21b96e42df45d5fd442545e83a --hash=sha256:86454bc52204bee18843cf00577aa909a89bc1e1cacc5e36d4f0df46b495afdf --hash=sha256:8a94521309f3f1871a778a83d3dee39da7d21ef418991587a84972ba15c61ab8 --hash=sha256:f632cf05d5e9a8a5cafc1e211a0c0dfbf2e3bf524bfc98657ca76a25d93bdd90 --hash=sha256:6d8b4f3159972475cd02bbc4488b465ea843629d600813b9116c4397157704ef --hash=sha256:4668033c33c95ba006a40328f3f6d9a34371e36dbcbd6a5405fba9b441db4fa5 --hash=sha256:20249bae50449ab02f41df580490e14d3e2f717fdcb4287ba26b2e05deef246a --hash=sha256:98ffb774b6b428b95c1b31520caab62479a74223e9bd8cc5144d1c3dda995598 liac-arff==2.5.0 --hash=sha256:3220d0af6487c5aa71b47579be7ad1d94f3849ff1e224af3bf05ad49a0b5c4da

# ==========================  END  INSTALL DEPENDENCIES ========================


# ========================== BEGIN INSTALL DEPENDENCIES ========================
#
# Here we install DFFML and all the plugins

# The release of dffml we're using, latest is the latest PyPi release, main is
# the main branch
ARG DFFML_RELEASE=latest
ENV DFFML_RELEASE ${DFFML_RELEASE}

# Copy over DFFML
COPY . /usr/src/dffml
# Install the correct version of DFFML
RUN /usr/src/dffml/.ci/dffml-install.sh

# Copy over entrypoint script
COPY scripts/docker-entrypoint.sh /usr/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]
