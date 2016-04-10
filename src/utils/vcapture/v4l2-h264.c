/*
	It could be supported kernel 3.0 or later.
 */


#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <pthread.h>
#include <string.h>

#include <linux/videodev2.h>
#include <linux/uvcvideo.h>

#include "pidebug.h"
#include "pidefine.h"
#include "v4l2-h264.h"

static __u16 ux_size[UVCX_LAST] = {
	0,
	sizeof( uvcx_video_config_probe_commit_t	),	/* UVCX_VIDEO_CONFIG_PROBE		*/
	sizeof( uvcx_video_config_probe_commit_t	),  /* UVCX_VIDEO_CONFIG_COMMIT		*/
	sizeof( uvcx_rate_control_mode_t			),  /* UVCX_RATE_CONTROL_MODE		*/
	sizeof( uvcx_temporal_scale_mode_t			),  /* UVCX_TEMPORAL_SCALE_MODE		*/
	sizeof( uvcx_spatial_scale_mode_t			),  /* UVCX_SPATIAL_SCALE_MODE		*/
	sizeof( uvcx_snr_scale_mode_t				),  /* UVCX_SNR_SCALE_MODE			*/
	sizeof( uvcx_ltr_buffer_size_control_t		),  /* UVCX_LTR_BUFFER_SIZE_CONTROL	*/
	sizeof( uvcx_ltr_picture_control_t			),  /* UVCX_LTR_PICTURE_CONTROL		*/
	sizeof( uvcx_picture_type_control_t			),  /* UVCX_PICTURE_TYPE_CONTROL	*/
	sizeof( uvcx_version_t						),  /* UVCX_VERSION					*/
	sizeof( uvcx_encoder_reset_t				),  /* UVCX_ENCODER_RESET			*/
	sizeof( uvcx_framerate_config_t				),  /* UVCX_FRAMERATE_CONFIG		*/
	sizeof( uvcx_video_advance_config_t			),  /* UVCX_VIDEO_ADVANCE_CONFIG	*/
	sizeof( uvcx_bitrate_layers_t				),  /* UVCX_BITRATE_LAYERS			*/
	sizeof( uvcx_qp_steps_layers_t				)   /* UVCX_QP_STEPS_LAYERS			*/
};

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

static int get_ctrl_list (v4l2_info_t *info)
{
	struct v4l2_queryctrl queryctrl = { 0, };
	struct v4l2_querymenu querymenu = { 0, };
	int curctrl = 0, nextcount=0;
	int rv, count = 0;
	int fd = info->vfd;

	queryctrl.id	= 0 | V4L2_CTRL_FLAG_NEXT_CTRL;
	curctrl			= 0 | V4L2_CTRL_FLAG_NEXT_CTRL;

	while ((rv=query_ioctl(fd, curctrl, &queryctrl)), rv ? errno!=EINVAL : 1)
	{
		if (rv && queryctrl.id <= curctrl)
		{
			DBG ("buggy V4L2_CTRL_FLAG_NEXT_CTRL flag implementation (workaround enabled)\n");
			curctrl ++;
			queryctrl.id = curctrl;

			if (nextcount++ > 256)
				break;

			goto next_control;
		}
		else if ((queryctrl.id == V4L2_CTRL_FLAG_NEXT_CTRL) || (!rv && queryctrl.id == curctrl))
		{
			DBG ("buggy V4L2_CTRL_FLAG_NEXT_CTRL flag implementation (failed enumeration for id=0x%08x)\n", queryctrl.id);
			break;
		}

		if (info->ctlList)
		{
			DBG ("id=%08X %d %-32s %d-%d,%d:%d %X\n",
				queryctrl.id, queryctrl.type, queryctrl.name, queryctrl.minimum, queryctrl.maximum,
				queryctrl.step, queryctrl.default_value, queryctrl.flags);
		
			memcpy (&info->ctlList[count].ctrl, &queryctrl, sizeof(queryctrl));
		}

		if (queryctrl.type == V4L2_CTRL_TYPE_MENU)
		{
			if (info->ctlList)
			{
				info->ctlList[count].menu = malloc (sizeof(querymenu) * queryctrl.maximum);
				if ( ! info->ctlList[count].menu )
				{
					ERR("malloc ( v4l2->ctlList[%d].menu )\n", count);
//					ASSERT(0) ;
				}
				memset (info->ctlList[count].menu, 0, sizeof(querymenu) * queryctrl.maximum);
			}

			for (querymenu.index = queryctrl.minimum;
					querymenu.index <= queryctrl.maximum;
					querymenu.index ++)
			{
				querymenu.id = queryctrl.id;
				rv = xioctl(fd, VIDIOC_QUERYMENU, &querymenu);
				if (rv < 0)
				{
					ERR("xioctl ( VIDIOC_QUERYMENU[id=%08X,index=%d] )\n", queryctrl.id, querymenu.index);
					continue;
				}

				if (info->ctlList)
				{
					struct v4l2_querymenu *menu = &info->ctlList[count].menu[querymenu.index];
					memcpy (menu, &querymenu, sizeof(querymenu));

					DBG("MENU id=%08X %d %s\n", querymenu.id, querymenu.index, querymenu.name);
				}
			}
		}

		curctrl = queryctrl.id;
		count ++;

next_control:
		queryctrl.id |= V4L2_CTRL_FLAG_NEXT_CTRL;
	}

	DBG("### ctlcount = %d\n", count) ;
	return count;
}

