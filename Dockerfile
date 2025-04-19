FROM ghcr.io/kicad/kicad:9.0

# Install all the tools, dependencies are already installed
ADD dl_deb.py /usr/bin/
RUN sudo apt-get update  && \
	sudo apt install -y bsdmainutils wget && \
	sudo apt install -y python3-requests python3-socks python3-pyparsing && \
	sudo python3 /usr/bin/dl_deb.py INTI-CMNB/InteractiveHtmlBom && \
	sudo dpkg --ignore-depends kicad -i interactivehtmlbom*.deb && \
	sudo rm /*.deb  && \
	sudo rm -rf /var/lib/apt/lists/* /var/cache/debconf/templates.dat-old /var/lib/dpkg/status-old

ADD scripts /scripts
ADD tools /tools
ENV PATH="$PATH:/scripts:/tools"

USER root
