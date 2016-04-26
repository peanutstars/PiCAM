#!/bin/bash

# This is a deinitialize script for modules

MOD_DIR=/PiCAM/modules
MOD_MINIUPNPC=$MOD_DIR/miniupnp

mod_miniupnpc() {
	pushd $MOD_MINIUPNPC/miniupnpc
	sudo python setup.py install --record list.txt
	sudo cat list.txt | xargs rm -rf
	popd
}


# Main
mod_miniupnpc