static EV4l2Ret get_ctrl_all (v4l2_info_t *info)
{
	int rv, i, fd = info->vfd;
	v4l2_ctrl_list_t *list = info->ctlList;
	__u32 v4l2Class;

	for (i=0; i<info->ctlCnt; i++, list++)
	{
		v4l2Class = V4L2_CTRL_ID2CLASS (list->ctrl.id);
		
		if ( v4l2Class == V4L2_CTRL_CLASS_USER )
		{
			struct v4l2_control ctrl = { 0, 0 };

			ctrl.id		= list->ctrl.id;
			rv = xioctl (fd, VIDIOC_G_CTRL, &ctrl);
			if (rv) {
				ERR ("control id: 0x%X failed to get value (error %i)\n", ctrl.id, rv);
			}
			else {
				list->value = ctrl.value;
				DBG ("Get User 0x%X -> 0x%X(%u)\n", ctrl.id, ctrl.value, ctrl.value);
			}
		}
		else
		{
			struct v4l2_ext_controls ctrls = { 0, };
			struct v4l2_ext_control ctrl = { 0, };

			ctrl.id			= list->ctrl.id;
			ctrls.count		= 1;
			ctrls.controls	= &ctrl;

			rv = xioctl (fd, VIDIOC_G_EXT_CTRLS, &ctrls);
			if (rv) {
				ERR("control id: 0x%X failed to get value (error %i)\n", ctrl.id, rv);
			}
			else
			{
				if ( list->ctrl.type == V4L2_CTRL_TYPE_INTEGER64 ) {
					list->value64 = ctrl.value64;
					DBG ("Get Ext64 0x%X -> 0x%llX(%lld)\n", ctrl.id, ctrl.value64, ctrl.value64);
				}
				else {
					list->value	= ctrl.value;
					DBG ("Get Ext32 0x%X -> 0x%X(%u)\n", ctrl.id, ctrl.value, ctrl.value);
				}
			}
		}
	}
	return EV4L2RV_OK ;
}

