#ifndef __PI_THREAD_H__
#define __PI_THREAD_H__

#include <pthread.h>

#if 0
#define SET_THREAD_NAME(thread, name)                                                            \
                                    {                                                            \
                                        if ((name) != NULL)                                      \
                                        {                                                        \
                                            pthread_setname_np((thread), (name));                \
                                        }                                                        \
                                    }
#else
#define SET_THREAD_NAME(thread, name)
#endif

enum EThreadParams {
	ETP_MODE_NORMAL		= 0 ,
	ETP_MODE_DETACHED	,
} ;

// Thread
#define CREATE_THREAD(thread, func, stack_size, para, detached)                                  \
                                    {                                                            \
                                        pthread_attr_t thread_attr ;                             \
                                        pthread_attr_init(&thread_attr) ;                        \
                                        pthread_attr_setstacksize(&thread_attr, (stack_size)) ;  \
                                        if (detached)                                            \
                                        {                                                        \
                                            pthread_attr_setdetachstate(&thread_attr, PTHREAD_CREATE_DETACHED) ; \
                                        }                                                        \
                                        pthread_create(&(thread), &thread_attr, (func), (para)) ;\
                                        pthread_attr_destroy(&thread_attr) ;                     \
                                        SET_THREAD_NAME((thread), __FUNCTION__) ;                \
                                    }
#define EXIT_THREAD(err)            pthread_exit(err)

// Mutex
#define INIT_MUTEX(mutex)         pthread_mutex_init(&(mutex), NULL)  //((mutex) = (pthread_mutex_t)PTHREAD_MUTEX_INITIALIZER)
#define INIT_RECURSIVE_MUTEX(mutex)                                                                \
                                    {                                                              \
                                        pthread_mutexattr_t attr ;                                 \
                                        pthread_mutexattr_init(&attr) ;                            \
                                        pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE) ;\
                                        pthread_mutex_init(&(mutex), &attr) ;                      \
                                    }
#define DESTROY_MUTEX(mutex)        pthread_mutex_destroy(&(mutex))
#define TRY_LOCK_MUTEX(mutex)       pthread_mutex_trylock(&(mutex))
#define LOCK_MUTEX(mutex)           pthread_mutex_lock(&(mutex))
#define UNLOCK_MUTEX(mutex)         pthread_mutex_unlock(&(mutex))

// Timeout
#define SET_SIGNAL_TIME_SEC(timeout, sec)														\
									clock_gettime (CLOCK_MONOTONIC, &(timeout));				\
									(timeout).tv_sec += (sec)
#define SET_SIGNAL_TIME_MSEC(timeout, msec)														\
									{															\
										clock_gettime (CLOCK_MONOTONIC, &(timeout)) ;			\
										(timeout).tv_nsec += ((msec) * 1000000) ;				\
										while((timeout).tv_nsec >= 1000000000)					\
										{														\
											(timeout).tv_nsec -= 1000000000 ;					\
											(timeout).tv_sec ++ ;								\
										}														\
									}

// Condition / Signal
#define INIT_SIGNAL(signal)			{															\
										pthread_condattr_t cattr ;								\
										pthread_condattr_init (&cattr) ;						\
										pthread_condattr_setclock (&cattr, CLOCK_MONOTONIC) ;	\
										pthread_cond_init (&(signal), &cattr) ;					\
									}
#define DESTROY_SIGNAL(signal)		pthread_cond_destroy(&(signal))
									
#define WAIT_SIGNAL(signal, mutex)  pthread_cond_wait(&(signal), &(mutex))
#define WAIT_SIGNAL_TIMEOUT(signal, mutex, timeout) \
                                    pthread_cond_timedwait(&(signal), &(mutex), &(timeout))
#define SIGNAL(signal)              pthread_cond_signal(&(signal))
#define SIGNAL_MUTEX(signal, mutex)	LOCK_MUTEX(mutex) ;											\
									SIGNAL(signal) ;											\
									UNLOCK_MUTEX(mutex) ;
#define BROADCAST(signal)           pthread_cond_broadcast(&(signal))


#endif /* __PI_THREAD_H__ */
