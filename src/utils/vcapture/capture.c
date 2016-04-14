/*
 *  V4L2 video capture example
 *
 *  This program can be used and distributed without restrictions.
 *
 *      This program is provided with the V4L2 API
 * see http://linuxtv.org/docs.php for more information
 * ---------------------------------------------------------------
 * Get Original Code from http://linuxtv.org/downloads/v4l-dvb-apis/capture-example.html
 * This Code from https://gist.githubusercontent.com/maxlapshin/1253534/raw/e676d3ccae0c5482e277994872ed03b36dfd8cc7/capture_raw_frames.c%2520%2520
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <getopt.h>             /* getopt_long() */

#include <fcntl.h>              /* low-level i/o */
#include <unistd.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <signal.h>
#include <stdlib.h>

#include <linux/videodev2.h>

#include "v4l2-h264.h"
#include "pidebug.h"
#include "pithread.h"
#include "ver.h"

#define CLEAR(x) memset(&(x), 0, sizeof(x))

#ifndef V4L2_PIX_FMT_H264
#define V4L2_PIX_FMT_H264     v4l2_fourcc('H', '2', '6', '4') /* H264 with start codes */
#endif

enum io_method {
	IO_METHOD_READ = 0,
	IO_METHOD_MMAP,
	IO_METHOD_USERPTR,
};

struct buffer {
	void   *start;
	size_t  length;
};

struct CaptureHandler {
	int			run ;
	int			done ;
	int			fgStdOut	: 1 ,
				fgFrame		: 1 ,
				fgVerbose	: 1 ; 
	char*		streamPath ;
	int			sfd ;
	V4l2Param	option ;
} ;
typedef struct CaptureHandler CaptureHandler ;

static CaptureHandler gCapHdr =
{
	.run		= 1 ,
	.done		= 0 ,
	.fgStdOut	= 0 ,
	.fgFrame	= 0 ,
	.fgVerbose	= 0 ,
	.streamPath = NULL ,
	.sfd		= -1 ,
	.option		= {
		.vfd			= -1 ,
		.width			= 1280 ,
		.height			= 720 ,
		.sliceUnits		= 1 ,
		.fps			= 7 ,
		.rateControl	= RATECONTROL_CBR ,
		.iFramePeriod	= 1000 ,
		.peakBitrate	= 3000000 ,
		.averageBitrate = 3000000 ,
		.entropy		= ENTROPY_CAVLC ,
		.timestamp		= 0 ,
	} ,
} ;

static char            *dev_name;
static enum io_method   io = IO_METHOD_MMAP;
static int              fd = -1;
struct buffer          *buffers;
static unsigned int     n_buffers;
static int              frame_number = 0;
static v4l2_info_t     *v4l2Info = NULL ;

static void errno_exit(const char *s)
{
        fprintf(stderr, "%s error %d, %s\n", s, errno, strerror(errno));
        exit(EXIT_FAILURE);
}

static int xioctl(int fh, int request, void *arg)
{
        int r;

        do {
                r = ioctl(fh, request, arg);
        } while (-1 == r && EINTR == errno);

        return r;
}

static int safeWrite(int fd, const char *ptr, int size)
{
	int left = size ;
	int wcnt ;
	do
	{
		wcnt = write(fd, ptr, left) ;
		if (wcnt != left) {
			if (wcnt < 0) {
				if (errno == ENOSPC || errno == EIO) {
					ERR2("Failed to write stream into file.\n") ;
					kill (getpid(), SIGINT) ;
				}
				else if (errno == EINTR) {
					continue ;
				}
				else {
					ERR2("Occured a Unhandled Error.\n") ;
					kill (getpid(), SIGINT) ;
				}
			}
		}
		left -= wcnt ;
		ptr += wcnt ;
	} while(left > 0) ;

	return 0 ;
}