static EV4l2Ret set_ctrl (v4l2_info_t *info, v4l2_ctrl_list_t *list)
{
	int rv, fd = info->vfd;
	__u32 v4l2Class = V4L2_CTRL_ID2CLASS(list->ctrl.id);

	if ( v4l2Class == V4L2_CTRL_CLASS_USER )
	{
		struct v4l2_control ctrl;

		ctrl.id		= list->ctrl.id;
		ctrl.value	= list->value;

		rv = xioctl (fd, VIDIOC_S_CTRL, &ctrl);
		if (rv) {
			ERR ("control id: 0x%X failed to get value (error %i)\n", ctrl.id, rv);
			return EV4L2RV_ERR_IOCTL ;
		}
		else {
			DBG ("Set User 0x%X -> 0x%X(%u)\n", ctrl.id, ctrl.value, ctrl.value);
		}
	}
	else
	{
		struct v4l2_ext_controls ctrls = { 0, };
		struct v4l2_ext_control ctrl = { 0, };

		ctrl.id				= list->ctrl.id;
		ctrls.count			= 1;
		ctrls.controls		= &ctrl;
		if ( list->ctrl.type == V4L2_CTRL_TYPE_INTEGER64 ) {
			ctrl.value64	= list->value64;
			DBG ("Set Ext64 0x%X <- 0x%llX(%lld)\n", ctrl.id, ctrl.value64, ctrl.value64);
		}
		else {
			ctrl.value		= list->value;
			DBG ("Set Ext32 0x%X <- 0x%X(%u)\n", ctrl.id, ctrl.value, ctrl.value);
		}

		rv = xioctl (fd, VIDIOC_S_EXT_CTRLS, &ctrls);
		if (rv) {
			ERR ("control id: 0x%X failed to get value (error %i)\n", ctrl.id, rv);
			return EV4L2RV_ERR_IOCTL ;
		}
	}
	return EV4L2RV_OK ;
}

static EV4l2Ret set_ctrl_default (v4l2_info_t *info)
{
	v4l2_ctrl_list_t *list;
	int i;

	/* fill default value */
	for (i=0,list=info->ctlList; i<info->ctlCnt; i++, list++) {
		if ( list->ctrl.type == V4L2_CTRL_TYPE_INTEGER64 ) {
			list->value64 = (__s64)list->ctrl.default_value ;
		}
		else {
			list->value = list->ctrl.default_value;
		}
	}

	/* set default value */
	for (i=0,list=info->ctlList; i<info->ctlCnt; i++, list++) {
		info->op->set_ctrl (info, list);
	}

	return EV4L2RV_OK ;
}

static void xu_h264_init_buf (v4l2_info_t *info)
{
	int i;

	info->h264.unit		= 12; /* XXX : Currently hard coding, Logitech C920 used 12 for unit */
	info->h264.size		= ux_size;

	for (i=UVCX_VIDEO_CONFIG_COMMIT; i<UVCX_LAST; i++)
	{
		if ( info->h264.size[i] > 0 )
		{
			info->h264.selector[i] = malloc (info->h264.size[i]);
			if ( ! info->h264.selector[i] ) {
				ERR ("malloc ( XU[%d]-%d )\n", i, info->h264.size[i]) ;
//				ASSERT(0) ;
			}
			memset (info->h264.selector[i], 0, info->h264.size[i]);
		}
	}
	/* The buffer used in common. */ 
	info->h264.selector[UVCX_VIDEO_CONFIG_PROBE] = info->h264.selector[UVCX_VIDEO_CONFIG_COMMIT];
}

static void xu_h264_deinit_buf (v4l2_info_t *info)
{
	int i;
	
	for (i=UVCX_VIDEO_CONFIG_COMMIT; i<UVCX_LAST; i++) {
		free (info->h264.selector[i]);
	}
}

static EV4l2Ret xu_h264_init (v4l2_info_t *info)
{
	return EV4L2RV_OK ;
}

