#ifndef __V4L2_H264_H__
#define __V4L2_H264_H__

#include "uvch264.h"

struct v4l2_info ;

enum EV4l2Ret
{
	EV4L2RV_OK			= 0 ,
	EV4L2RV_ERR_IOCTL ,
} ;
typedef enum EV4l2Ret EV4l2Ret ;

typedef struct v4l2_control_list
{
	int                     fg_change ;
	struct v4l2_queryctrl   ctrl ;
	__s32                   value ;
	__s64                   value64 ;
	struct v4l2_querymenu   *menu ;

} v4l2_ctrl_list_t ;

typedef struct xu_value
{
	int     unit ;
	__u16   *size ;
	void    *selector[UVCX_LAST] ;

} xu_value_t ;

typedef struct v4l2_operation
{
	char*		name ;
	int			(*get_ctrl_list)(struct v4l2_info *info) ;
	EV4l2Ret	(*get_ctrl_all)(struct v4l2_info *info) ;
	EV4l2Ret	(*set_ctrl)(struct v4l2_info *info, v4l2_ctrl_list_t *list) ;
	EV4l2Ret	(*set_ctrl_default)(struct v4l2_info *info) ;
	EV4l2Ret	(*xu_h264_init)(struct v4l2_info *info) ;
	EV4l2Ret	(*xu_h264_get_all)(struct v4l2_info *info) ;
	EV4l2Ret	(*xu_h264_set)(struct v4l2_info *info, int selector) ;

} v4l2_op_t ;

typedef struct v4l2_info
{
	pthread_cond_t      cond;
	pthread_mutex_t     mutex;
	int					vfd ;

	int                 ctlCnt;
	v4l2_ctrl_list_t    *ctlList;

	xu_value_t          h264;

	v4l2_op_t           *op;

} v4l2_info_t;


#endif /* __V4L2_H264_H__ */
