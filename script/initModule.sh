#!/bin/bash

# This is a initialize script for modules

MOD_DIR=/PiCAM/modules
MOD_MINIUPNPC=$MOD_DIR/miniupnp

mod_dir_chown() {
	WHOAMI=`whoami`
	sudo mkdir $MOD_DIR
	sudo chown $WHOAMI:$WHOAMI $MOD_DIR
}

mod_miniupnpc() {
	git clone https://github.com/miniupnp/miniupnp.git $MOD_MINIUPNPC
	pushd $MOD_MINIUPNPC/miniupnpc
	make
	make pythonmodule
	sudo python setup.py install
	popd
}


# Main
mod_dir_chown
mod_miniupnpc
