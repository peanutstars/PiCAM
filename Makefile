#

SRCDIR		:= src

all:
	$(MAKE) -C $(SRCDIR)

clean:
	$(MAKE) -C $(SRCDIR) clean

install:
	$(MAKE) -C $(SRCDIR) install