static void dump_xu_h264_value (int selector, void *data)
{
	switch (selector)
	{
		case UVCX_VIDEO_CONFIG_PROBE:
		case UVCX_VIDEO_CONFIG_COMMIT:
			{
				uvcx_video_config_probe_commit_t *conf = data;
				DBG ("  [[ UVCX_VIDEO_CONFIG_PROBE or UVCX_VIDEO_CONFIG_COMMIT ]]\n");
				DBG ("Frame Interval             : %d\n",		conf->dwFrameInterval);
				DBG ("Bitrate                    : %d\n",		conf->dwBitRate);
				DBG ("Hints                      : %X\n",		conf->bmHints);
				DBG ("Configuration Index        : %d\n",		conf->wConfigurationIndex);
				DBG ("Width x Height             : %d x %d\n",	conf->wWidth, conf->wHeight);
				DBG ("Slice Units, Modes         : %X, %X\n",	conf->wSliceUnits, conf->wSliceMode);
				DBG ("Profile                    : %X\n",		conf->wProfile);
				DBG ("IDR Frame Period           : %d msec\n",	conf->wIFramePeriod);
				DBG ("Estimated Video Delay      : %d msec\n",	conf->wEstimatedVideoDelay);
				DBG ("Estimated Max Config Delay : %d msec\n",	conf->wEstimatedMaxConfigDelay);
				DBG ("Usage Type                 : %X\n",		conf->bUsageType);
				DBG ("Rate Control Mode          : %X\n",		conf->bRateControlMode);
				DBG ("Temporal Scale Mode        : %X\n",		conf->bTemporalScaleMode);
				DBG ("Spatial Scale Mode         : %X\n",		conf->bSpatialScaleMode);
				DBG ("SNR Scale Mode             : %X\n",		conf->bSNRScaleMode);
				DBG ("Stream Mux Option          : %X\n",		conf->bStreamMuxOption);
				DBG ("Stream Format              : %X\n",		conf->bStreamFormat);
				DBG ("Entropy CABAC              : %X\n",		conf->bEntropyCABAC);
				DBG ("Timestamp                  : %X\n",		conf->bTimestamp);
				DBG ("Num of Recorder Freames    : %d\n",		conf->bNumOfReorderFrames);
				DBG ("Preview Flipped            : %X\n",		conf->bPreviewFlipped);
				DBG ("View                       : %d\n",		conf->bView);
				DBG ("Reserved 1,2               : %X %X\n",	conf->bReserved1, conf->bReserved2);
				DBG ("Stream ID                  : %X\n",		conf->bStreamID);
				DBG ("Spatial Layer Ratio        : %X\n",		conf->bSpatialLayerRatio);
				DBG ("Leaky Bucket Size          : %d msec\n",	conf->wLeakyBucketSize);
			}
			break;
		case UVCX_RATE_CONTROL_MODE:
			{
				uvcx_rate_control_mode_t *conf = data;
				DBG ("  [[ UVCX_RATE_CONTROL_MODE: ]]\n");
				DBG ("wLayerID                   : %X\n",		conf->wLayerID);
				DBG ("bRateControlMode           : %02X\n",		conf->bRateControlMode);
			}
			break;
		case UVCX_PICTURE_TYPE_CONTROL:
			{
				uvcx_picture_type_control_t *conf = data;
				DBG ("  [[ UVCX_PICTURE_TYPE_CONTROL ]]\n");
				DBG ("wLayerID                   : %X\n",		conf->wLayerID);
				DBG ("wPicType                   : %04X\n",		conf->wPicType);
			}
			break;
		case UVCX_VERSION:
			{
				uvcx_version_t *conf = data;
				DBG ("  [[ UVCX_VERSION ]]\n");
				DBG ("wVersion                   : %04X\n",		conf->wVersion);
			}
			break;
		case UVCX_ENCODER_RESET:
			{
				uvcx_encoder_reset_t *conf = data;
				DBG ("  [[ UVCX_ENCODER_RESET ]]\n");
				DBG ("wLayerID                   : %X\n",		conf->wLayerID);
			}
			break;
		case UVCX_FRAMERATE_CONFIG:
			{
				uvcx_framerate_config_t *conf = data;
				DBG ("  [[ UVCX_FRAMERATE_CONFIG ]]\n");
				DBG ("wLayerID                   : %X\n",		conf->wLayerID);
				DBG ("dwFrameInterval            : %d00 nsec\n",conf->dwFrameInterval);
			}
			break;
		case UVCX_VIDEO_ADVANCE_CONFIG:
			{
				uvcx_video_advance_config_t *conf = data;
				DBG ("  [[ UVCX_VIDEO_ADVANCE_CONFIG ]]\n");
				DBG ("wLayerID                   : %X\n",		conf->wLayerID);
				DBG ("dwMb_max                   : %u\n",		conf->dwMb_max);
				DBG ("blevel_idc                 : %02X\n",		conf->blevel_idc);
				DBG ("bReserved                  : %02X\n",		conf->bReserved);
			}
			break;
		case UVCX_BITRATE_LAYERS:
			{
				uvcx_bitrate_layers_t *conf = data;
				DBG ("  [[ UVCX_BITRATE_LAYERS ]]\n");
				DBG ("wLayerID                   : %X\n",		conf->wLayerID);
				DBG ("dwPeakBitrate              : %u bps\n",	conf->dwPeakBitrate);
				DBG ("dwAverageBitrate           : %u bps\n",	conf->dwAverageBitrate);
			}
			break;
		case UVCX_QP_STEPS_LAYERS:
			{
				uvcx_qp_steps_layers_t *conf = data;
				DBG ("  [[ UVCX_QP_STEPS_LAYERS ]]\n");
				DBG ("wLayerID                   : %X\n",		conf->wLayerID);
				DBG ("bFrameType                 : %02X\n",		conf->bFrameType);
				DBG ("bMinQp                     : %d\n",		conf->bMinQp);
				DBG ("bMaxQp                     : %d\n",		conf->bMaxQp);
			}
			break;
	}
}

