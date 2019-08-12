FROM ubuntu:16.04

ENV HADOOP_HOME /usr/local/hadoop
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64

# install packages
RUN \
  apt-get update && apt-get install -y \
  ssh \
  rsync \
  vim \
  openjdk-8-jdk

# download and extract hadoop, set JAVA_HOME in hadoop-env.sh, update path
RUN \
  wget http://apache.mirrors.tds.net/hadoop/common/hadoop-3.1.2/hadoop-3.1.2.tar.gz && \
  tar -xzf hadoop-3.1.2.tar.gz && \
  rm -rf hadoop-3.1.2.tar.gz && \
  mv hadoop-3.1.2 /usr/local && \
  ln -sf /usr/local/hadoop-3.1.2/ /usr/local/hadoop \
  cat hadoop_config >> ~/.bashrc \

CMD bash ~/.bashrc
  ##echo "export JAVA_HOME=$JAVA_HOME" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh && \
  ##echo "PATH=$PATH:$HADOOP_HOME/bin" >> ~/.bashrc

##ssh setup
RUN \
    mkdir ~/.ssh \
    chmod 700 ~/.ssh \
    touch ~/.ssh/authorized_keys \
    chmod 600 ~/.ssh/authorized_keys \

## ssh key gen
RUN \
    ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys \
    chmod 600 ~/.ssh/authorized_keys \
    ssh-copy-id -i ~/.ssh/id_rsa.pub localhost \
    ssh localhost

# copy hadoop configs
ADD configs/*xml $HADOOP_HOME/etc/hadoop/

# copy script to start hadoop
ADD start-hadoop.sh start-hadoop.sh

# expose various ports
EXPOSE 9000 8088 50070 50075 50030 50060

# start hadoop
RUN chmod a+x /start-hadoop.sh
CMD bash start-hadoop.sh

## start hdfs
##RUN \
##    hdf namenode -format \
##    start-dfs.sh \
##    start-yarn.sh

# expose various ports
##EXPOSE 8000 9000 8088 50070 50075 50030 50060