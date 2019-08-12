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

RUN \
  wget http://apache.mirrors.tds.net/hadoop/common/hadoop-3.1.2/hadoop-3.1.2.tar.gz && \
  tar -xzf hadoop-3.1.2.tar.gz && \
  rm -rf hadoop-3.1.2.tar.gz && \
  mv hadoop-3.1.2 /usr/local && \
  ln -sf /usr/local/hadoop-3.1.2/ /usr/local/hadoop

ADD configs/hadoop_config /usr/local/hadoop
CMD cat /usr/local/hadoop/hadoop_config >> ~/.bashrc

CMD bash ~/.bashrc

# copy hadoop configs
ADD configs/*xml $HADOOP_HOME/etc/hadoop/

# copy script to start hadoop
ADD start-hadoop.sh start-hadoop.sh

# expose various ports
EXPOSE 9000 8088 50070 50075 50030 50060

# start hadoop
RUN chmod a+x /start-hadoop.sh
CMD bash start-hadoop.sh
