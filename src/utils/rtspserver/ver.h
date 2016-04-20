#ifndef __VERSION_H__
#define __VERSION_H__

#define TOSTR2(x)			#x
#define TOSTR(x)			TOSTR2(x)

#define VER_MAJOR			0
#define VER_MINOR			1
#define VER_SUBLEVEL		0
#define VER_STRING			"v" TOSTR(VER_MAJOR) "." TOSTR(VER_MINOR) "." TOSTR(VER_SUBLEVEL)

#endif /* __VERSION_H__ */