static EV4l2Ret xu_h264_get_l3x (v4l2_info_t *info)
{
	struct uvc_xu_control_query ctrl;
	int i, rv, fd=info->vfd;

	for (i=UVCX_VIDEO_CONFIG_PROBE; i<UVCX_LAST; i++)
	{
		if ( i == UVCX_VIDEO_CONFIG_COMMIT ) {
			continue;
		}

		ctrl.unit		= info->h264.unit;
		ctrl.selector	= i;
		ctrl.size		= info->h264.size[i];
		ctrl.data		= (__u8 *)info->h264.selector[i];
		ctrl.query		= UVC_GET_CUR;

		rv = xioctl (fd, UVCIOC_CTRL_QUERY, &ctrl);
		if (rv) {
			ERR ("xioctl ( UVCIOC_CTRL_QUERY selector=%d )\n", i);
			info->h264.size[i] = -1;
			continue;
		}
		dump_xu_h264_value (i, info->h264.selector[i]);
	}
	return EV4L2RV_OK ;
}

static EV4l2Ret xu_h264_set_l3x (v4l2_info_t *info, int selector)
{
	struct uvc_xu_control_query ctrl;
	int rv, fd=info->vfd;

	ctrl.unit		= info->h264.unit;
	ctrl.selector	= selector;
	ctrl.size		= info->h264.size[selector];
	ctrl.data		= (__u8 *)info->h264.selector[selector];
	ctrl.query		= UVC_SET_CUR;

	rv = xioctl (fd, UVCIOC_CTRL_QUERY, &ctrl);
	if (rv) {
		ERR ("xioctl ( UVCIOC_CTRL_QUERY selector=%d )\n", selector);
		return EV4L2RV_ERR_IOCTL ;
	}

	return EV4L2RV_OK ;
}

static v4l2_op_t v4l2Op = {
	.name				= "linux 3.x" ,
	.get_ctrl_list		= get_ctrl_list ,
	.get_ctrl_all		= get_ctrl_all ,
	.set_ctrl			= set_ctrl ,
	.set_ctrl_default	= set_ctrl_default ,
	.xu_h264_init		= xu_h264_init ,
	.xu_h264_get_all	= xu_h264_get_l3x ,
	.xu_h264_set		= xu_h264_set_l3x ,
} ;


