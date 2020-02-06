FROM ubuntu:18.04

RUN sed -i 's/archive.ubuntu.com/tw.&/' /etc/apt/sources.list
RUN apt update && apt install --no-install-recommends -y openssh-server
RUN mkdir /var/run/sshd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
COPY run.sh /run.sh
RUN chmod +x /run.sh
# https://stackoverflow.com/a/53897608
EXPOSE 22/TCP
ENTRYPOINT ["/run.sh"] 