static void process_image(CaptureHandler* capHdr, const void *p, int size)
{
	/* Insert NAL AUD(Access Unit Delimiter).
	   AUD must be exist to play on a mobile devcie. */

	const char h264AUD[] = { 0x00, 0x00, 0x00, 0x01, 0x09, 0xf0 } ;

    frame_number++;
	if (capHdr->fgVerbose) {
		fprintf(stderr, "%06d - %12d bytes\n", frame_number, size) ;
	}

	if (capHdr->fgStdOut) {
		fwrite(h264AUD, sizeof(h264AUD), 1, stdout) ;
		fwrite(p, size, 1, stdout) ;
	}
	if (capHdr->sfd >= 0) {
		safeWrite(capHdr->sfd, h264AUD, sizeof(h264AUD)) ;
		safeWrite(capHdr->sfd, (const char*)p, size) ;
	}
	if (capHdr->fgFrame) {
        FILE *fp ;
        char filename[32] ;
        sprintf(filename, "frame-%06d.h264", frame_number) ;
		fp = fopen(filename, "wb") ;
		if (fp) {
			fwrite(h264AUD, sizeof(h264AUD), 1, fp) ;
			fwrite(p, size, 1, fp);
			fclose(fp);
		}
	}
}

static int read_frame(CaptureHandler* capHdr)
{
        struct v4l2_buffer buf;
        unsigned int i;

        switch (io) {
        case IO_METHOD_READ:
                if (-1 == read(fd, buffers[0].start, buffers[0].length)) {
                        switch (errno) {
                        case EAGAIN:
                                return 0;

                        case EIO:
                                /* Could ignore EIO, see spec. */

                                /* fall through */

                        default:
                                errno_exit("read");
                        }
                }

                process_image(capHdr, buffers[0].start, buffers[0].length);
                break;

        case IO_METHOD_MMAP:
                CLEAR(buf);

                buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                buf.memory = V4L2_MEMORY_MMAP;

                if (-1 == xioctl(fd, VIDIOC_DQBUF, &buf)) {
                        switch (errno) {
                        case EAGAIN:
                                return 0;

                        case EIO:
                                /* Could ignore EIO, see spec. */

                                /* fall through */

                        default:
                                errno_exit("VIDIOC_DQBUF");
                        }
                }

                assert(buf.index < n_buffers);

                process_image(capHdr, buffers[buf.index].start, buf.bytesused);

                if (-1 == xioctl(fd, VIDIOC_QBUF, &buf))
                        errno_exit("VIDIOC_QBUF");
                break;

        case IO_METHOD_USERPTR:
                CLEAR(buf);

                buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                buf.memory = V4L2_MEMORY_USERPTR;

                if (-1 == xioctl(fd, VIDIOC_DQBUF, &buf)) {
                        switch (errno) {
                        case EAGAIN:
                                return 0;

                        case EIO:
                                /* Could ignore EIO, see spec. */

                                /* fall through */

                        default:
                                errno_exit("VIDIOC_DQBUF");
                        }
                }

                for (i = 0; i < n_buffers; ++i)
                        if (buf.m.userptr == (unsigned long)buffers[i].start
                            && buf.length == buffers[i].length)
                                break;

                assert(i < n_buffers);

                process_image(capHdr, (void *)buf.m.userptr, buf.bytesused);

                if (-1 == xioctl(fd, VIDIOC_QBUF, &buf))
                        errno_exit("VIDIOC_QBUF");
                break;
        }

        return 1;
}

static void* captureLoop(void* arg)
{
	CaptureHandler* capHdr = (CaptureHandler *)arg ;

	while (capHdr->run)
	{
		for (;;) {
			fd_set fds;
			struct timeval tv;
			int r;

			FD_ZERO(&fds);
			FD_SET(fd, &fds);

			/* Timeout. */
			tv.tv_sec = 2;
			tv.tv_usec = 0;

			r = select(fd + 1, &fds, NULL, NULL, &tv);

			if (-1 == r) {
				if (EINTR == errno)
					continue;
				ERR2("select\n") ;
				capHdr->run = 0 ;
			}

			if (0 == r) {
				fprintf(stderr, "select timeout\n");
				capHdr->run = 0 ;
				break ;
			}

			if (read_frame(capHdr))
				break;
			/* EAGAIN - continue select loop. */
		}
	}
	capHdr->done = 1 ;
	return NULL ;
}

