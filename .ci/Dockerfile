FROM ubuntu:16.04

ENV HADOOP_HOME /usr/local/hadoop

#java setup
RUN \
    apt purge openjdk* \
    add-apt-repository -y ppa:webupd8team/java \
    apt update \
    apt install -y oracle-java8-installer \
    echo "export JAVA_HOME=/usr" >> $HADOOP_HOME/etc/hadoop \
    ##source $HADOOP_HOME/etc/profile

#setup hadoopuser
RUN \
    addgroup hadoopgroup \
    adduser -ingroup hadoopgroup hadoopuser \
    apt install ssh \
    systemctl enable ssh \
    systemctl start ssh

##ssh setup
RUN \
    su - hadoopuser \
    echo "DIRECTORY SETUP STARTED" \
    mkdir ~/.ssh \
    chmod 700 ~/.ssh \
    touch ~/.ssh/authorized_keys \
    chmod 600 ~/.ssh/authorized_keys \
    echo "DIRECTORY SETUP DONE"

## ssh key gen
RUN \
    ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys \
    chmod 600 ~/.ssh/authorized_keys \
    ssh-copy-id -i ~/.ssh/id_rsa.pub localhost \
    ssh localhost

##download apache
RUN \
    wget http://it.apache.contactlab.it/hadoop/common/hadoop-3.1.2/hadoop-3.1.2.tar.gz \
    tar xzf hadoop-3.1.2.tar.gz \
    rm -rf hadoop-3.1.2.tar.gz \
    mv hadoop-3.1.2 /usr/local \
    ln -sf /usr/local/hadoop-3.1.2/ /usr/local/hadoop \
    chown -R hadoopuser:hadoopgroup /usr/local/hadoop-3.1.2/ \
    cat hadoop_config >> ~/.bashrc \
    source ~/.bashrc

## start hdfs
RUN \
    hdf namenode -format \
    start-dfs.sh \
    start-yarn.sh

# expose various ports
EXPOSE 8000 9000 8088 50070 50075 50030 50060