/**********
  This library is free software; you can redistribute it and/or modify it under
  the terms of the GNU Lesser General Public License as published by the
  Free Software Foundation; either version 2.1 of the License, or (at your
  option) any later version. (See <http://www.gnu.org/copyleft/lesser.html>.)

  This library is distributed in the hope that it will be useful, but WITHOUT
  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
  more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this library; if not, write to the Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 **********/
// Copyright (c) 1996-2016, Live Networks, Inc.  All rights reserved
// A test program that reads a H.264 Elementary Stream video file
// and streams it using RTP
// main program
//
// NOTE: For this application to work, the H.264 Elementary Stream video file *must* contain SPS and PPS NAL units,
// ideally at or near the start of the file.  These SPS and PPS NAL units are used to specify 'configuration' information
// that is set in the output stream's SDP description (by the RTSP server that is built in to this application).
// Note also that - unlike some other "*Streamer" demo applications - the resulting stream can be received only using a
// RTSP client (such as "openRTSP")

#include <liveMedia.hh>
#include <BasicUsageEnvironment.hh>
#include <GroupsockHelper.hh>

#include "rtspsvr.h"

struct ClientData {
	RTPSink* videoSink ;
	H264VideoStreamFramer* videoSource ;
	ClientData(RTPSink* sink, H264VideoStreamFramer* source) {
		videoSink = sink ;
		videoSource = source ;
	}
} ;

UsageEnvironment* env;


static void announceStream(RTSPServer* rtspServer, ServerMediaSession* sms, char const* streamName, char const* inputFileName) ;
static void play(char const* inputFileName, RTPSink* videoSink) ;

int main(int argc, char** argv)
{
	// Begin by setting up our usage environment:
	TaskScheduler* scheduler = BasicTaskScheduler::createNew();
	env = BasicUsageEnvironment::createNew(*scheduler);

	// Create 'groupsocks' for RTP and RTCP:
	struct in_addr destinationAddress0;
	destinationAddress0.s_addr = chooseRandomIPv4SSMAddress(*env);
	struct in_addr destinationAddress1;
	destinationAddress1.s_addr = chooseRandomIPv4SSMAddress(*env);

	// Note: This is a multicast address.  If you wish instead to stream
	// using unicast, then you should use the "testOnDemandRTSPServer"
	// test program - not this test program - as a model.

	const unsigned short rtpPortNum = 18888;
	const unsigned char ttl = 255;

	const Port rtpPort0(rtpPortNum);
	const Port rtcpPort0(rtpPortNum+1);
	const Port rtpPort1(rtpPortNum+2);
	const Port rtcpPort1(rtpPortNum+3);

	Groupsock rtpGroupsock0(*env, destinationAddress0, rtpPort0, ttl);
	rtpGroupsock0.multicastSendOnly(); // we're a SSM source
	Groupsock rtcpGroupsock0(*env, destinationAddress0, rtcpPort0, ttl);
	rtcpGroupsock0.multicastSendOnly(); // we're a SSM source
	Groupsock rtpGroupsock1(*env, destinationAddress1, rtpPort1, ttl);
	rtpGroupsock1.multicastSendOnly(); // we're a SSM source
	Groupsock rtcpGroupsock1(*env, destinationAddress1, rtcpPort1, ttl);
	rtcpGroupsock1.multicastSendOnly(); // we're a SSM source

	Groupsock* rtpGroupsock[2]  = { &rtpGroupsock0,  &rtpGroupsock1 } ;
	Groupsock* rtcpGroupsock[2] = { &rtcpGroupsock0, &rtcpGroupsock1 } ;


	// Create a 'H264 Video RTP' sink from the RTP 'groupsock':
	// Create (and start) a 'RTCP instance' for this RTP sink:
	const unsigned estimatedSessionBandwidth = 500; // in kbps; for RTCP b/w share
	const unsigned maxCNAMElen = 100;
	unsigned char CNAME[maxCNAMElen+1];
	gethostname((char*)CNAME, maxCNAMElen);
	CNAME[maxCNAMElen] = '\0'; // just in case
	// Note: This starts RTCP running automatically

	RTSPServer* rtspServer = RTSPServer::createNew(*env, 8554);
	if (rtspServer == NULL) {
		*env << "Failed to create RTSP server: " << env->getResultMsg() << "\n";
		exit(1);
	}

	for (int cam=0 ; cam < 2; cam++)
	{
		char streamName[64] ;
		char inputFileName[64] ;
		char const* descriptionString = "Session streamed by \"H264VideoStreamer\"" ;

		snprintf(streamName, sizeof(streamName), FORMAT_STREAM_NAME, cam) ;
		snprintf(inputFileName, sizeof(inputFileName), FORMAT_VIDEO_NAME, cam) ;

		RTPSink* videoSink = H264VideoRTPSink::createNew(*env, rtpGroupsock[cam], 96);
		RTCPInstance* rtcp = RTCPInstance::createNew(*env, rtcpGroupsock[cam], estimatedSessionBandwidth, CNAME, 
													videoSink, NULL /* we're a server */, True /* we're a SSM source */);
		ServerMediaSession* sms = ServerMediaSession::createNew(*env, streamName, inputFileName, descriptionString, True /*SSM*/);
		sms->addSubsession(PassiveServerMediaSubsession::createNew(*videoSink, rtcp));
		rtspServer->addServerMediaSession(sms);

		announceStream(rtspServer, sms, streamName, inputFileName);

		play(inputFileName, videoSink);
	}

	env->taskScheduler().doEventLoop(); // does not return

	return 0; // only to prevent compiler warning
}

static void announceStream(RTSPServer* rtspServer, ServerMediaSession* sms, char const* streamName, char const* inputFileName)
{
	char* url = rtspServer->rtspURL(sms);
	UsageEnvironment& env = rtspServer->envir();
	env << "\n\"" << streamName << "\" stream, from the file \"" << inputFileName << "\"\n"; 
	env << "Play this stream using the URL \"" << url << "\"\n";
	delete[] url;
}

static void afterPlaying(void* handler )
{
	ClientData* clientData = (ClientData*) handler ;
	
	*env << "...done reading from file\n";
	clientData->videoSink->stopPlaying();
	Medium::close(clientData->videoSource);

	delete clientData ;
}

static void play(char const* inputFileName, RTPSink* videoSink)
{

	// Open the input file as a 'byte-stream file source':
	ByteStreamFileSource* fileSource = ByteStreamFileSource::createNew(*env, inputFileName);
	if (fileSource == NULL) {
		*env << "Unable to open file \"" << inputFileName << "\" as a byte-stream file source\n";
		exit(1);
	}

	FramedSource* videoES = fileSource;

	// Create a framer for the Video Elementary Stream:
	H264VideoStreamFramer* videoSource = H264VideoStreamFramer::createNew(*env, videoES);
	ClientData *clientData = new ClientData(videoSink, videoSource) ;

	// Finally, start playing:
	*env << "Beginning to read from file...\n";
	videoSink->startPlaying(*videoSource, afterPlaying, clientData);
}