static void stop_capturing(void)
{
        enum v4l2_buf_type type;

        switch (io) {
        case IO_METHOD_READ:
                /* Nothing to do. */
                break;

        case IO_METHOD_MMAP:
        case IO_METHOD_USERPTR:
                type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                if (-1 == xioctl(fd, VIDIOC_STREAMOFF, &type))
                        errno_exit("VIDIOC_STREAMOFF");
                break;
        }
}

static void start_capturing(void)
{
        unsigned int i;
        enum v4l2_buf_type type;

        switch (io) {
        case IO_METHOD_READ:
                /* Nothing to do. */
                break;

        case IO_METHOD_MMAP:
                for (i = 0; i < n_buffers; ++i) {
                        struct v4l2_buffer buf;

                        CLEAR(buf);
                        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                        buf.memory = V4L2_MEMORY_MMAP;
                        buf.index = i;

                        if (-1 == xioctl(fd, VIDIOC_QBUF, &buf))
                                errno_exit("VIDIOC_QBUF");
                }
                type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                if (-1 == xioctl(fd, VIDIOC_STREAMON, &type))
                        errno_exit("VIDIOC_STREAMON");
                break;

        case IO_METHOD_USERPTR:
                for (i = 0; i < n_buffers; ++i) {
                        struct v4l2_buffer buf;

                        CLEAR(buf);
                        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                        buf.memory = V4L2_MEMORY_USERPTR;
                        buf.index = i;
                        buf.m.userptr = (unsigned long)buffers[i].start;
                        buf.length = buffers[i].length;

                        if (-1 == xioctl(fd, VIDIOC_QBUF, &buf))
                                errno_exit("VIDIOC_QBUF");
                }
                type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                if (-1 == xioctl(fd, VIDIOC_STREAMON, &type))
                        errno_exit("VIDIOC_STREAMON");
                break;
        }
}

static void uninit_device(void)
{
        unsigned int i;

        switch (io) {
        case IO_METHOD_READ:
                free(buffers[0].start);
                break;

        case IO_METHOD_MMAP:
                for (i = 0; i < n_buffers; ++i)
                        if (-1 == munmap(buffers[i].start, buffers[i].length))
                                errno_exit("munmap");
                break;

        case IO_METHOD_USERPTR:
                for (i = 0; i < n_buffers; ++i)
                        free(buffers[i].start);
                break;
        }

        free(buffers);

//		v4l2_destroy(v4l2Info) ;
}

static void init_read(unsigned int buffer_size)
{
        buffers = calloc(1, sizeof(*buffers));

        if (!buffers) {
                fprintf(stderr, "Out of memory\n");
                exit(EXIT_FAILURE);
        }

        buffers[0].length = buffer_size;
        buffers[0].start = malloc(buffer_size);

        if (!buffers[0].start) {
                fprintf(stderr, "Out of memory\n");
                exit(EXIT_FAILURE);
        }
}

static void init_mmap(void)
{
        struct v4l2_requestbuffers req;

        CLEAR(req);

        req.count = 16;
        req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory = V4L2_MEMORY_MMAP;

        if (-1 == xioctl(fd, VIDIOC_REQBUFS, &req)) {
                if (EINVAL == errno) {
                        fprintf(stderr, "%s does not support "
                                 "memory mapping\n", dev_name);
                        exit(EXIT_FAILURE);
                } else {
                        errno_exit("VIDIOC_REQBUFS");
                }
        }

        if (req.count < 2) {
                fprintf(stderr, "Insufficient buffer memory on %s\n",
                         dev_name);
                exit(EXIT_FAILURE);
        }

        buffers = calloc(req.count, sizeof(*buffers));

        if (!buffers) {
                fprintf(stderr, "Out of memory\n");
                exit(EXIT_FAILURE);
        }

        for (n_buffers = 0; n_buffers < req.count; ++n_buffers) {
                struct v4l2_buffer buf;

                CLEAR(buf);

                buf.type        = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                buf.memory      = V4L2_MEMORY_MMAP;
                buf.index       = n_buffers;

                if (-1 == xioctl(fd, VIDIOC_QUERYBUF, &buf))
                        errno_exit("VIDIOC_QUERYBUF");

                buffers[n_buffers].length = buf.length;
                buffers[n_buffers].start =
                        mmap(NULL /* start anywhere */,
                              buf.length,
                              PROT_READ | PROT_WRITE /* required */,
                              MAP_SHARED /* recommended */,
                              fd, buf.m.offset);

                if (MAP_FAILED == buffers[n_buffers].start)
                        errno_exit("mmap");
        }
}

