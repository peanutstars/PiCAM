#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>

#include <linux/videodev2.h>
#include <linux/uvcvideo.h>

#include <uvch264.h>
#include "pidebug.h"

static int xioctl (int fd, int request, void *arg)
{
	int rv; 

	do  
	{   
		rv = ioctl (fd, request, arg);
	}   
	while ( rv==(-1) && errno==EINTR);

	return rv; 
}

static int query_ioctl (int fd, int cur_ctrl, struct v4l2_queryctrl *ctrl)
{
	int rv = 0;
	int tries = 4;

	do  
	{   
		if (rv) {
			ctrl->id = cur_ctrl | V4L2_CTRL_FLAG_NEXT_CTRL;
		}

		rv = ioctl (fd, VIDIOC_QUERYCTRL, ctrl);
	}
	while (rv && tries-- &&
			((errno == EIO || errno == EPIPE || errno == ETIMEDOUT)));

	return rv;
}