static void configForH264 (v4l2_info_t *info)
{
	uvcx_video_config_probe_commit_t *uvcx_cfg = info->h264.selector[UVCX_VIDEO_CONFIG_PROBE];
	uvcx_rate_control_mode_t *uvcx_rate = info->h264.selector[UVCX_RATE_CONTROL_MODE] ;
	uvcx_framerate_config_t *uvcx_framerate = info->h264.selector[UVCX_FRAMERATE_CONFIG] ;
	uvcx_bitrate_layers_t *uvcx_bitrate = info->h264.selector[UVCX_BITRATE_LAYERS] ;

	uvcx_cfg->dwFrameInterval = (int)((1.0/info->param.fps)*10000000.0) ;
	uvcx_cfg->wWidth = info->param.width ;
	uvcx_cfg->wHeight = info->param.height ;
	uvcx_cfg->wIFramePeriod = info->param.iFramePeriod;	// IDR Frame: 1/sec,  Unit: msec
	uvcx_cfg->dwBitRate = info->param.averageBitrate ;
	uvcx_cfg->bRateControlMode = info->param.rateControl ;
	uvcx_cfg->bEntropyCABAC = info->param.entropy ;
	uvcx_cfg->bTimestamp = info->param.timestamp ;

	uvcx_rate->bRateControlMode = info->param.rateControl ;

	uvcx_framerate->dwFrameInterval = uvcx_cfg->dwFrameInterval ;

	uvcx_bitrate->dwPeakBitrate = info->param.peakBitrate ;
	uvcx_bitrate->dwAverageBitrate = info->param.averageBitrate ;

	info->op->xu_h264_set (info, UVCX_VIDEO_CONFIG_PROBE) ;
	info->op->xu_h264_set (info, UVCX_VIDEO_CONFIG_COMMIT) ;
	info->op->xu_h264_set (info, UVCX_RATE_CONTROL_MODE) ;
	info->op->xu_h264_set (info, UVCX_FRAMERATE_CONFIG) ;
	info->op->xu_h264_set (info, UVCX_BITRATE_LAYERS) ;
}

v4l2_info_t *v4l2_create (V4l2Param* param)
{
	v4l2_info_t *info;

	info = malloc (sizeof(*info));
	if ( ! info ) {
		ERR ("malloc ( v4l2_info_t )\n");
		return info;
	}
	memset (info, 0, sizeof(*info));

	do
	{
		memcpy(&info->param, param, sizeof(*param)) ;
		info->vfd		= param->vfd ;
		info->op		= &v4l2Op ;
		info->ctlCnt	= info->op->get_ctrl_list(info);
		info->ctlList	= malloc (sizeof(v4l2_ctrl_list_t) * info->ctlCnt);
		if ( ! info->ctlList ) {
			ERR ("malloc ( sizeof(v4l2_ctrl_list_t) * %d )\n", info->ctlCnt);
			break;
		}
		memset (info->ctlList, 0, sizeof(v4l2_ctrl_list_t) * info->ctlCnt);

		info->op->get_ctrl_list (info);
		info->op->get_ctrl_all (info);
		// info->op->set_ctrl_default (info);

		xu_h264_init_buf (info);
		info->op->xu_h264_init (info);
		info->op->xu_h264_get_all (info);

		configForH264 (info);

		info->op->xu_h264_get_all (info);

		return info;
	}
	while (0) ;

	free (info);
	return NULL;
}


void v4l2_destroy (v4l2_info_t *info)
{
	xu_h264_deinit_buf (info);

	if ( info->ctlList )
	{
		int i;
		v4l2_ctrl_list_t *list;

		for (i=0,list=info->ctlList; i<info->ctlCnt; i++,list++) {
			if ( list->menu ) {
				free (list->menu);
			}
		}
		
		free (info->ctlList);
	}

	free (info);
}