static void init_userp(unsigned int buffer_size)
{
        struct v4l2_requestbuffers req;

        CLEAR(req);

        req.count  = 4;
        req.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory = V4L2_MEMORY_USERPTR;

        if (-1 == xioctl(fd, VIDIOC_REQBUFS, &req)) {
                if (EINVAL == errno) {
                        fprintf(stderr, "%s does not support "
                                 "user pointer i/o\n", dev_name);
                        exit(EXIT_FAILURE);
                } else {
                        errno_exit("VIDIOC_REQBUFS");
                }
        }

        buffers = calloc(4, sizeof(*buffers));

        if (!buffers) {
                fprintf(stderr, "Out of memory\n");
                exit(EXIT_FAILURE);
        }

        for (n_buffers = 0; n_buffers < 4; ++n_buffers) {
                buffers[n_buffers].length = buffer_size;
                buffers[n_buffers].start = malloc(buffer_size);

                if (!buffers[n_buffers].start) {
                        fprintf(stderr, "Out of memory\n");
                        exit(EXIT_FAILURE);
                }
        }
}

static void init_device(V4l2Param* option)
{
        struct v4l2_capability cap;
        struct v4l2_cropcap cropcap;
        struct v4l2_crop crop;
        struct v4l2_format fmt;
		struct v4l2_streamparm parm ;
        unsigned int min;

		option->vfd = fd ;

        if (-1 == xioctl(fd, VIDIOC_QUERYCAP, &cap)) {
                if (EINVAL == errno) {
                        fprintf(stderr, "%s is no V4L2 device\n",
                                 dev_name);
                        exit(EXIT_FAILURE);
                } else {
                        errno_exit("VIDIOC_QUERYCAP");
                }
        }

        if (!(cap.capabilities & V4L2_CAP_VIDEO_CAPTURE)) {
                fprintf(stderr, "%s is no video capture device\n",
                         dev_name);
                exit(EXIT_FAILURE);
        }

        switch (io) {
        case IO_METHOD_READ:
                if (!(cap.capabilities & V4L2_CAP_READWRITE)) {
                        fprintf(stderr, "%s does not support read i/o\n",
                                 dev_name);
                        exit(EXIT_FAILURE);
                }
                break;

        case IO_METHOD_MMAP:
        case IO_METHOD_USERPTR:
                if (!(cap.capabilities & V4L2_CAP_STREAMING)) {
                        fprintf(stderr, "%s does not support streaming i/o\n",
                                 dev_name);
                        exit(EXIT_FAILURE);
                }
                break;
        }


        /* Select video input, video standard and tune here. */


        CLEAR(cropcap);

        cropcap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

        if (0 == xioctl(fd, VIDIOC_CROPCAP, &cropcap)) {
                crop.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                crop.c = cropcap.defrect; /* reset to default */

                if (-1 == xioctl(fd, VIDIOC_S_CROP, &crop)) {
                        switch (errno) {
                        case EINVAL:
                                /* Cropping not supported. */
                                break;
                        default:
                                /* Errors ignored. */
                                break;
                        }
                }
        } else {
                /* Errors ignored. */
        }


        CLEAR(fmt);

        fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

		/* H264 */
		fmt.fmt.pix.width       = option->width ;
		fmt.fmt.pix.height      = option->height ;
		fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_H264; //replace
		fmt.fmt.pix.field       = V4L2_FIELD_ANY;

		if (-1 == xioctl(fd, VIDIOC_S_FMT, &fmt)) {
			errno_exit("VIDIOC_S_FMT");
		}

        /* Buggy driver paranoia. */
        min = fmt.fmt.pix.width * 2;
        if (fmt.fmt.pix.bytesperline < min)
                fmt.fmt.pix.bytesperline = min;
        min = fmt.fmt.pix.bytesperline * fmt.fmt.pix.height;
        if (fmt.fmt.pix.sizeimage < min)
                fmt.fmt.pix.sizeimage = min;

        switch (io) {
        case IO_METHOD_READ:
                init_read(fmt.fmt.pix.sizeimage);
                break;

        case IO_METHOD_MMAP:
                init_mmap();
                break;

        case IO_METHOD_USERPTR:
                init_userp(fmt.fmt.pix.sizeimage);
                break;
        }


		/* Set FPS */
		CLEAR(parm) ;

		parm.type = V4L2_BUF_TYPE_VIDEO_CAPTURE ;
		parm.parm.capture.timeperframe.numerator = 1000 ;
		parm.parm.capture.timeperframe.denominator =
			option->fps * parm.parm.capture.timeperframe.numerator ;
		if (-1 == xioctl(fd, VIDIOC_S_PARM, &parm)) {
			errno_exit("VIDIOC_S_FMT");
		} else {
			struct v4l2_fract *tf = &parm.parm.capture.timeperframe;
			if ( ! tf->denominator || ! tf->numerator)
				fprintf(stderr, "Invalid frame rate\n") ;
			else
				fprintf(stderr, "Frame rate set to %.3f fps\n", 1.0 * tf->denominator / tf->numerator) ;
		}


		v4l2Info = v4l2_create(option) ;
}

