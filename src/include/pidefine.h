#ifndef __PI_DEFINE_H__
#define __PI_DEFINE_H__

/*****************************************
 * pthread mutex and cond
 *****************************************/
#define mutex_init(x)           pthread_mutex_init(&(x)->mutex, (pthread_mutexattr_t *)NULL)
#define mutex_destroy(x)        pthread_mutex_destroy(&(x)->mutex)

#define cond_init(x)            pthread_cond_init(&(x)->cond, (pthread_condattr_t *)NULL)
#define cond_destroy(x)         pthread_cond_destroy(&(x)->cond)


#endif /* __PI_DEFINE_H__ */