static void close_device(void)
{
        if (-1 == close(fd))
                errno_exit("close");

        fd = -1;
}

static void open_device(void)
{
        struct stat st;

        if (-1 == stat(dev_name, &st)) {
                fprintf(stderr, "Cannot identify '%s': %d, %s\n",
                         dev_name, errno, strerror(errno));
                exit(EXIT_FAILURE);
        }

        if (!S_ISCHR(st.st_mode)) {
                fprintf(stderr, "%s is no device\n", dev_name);
                exit(EXIT_FAILURE);
        }

        fd = open(dev_name, O_RDWR /* required */ | O_NONBLOCK, 0);

        if (-1 == fd) {
                fprintf(stderr, "Cannot open '%s': %d, %s\n",
                         dev_name, errno, strerror(errno));
                exit(EXIT_FAILURE);
        }
}

static void commonSigHandler(int signum)
{
	if (signum == SIGTERM || signum == SIGINT) {
		gCapHdr.run = 0 ;
	}
	else {
		ERR("Occured a unhandled signal, %d.\n", signum) ;
	}
}

static void initSignal (void)
{
	const int handledSignals[] = { SIGTERM, SIGINT } ;
	struct sigaction sa ;
	int i ;

	for (i=0; i<sizeof(handledSignals)/sizeof(int); i++)
	{
		memset (&sa, 0, sizeof(sa)) ;
		sa.sa_handler = commonSigHandler ;
		sigemptyset(&sa.sa_mask) ;
		sigaction(handledSignals[i], &sa, 0) ;
	}
}

static void mainLoop (CaptureHandler* capHdr)
{
	pthread_t thid ;

	initSignal() ;
	CREATE_THREAD(thid, captureLoop, 0x1000, capHdr, ETP_MODE_DETACHED) ;

	while ( ! capHdr->done) {
		usleep(500000) ;
	}
}

static void dumpV4l2Param (FILE* fp, V4l2Param* param)
{
	fprintf(fp,	"Picture Size       : %d x %d @ %d fps\n", param->width, param->height, param->fps) ;
	fprintf(fp, "Rate-control       : %s\n", param->rateControl == RATECONTROL_CBR ? "CBR" : "VBR") ;
	fprintf(fp, "I Frame Period     : %d msec\n", param->iFramePeriod) ;
	fprintf(fp, "Peak Bitrate       : %d bps\n", param->peakBitrate) ;
	fprintf(fp, "Average Bitrate    : %d bps\n", param->averageBitrate) ;
	fprintf(fp, "Entropy Method     : %s\n", param->entropy == ENTROPY_CAVLC ? "CAVLC" : "CABAC") ;
	fprintf(fp, "Picture timing SEI : %s\n", param->timestamp ? "Enabled" : "Disabled") ;
}

static void usage(FILE *fp, int argc, char **argv)
{
	fprintf(fp,
		"Usage: %s [options]\n\n"
		"It is utility for capturing H264 streams from UVC interface and other formats are not supported.\n\n"
		"Version " VER_STRING "\n"
		"Options:\n"
		"-v | --verbose               Display messages."
		"-d | --dev name              Video device name [%s]\n"
		"-h | --help                  Print this message\n"
		"-m | --mmap                  Use memory mapped buffers [default]\n"
		"-r | --read                  Use read() calls\n"
		"-u | --userp                 Use application allocated buffers\n"
		"-o | --output                Output stream to stdout\n"
		"-s | --stream <file>         Output stream to file\n"
		"-f | --frame                 Output stream to store each the frames\n"
		"--width <size>               Set a width of picture, default is 1280\n"
		"                                1920, 1280, 1024, 864, 800, 640\n"
		"--height <size>              Set a height of picture, default is 720\n"
		"                                1080,  720,  576, 480, 448, 360\n" 
		"--slice-units <num>          Set a value of slice units, default is 1\n"
		"                                Range is from 1 to 8.\n"
		"--frame-rate <fps>           Set a frame-rate, default is 15 fps\n"
		"                                30, 24, 20, 15, 10, 7(like as 7.5)\n"
//		"--rate-control <cbr|vbr>     Set a rate-control, default is cbr mode.\n"
		"--iframe-period <sec>        Set a iframe-peroid value, default is 3 sec.\n"
		"                                Range is from 1 to 10 second.\n"
//		"--peak-bitrate <bitrate>     Set a peak-bitrate value, default is 3000000.\n"
		"--average-bitrate <bitrate>  Set a average-bitrate value, default is 3000000.\n"
		"                                Range is from 1000000 to 5000000 bps.\n"
//		"--entropy <CAVLC|CABAC>      Set a entropy, default is CAVLC.\n"
//		"--timestamp <enable|disable> Set picture timing SEI enable or disable.\n"
		, argv[0], dev_name);
}

static const char short_options[] = "vd:hmruos:f";

static const struct option
long_options[] = {
		{ "width" ,				required_argument, NULL, 0 } ,
		{ "height" ,			required_argument, NULL, 0 } ,
		{ "slice-units" ,		required_argument, NULL, 0 } ,
		{ "frame-rate" ,		required_argument, NULL, 0 } ,
		{ "rate-control" ,		required_argument, NULL, 0 } ,
		{ "iframe-period" ,		required_argument, NULL, 0 } ,
		{ "peak-bitrate" ,		required_argument, NULL, 0 } ,
		{ "average-bitrate" ,	required_argument, NULL, 0 } ,
		{ "entropy" ,			required_argument, NULL, 0 } ,
		{ "timestamp" ,			required_argument, NULL, 0 } ,
		{ "verbose" ,			no_argument,       NULL, 'v' } ,
        { "dev",				required_argument, NULL, 'd' },
        { "help",   			no_argument,       NULL, 'h' },
        { "mmap",   			no_argument,       NULL, 'm' },
        { "read",   			no_argument,       NULL, 'r' },
        { "userp",  			no_argument,       NULL, 'u' },
        { "output", 			no_argument,       NULL, 'o' },
		{ "stream",				required_argument, NULL, 's' } ,
		{ "frame",				no_argument,       NULL, 'f' } ,
        { 0, 0, 0, 0 }
};

static void parseOptions (CaptureHandler* capHdr, int argc, char* argv[])
{
	const int allowWidth[] =  { 1920, 1280, 1024, 864, 800, 640 } ;
	const int allowHeight[] = { 1080,  720,  576, 480, 448, 360 } ;
	int i ;

	for (;;)
	{
		int idx;
		int c;
		int fgFound ;

		c = getopt_long(argc, argv,
				short_options, long_options, &idx);

		if (-1 == c)
			break;

		switch (c) {
			case 0: /* getopt_long() flag */
				fgFound = 0 ;
				if ( ! strcmp(long_options[idx].name, "width")) {
					capHdr->option.width = strtoul(optarg, NULL, 0) ;
					for (i=0; i<sizeof(allowWidth)/sizeof(int); i++) {
						if (allowWidth[i] == capHdr->option.width) {
							fgFound = 1 ;
							break ;
						}
					}
				}
				if ( ! strcmp(long_options[idx].name, "height")) {
					capHdr->option.height = strtoul(optarg, NULL, 0) ;
					for (i=0; i<sizeof(allowHeight)/sizeof(int); i++) {
						if (allowHeight[i] == capHdr->option.height) {
							fgFound = 1 ;
							break ;
						}
					}
				}
				if ( ! strcmp(long_options[idx].name, "slice-units")) {
					int unit = strtoul(optarg, NULL, 0) ;
					if (1 <= unit && unit <= 8) {
						capHdr->option.sliceUnits = unit ;
						fgFound = 1 ;
					}
				}
				if ( ! strcmp(long_options[idx].name, "frame-rate")) {
					const int allowFps[] = { 30, 24, 20, 15, 10, 7 } ;
					capHdr->option.fps = strtoul(optarg, NULL, 0) ;
					for (i=0; i<sizeof(allowFps)/sizeof(int); i++) {
						if (allowFps[i] == capHdr->option.fps) {
							fgFound = 1 ;
							break ;
						}
					}
				}
				if ( ! strcmp(long_options[idx].name, "iframe-period")) {
					int period = strtoul(optarg, NULL, 0) ;
					if (1 <= period && period <= 10) {
						capHdr->option.iFramePeriod = period * 1000;
						fgFound = 1 ;
					}
				}
				if ( ! strcmp(long_options[idx].name, "average-bitrate")) {
					int bitrate = strtoul(optarg, NULL, 0) ;
					if (1000000 <= bitrate && bitrate <= 5000000) {
						capHdr->option.averageBitrate = bitrate ;
						fgFound = 1 ;
					}
				}
				if ( ! fgFound) {
					fprintf(stderr, "Invalid option %s %s\n\n", long_options[idx].name, optarg ? : "") ;
					usage(stderr, argc, argv);
					exit(EXIT_FAILURE);
				}
				break;

			case 'v':
				capHdr->fgVerbose = 1 ;
				break ;

			case 'd':
				dev_name = optarg;
				break;

			case 'h':
				usage(stdout, argc, argv);
				exit(EXIT_SUCCESS);

			case 'm':
				io = IO_METHOD_MMAP;
				break;

			case 'r':
				io = IO_METHOD_READ;
				break;

			case 'u':
				io = IO_METHOD_USERPTR;
				break;

			case 'o':
				capHdr->fgStdOut = 1 ;
				break;
			
			case 's' :
				capHdr->streamPath = optarg ;
				capHdr->sfd = open(optarg, O_WRONLY|O_CREAT|O_TRUNC, 0666) ;
				if (capHdr->sfd < 0) {
					ERR2("Failed to open %s.\n", optarg) ;
					exit(EXIT_FAILURE) ;
				}
				break ;

			case 'f' :
				capHdr->fgFrame = 1 ;
				break ;

			default:
				usage(stderr, argc, argv);
				exit(EXIT_FAILURE);
		}
	}
	
	for(i=0; i<sizeof(allowWidth)/sizeof(int); i++) {
		if (allowWidth[i] == capHdr->option.width) {
			if (allowHeight[i] == capHdr->option.height) {
				break ;
			}
			else {
				fprintf(stderr, "The resolution is wrong, I recommended the following : %dx%d\n\n",
					allowWidth[i] , allowHeight[i]) ;
				usage(stderr, argc, argv);
				exit(EXIT_FAILURE);
			}
		}
	}
	
	dumpV4l2Param(stderr, &capHdr->option) ;
}

static void clearOut (CaptureHandler* capHdr)
{
	if (capHdr->sfd >= 0) {
		close(capHdr->sfd) ;
	}
}

int main(int argc, char **argv)
{
	CaptureHandler* capHdr = &gCapHdr ;
	dev_name = "/dev/video0";

	parseOptions(capHdr, argc, argv) ;

	open_device();
	init_device(&capHdr->option) ;
	start_capturing();
	mainLoop(capHdr) ;
	stop_capturing();
	uninit_device();
	close_device();

	clearOut(capHdr) ;

	fprintf(stderr, "\n");
	return 0;
}
