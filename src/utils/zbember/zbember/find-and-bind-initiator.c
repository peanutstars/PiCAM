//
// find-and-bind-initiator.c
//
// Author: Andrew Keesler <andrew.keesler@silabs.com>
//
// Initiator functionality as described in the Base Device Behavior
// spec.
//
// Copyright 2014 Silicon Laboratories, Inc.                               *80*

#include "app/framework/include/af.h"

#include "stack/include/binding-table.h"
#include "stack/include/event.h"

#include "app/framework/plugin/find-and-bind/find-and-bind.h"

#define EM_AF_PLUGIN_FIND_AND_BIND_INITIATOR_DEBUG

#ifdef  EM_AF_PLUGIN_FIND_AND_BIND_INITIATOR_DEBUG

#define emberAfPluginFindAndBindGetInitiatorEndpointCallback() 1
#define debugPrintln(...) emberAfCorePrintln(__VA_ARGS__)

#else
#define debugPrintln(...)
#endif  /* EM_AF_PLUGIN_FIND_AND_BIND_DEBUG */

// -----------------------------------------------------------------------------
// Constants

PGM int8u emAfFindAndBindPluginName[] = "Find and Bind";

#define INITIATOR_MASK_STATE_MASK              (0x03)
#define INITIATOR_MASK_STATE_OFFSET            (0)
#define INITIATOR_MASK_STATE_NONE    (0 << INITIATOR_MASK_STATE_OFFSET)
#define INITIATOR_MASK_STATE_QUERY   (1 << INITIATOR_MASK_STATE_OFFSET)
#define INITIATOR_MASK_STATE_PROCESS (2 << INITIATOR_MASK_STATE_OFFSET)

#define INITIATOR_MASK_DATA_MASK               (0x0C)
#define INITIATOR_MASK_DATA_OFFSET             (2)
#define INITIATOR_MASK_DATA_NONE (0 << INITIATOR_MASK_DATA_OFFSET)
#define INITIATOR_MASK_DATA_TX   (1 << INITIATOR_MASK_DATA_OFFSET)
#define INITIATOR_MASK_DATA_RX   (2 << INITIATOR_MASK_DATA_OFFSET)

#define INITIATOR_MASK_RESPONSES_MASK          (0x10)
#define INITIATOR_MASK_RESPONSES_OFFSET        (4)
#define INITIATOR_MASK_RESPONSES_FALSE (0 << INITIATOR_MASK_RESPONSES_OFFSET)
#define INITIATOR_MASK_RESPONSES_TRUE  (1 << INITIATOR_MASK_RESPONSES_OFFSET)

#define INITIATOR_MASK_PROCESS_MASK            (0xE0)
#define INITIATOR_MASK_PROCESS_OFFSET          (5)
#define INITIATOR_MASK_PROCESS_NONE  (0 << INITIATOR_MASK_PROCESS_OFFSET)
#define INITIATOR_MASK_PROCESS_IEEE  (1 << INITIATOR_MASK_PROCESS_OFFSET)
#define INITIATOR_MASK_PROCESS_DESCR (2 << INITIATOR_MASK_PROCESS_OFFSET)
#define INITIATOR_MASK_PROCESS_WRITE (4 << INITIATOR_MASK_PROCESS_OFFSET)

#define INITIATOR_MASK_INIT_VALUE                \
  (INITIATOR_MASK_STATE_NONE                     \
   | INITIATOR_MASK_DATA_NONE                    \
   | INITIATOR_MASK_RESPONSES_FALSE              \
   | INITIATOR_MASK_PROCESS_NONE)

// TODO: find a good amount for this value
#define TARGET_RESPONSES_LOG_SIZE 3
#define TARGET_RESPONSES_SIZE     (1 << TARGET_RESPONSES_LOG_SIZE)
#define INVALID_TARGET_RESPONSES_INDEX   TARGET_RESPONSES_SIZE

// TODO: find a good amount for this value
#define BROADCAST_IDENTIFY_QUERY_DELAY_MILLISECONDS (3 * MILLISECOND_TICKS_PER_SECOND)

// -----------------------------------------------------------------------------
// Globals

EmberEventControl emberAfPluginFindAndBindCheckTargetResponsesEventControl;

static int8u initiatorMask;

typedef struct {
  EmberNodeId nodeId;
  int8u endpoint;
} FindAndBindTargetInfo;

static FindAndBindTargetInfo targetResponses[TARGET_RESPONSES_SIZE];
static int8u currentTargetResponsesIndex = INVALID_TARGET_RESPONSES_INDEX;
static EmberEUI64 currentTargetResponseIeeeAddr;

static int8u initiatorEndpoint = EMBER_ZDP_INVALID_ENDPOINT;
static EmberAfProfileId initiatorProfileId = EMBER_AF_INVALID_PROFILE_ID;

// -----------------------------------------------------------------------------
// Private API Prototypes

/* mask */
#define initiatorMaskSet(mask, value)                         \
  CLEARBITS(initiatorMask, mask);                             \
  SETBITS(initiatorMask, value);

#define initiatorMaskRead(mask) READBITS(initiatorMask, mask)

#define initiatorMaskInit()  initiatorMask = INITIATOR_MASK_INIT_VALUE

#define initiatorMaskClean() initiatorMask = 0;

/* state machine */
static void stateMachineRun(void);

static EmberStatus broadcastIdentifyQuery(void);

static EmberStatus sendIeeeAddrRequest(void);
static void handleIeeeAddrResponse(const EmberAfServiceDiscoveryResult *result);

static EmberStatus sendSimpleDescriptorRequest(void);
static void handleSimpleDescriptorResponse(const EmberAfServiceDiscoveryResult *result);

static EmberStatus writeSimpleDescriptorResponse(int16u clusterId);

static void cleanupAndStop(EmberStatus status);

/* target responses hash set */
// Initializes all nodeIds to EMBER_NULL_NODE_ID, so they are "undefined".
void targetResponsesInit();

// Returns true iff the targetInfo was added.
// This means this function will return false if:
//   A targetInfo struct for that source has already been added.
//   The set is full.
static boolean targetResponsesAdd(FindAndBindTargetInfo *targetInfo);

// currentTargetInfoIndex = (set is "empty")
//                          ? (INVALID_TARGET_RESPONSES_INDEX)
//                          : (index of next target info)
static void targetResponsesGetNext();

#define modTargetResponsesSize(n)                                       \
  (n & ~(0xFF << TARGET_RESPONSES_LOG_SIZE))

#define targetResponseHash(targetInfo)                                  \
  (modTargetResponsesSize(0xFF & ((targetInfo).nodeId ^ (targetInfo).endpoint)))

#define targetInfosAreEqual(targetInfo1, targetInfo2)                   \
  ((targetInfo1).nodeId == (targetInfo2).nodeId                         \
   && (targetInfo1).endpoint == (targetInfo2).endpoint)

#define targetInfoIsUndefined(targetInfo)                               \
  ((targetInfo).nodeId == EMBER_NULL_NODE_ID)

#define currentTargetInfoIsNull()                                       \
  (currentTargetResponsesIndex == INVALID_TARGET_RESPONSES_INDEX)

#define currentTargetInfoNodeId                 \
  (targetResponses[currentTargetResponsesIndex].nodeId)
#define currentTargetInfoEndpoint               \
  (targetResponses[currentTargetResponsesIndex].endpoint)
#define currentTargetInfoIeeeAddr               \
  (currentTargetResponseIeeeAddr)

// -----------------------------------------------------------------------------
// Public API

EmberStatus emberAfPluginFindAndBindInitiator(void)
{
  initiatorMaskInit();
  targetResponsesInit();

  emberEventControlSetActive(emberAfPluginFindAndBindCheckTargetResponsesEventControl);

  initiatorMaskSet(INITIATOR_MASK_STATE_MASK,
                   INITIATOR_MASK_STATE_QUERY);
  initiatorMaskSet(INITIATOR_MASK_RESPONSES_MASK,
                   INITIATOR_MASK_RESPONSES_TRUE);

  return EMBER_SUCCESS;
}

void emberAfPluginFindAndBindCheckTargetResponsesEventHandler(void)
{
  emberEventControlSetInactive(emberAfPluginFindAndBindCheckTargetResponsesEventControl);

  // If the state is none, then quit.
  if (!initiatorMaskRead(INITIATOR_MASK_STATE_MASK)) {
    return;
  }

  if ((initiatorMask & INITIATOR_MASK_STATE_QUERY)              // Looking for targets?
      && (initiatorMaskRead(INITIATOR_MASK_RESPONSES_MASK))) {  // Received responses?

    // Then set to check for new responses again later.
    emberEventControlSetDelayMS(emberAfPluginFindAndBindCheckTargetResponsesEventControl,
                                BROADCAST_IDENTIFY_QUERY_DELAY_MILLISECONDS);

  } else if (!initiatorMaskRead(INITIATOR_MASK_PROCESS_MASK)) {

    initiatorMaskSet(INITIATOR_MASK_STATE_MASK,
                     INITIATOR_MASK_STATE_PROCESS);

    targetResponsesGetNext();
    if (!currentTargetInfoIsNull()) {

      initiatorMaskSet(INITIATOR_MASK_PROCESS_MASK,
                       INITIATOR_MASK_PROCESS_IEEE);

    } else {
      // If currentTargetInfo is NULL, then the set is "empty",
      // so we are done!
      cleanupAndStop(EMBER_SUCCESS); // KICKOUT
      return;
    }
  }

  initiatorMaskSet(INITIATOR_MASK_RESPONSES_MASK,
                   INITIATOR_MASK_RESPONSES_FALSE);
  initiatorMaskSet(INITIATOR_MASK_DATA_MASK,
                   INITIATOR_MASK_DATA_NONE);

  stateMachineRun();
}

// I feel like this needs to be given back to the user at the end product.
// This callback seems like it could be very important to any custom application.
// Is there a way that the plugin can get the source node id and the source endpoint
// from the ZCL identify responses? - agkeesle
boolean emberAfPreCommandReceivedCallback(EmberAfClusterCommand *cmd)
{
  if ((cmd->type
       == EMBER_INCOMING_BROADCAST_LOOPBACK)    // Is this from someone else?
      || !(initiatorMaskRead(INITIATOR_MASK_STATE_MASK)
           & INITIATOR_MASK_STATE_QUERY)        // Are you looking for responses?
      || !(initiatorMaskRead(INITIATOR_MASK_DATA_MASK)
           & INITIATOR_MASK_DATA_RX)            // Are you looking for data to rx?
      || (cmd->apsFrame->destinationEndpoint
          != initiatorEndpoint)                 // Does it concern your endpoint?
      || (cmd->apsFrame->profileId
          != initiatorProfileId)                // Does it concern your profileId?
      || (cmd->apsFrame->clusterId
          != ZCL_IDENTIFY_CLUSTER_ID)           // Was this sent to the identify cluster?
      || !(cmd->clusterSpecific)                // Is this a cluster specific command?
      || (cmd->commandId                        // Is the cluster command identify?
          != ZCL_IDENTIFY_QUERY_RESPONSE_COMMAND_ID)
      || (cmd->direction
          != ZCL_DIRECTION_SERVER_TO_CLIENT)) { // Is command from a server?
    return FALSE;
  }

  if (emberAfPreCommandReceivedCustomCallback(cmd)) {
  } else {
	return FALSE ;
  }

  FindAndBindTargetInfo targetInfo;
  targetInfo.nodeId   = cmd->source;
  targetInfo.endpoint = cmd->apsFrame->sourceEndpoint;
  if (targetResponsesAdd(&targetInfo)) {
    initiatorMaskSet(INITIATOR_MASK_RESPONSES_MASK,
                     INITIATOR_MASK_RESPONSES_TRUE);
  }
  return TRUE;
}

// -----------------------------------------------------------------------------
// Target Responses Set (Private) API

void targetResponsesInit()
{
  int8u i;

  for (i = 0; i < TARGET_RESPONSES_SIZE; i ++) {
    targetResponses[i].nodeId = EMBER_NULL_NODE_ID;
  }
}

static boolean targetResponsesAdd(FindAndBindTargetInfo *targetInfo)
{
  int8u i, j;

  if (!targetInfo) {
    return FALSE;
  }

  i = j = targetResponseHash(*targetInfo);
  
  // Look for an open slot, i.e., somewhere that the bind
  // info is undefined.
  do {
    // We will not be removing from the set, so we don't have
    // to worry about this entry moving.
    if (targetInfosAreEqual(*targetInfo, targetResponses[j])) {
      return FALSE;
    }

    if (targetInfoIsUndefined(targetResponses[j])) {
      targetResponses[j].nodeId = targetInfo->nodeId;
      targetResponses[j].endpoint = targetInfo->endpoint;
      debugPrintln("add: {0x%02X, %d} @ %d (%d)",
                   targetInfo->nodeId,
                   targetInfo->endpoint,
                   j,
                   i);
      return TRUE;
    }

    if (++j == TARGET_RESPONSES_SIZE) {
      j = 0;
    }

  } while (j != i);

  return FALSE;
}

static void targetResponsesGetNext()
{
  // Is the target response greater than the target response set size?
  // Then change it back to 0.
  // Otherwise, increment by 1.
  currentTargetResponsesIndex = ((currentTargetResponsesIndex
                                  >= TARGET_RESPONSES_SIZE)
                                 ? 0
                                 : currentTargetResponsesIndex + 1);

  // Search for the next target response in the set that is not undefined.
  // If you get to the end of the set, quit.
  while (targetInfoIsUndefined(targetResponses[currentTargetResponsesIndex])
         && ++currentTargetResponsesIndex < TARGET_RESPONSES_SIZE)
    ; //pass
}

// -----------------------------------------------------------------------------
// Private API

static void stateMachineRun(void)
{  
  EmberStatus status;

  if (initiatorMask & INITIATOR_MASK_STATE_QUERY) {

    initiatorMaskSet(INITIATOR_MASK_DATA_MASK,
                     INITIATOR_MASK_DATA_TX);

    status = broadcastIdentifyQuery();

  } else if (initiatorMask & INITIATOR_MASK_STATE_PROCESS) {
    
    if (initiatorMask & INITIATOR_MASK_PROCESS_IEEE) {

      initiatorMaskSet(INITIATOR_MASK_DATA_MASK,
                       INITIATOR_MASK_DATA_TX);

      status = sendIeeeAddrRequest();

    } else if (initiatorMask & INITIATOR_MASK_PROCESS_DESCR) {

      initiatorMaskSet(INITIATOR_MASK_DATA_MASK,
                       INITIATOR_MASK_DATA_TX);

      status = sendSimpleDescriptorRequest();

    } else {
      debugPrintln("%p: Unidentified process. Mask: 0x%X",
                   emAfFindAndBindPluginName,
                   initiatorMask);
      status = EMBER_BAD_ARGUMENT;
    }
  } else {
    debugPrintln("%p: Unidentified state. Mask: 0x%X",
                 emAfFindAndBindPluginName,
                 initiatorMask);
    status = EMBER_BAD_ARGUMENT;
  }

  if (status != EMBER_SUCCESS) {
    cleanupAndStop(status);
  }
}

static EmberStatus broadcastIdentifyQuery(void)
{
  EmberStatus status;

  if ((initiatorEndpoint
       = emberAfPluginFindAndBindGetInitiatorEndpointCallback())
      == EMBER_ZDP_INVALID_ENDPOINT) {

    debugPrintln("Initiator shutting down: invalid endpoint");
    return EMBER_BAD_ARGUMENT;

  }

  initiatorProfileId // please tell me there is a better way to do this...
    = emberAfProfileIdFromIndex(emberAfIndexFromEndpoint(initiatorEndpoint));
  
  emberAfSetCommandEndpoints(initiatorEndpoint, EMBER_BROADCAST_ENDPOINT);
  emberAfFillCommandIdentifyClusterIdentifyQuery();

  status // BDB wants 0xFFFF
    = emberAfSendCommandBroadcast(EMBER_SLEEPY_BROADCAST_ADDRESS);

  initiatorMaskSet(INITIATOR_MASK_DATA_MASK,
                   INITIATOR_MASK_DATA_RX);

  debugPrintln("%p: Broadcast: 0x%X",
               emAfFindAndBindPluginName,
               status);

  return status;
}

static EmberStatus sendIeeeAddrRequest(void)
{
  EmberStatus status;
  
  if (currentTargetInfoIsNull()) {
    return EMBER_BAD_ARGUMENT;
  }

  status = emberAfFindIeeeAddress(currentTargetInfoNodeId,
                                  handleIeeeAddrResponse);

  initiatorMaskSet(INITIATOR_MASK_DATA_MASK,
                   INITIATOR_MASK_DATA_RX);

  debugPrintln("%p: Ieee request: 0x%X",
               emAfFindAndBindPluginName,
               status);
  
  return status;
}

static void handleIeeeAddrResponse(const EmberAfServiceDiscoveryResult *result)
{
  debugPrintln("%p: Ieee response: 0x%X",
               emAfFindAndBindPluginName,
               result->status);

  if (currentTargetInfoIsNull()
      || (result->status
          != EMBER_AF_UNICAST_SERVICE_DISCOVERY_COMPLETE_WITH_RESPONSE)) {
    cleanupAndStop(EMBER_ERR_FATAL);
    return;
  }

  MEMCOPY(currentTargetInfoIeeeAddr,
          result->responseData,
          EUI64_SIZE);

  initiatorMaskSet(INITIATOR_MASK_DATA_MASK,
                   INITIATOR_MASK_DATA_NONE);
  initiatorMaskSet(INITIATOR_MASK_PROCESS_MASK,
                   INITIATOR_MASK_PROCESS_DESCR);

  emberEventControlSetActive(emberAfPluginFindAndBindCheckTargetResponsesEventControl);
}

static EmberStatus sendSimpleDescriptorRequest()
{
  EmberStatus status;

  status = emberAfFindClustersByDeviceAndEndpoint(currentTargetInfoNodeId,
                                                  currentTargetInfoEndpoint,
                                                  handleSimpleDescriptorResponse);

  initiatorMaskSet(INITIATOR_MASK_DATA_MASK,
                   INITIATOR_MASK_DATA_RX);

  debugPrintln("%p: Descriptor request: 0x%X",
               emAfFindAndBindPluginName,
               status);

  return status;
}

static void handleSimpleDescriptorResponse(const EmberAfServiceDiscoveryResult *result)
{
  EmberStatus status = EMBER_SUCCESS;
  int8u i;
  EmberAfClusterList *clusterList = (EmberAfClusterList *)(result->responseData);

  debugPrintln("%p: Descriptor response: 0x%X",
               emAfFindAndBindPluginName,
               result->status);

  if (currentTargetInfoIsNull()
      || (result->status
          != EMBER_AF_UNICAST_SERVICE_DISCOVERY_COMPLETE_WITH_RESPONSE)
      || !clusterList) {
    cleanupAndStop(EMBER_ERR_FATAL);
    return;
  }

  initiatorMaskSet(INITIATOR_MASK_DATA_MASK,
                   INITIATOR_MASK_DATA_NONE);
  initiatorMaskSet(INITIATOR_MASK_PROCESS_MASK,
                   INITIATOR_MASK_PROCESS_WRITE);

  i = 0;
  while ((status != EMBER_TABLE_FULL) && (i < clusterList->inClusterList[i])) {
    if (emberAfContainsClient(initiatorEndpoint, clusterList->inClusterList[i])
        && emberAfPluginFindAndBindFoundBindTargetCallback(currentTargetInfoNodeId,
                                                           currentTargetInfoEndpoint,
                                                           currentTargetInfoIeeeAddr,
                                                           clusterList->inClusterList[i])) {
        
        status = writeSimpleDescriptorResponse(clusterList->inClusterList[i]);
        debugPrintln("write cluster 0x%2X: 0x%X",
                     clusterList->inClusterList[i],
                     status);
    }
    ++ i;
  }

  i = 0;
  while ((status != EMBER_TABLE_FULL) && (i < clusterList->outClusterList[i])) {
    if (emberAfContainsServer(initiatorEndpoint, clusterList->outClusterList[i])
        && emberAfPluginFindAndBindFoundBindTargetCallback(currentTargetInfoNodeId,
                                                           currentTargetInfoEndpoint,
                                                           currentTargetInfoIeeeAddr,
                                                           clusterList->inClusterList[i])) {
      status = writeSimpleDescriptorResponse(clusterList->outClusterList[i]);
      debugPrintln("write cluster 0x%2X: 0x%X",
                   clusterList->outClusterList[i],
                   status);
    }
    ++ i;
  }
 
  // Done with processing this target response.
  initiatorMaskSet(INITIATOR_MASK_PROCESS_MASK,
                   INITIATOR_MASK_PROCESS_NONE);

  emberEventControlSetActive(emberAfPluginFindAndBindCheckTargetResponsesEventControl);
}

static EmberStatus writeSimpleDescriptorResponse(int16u clusterId)
{
  static int8u tableIndex = 0;
  EmberStatus status = EMBER_TABLE_FULL;
  EmberBindingTableEntry entry;

  while (tableIndex < EMBER_BINDING_TABLE_SIZE) {
    status = emberGetBinding(tableIndex, &entry);
    if (status != EMBER_SUCCESS) {
      return status;
    } else if (entry.type == EMBER_UNUSED_BINDING) {

      entry
        = (EmberBindingTableEntry)
        {EMBER_UNICAST_BINDING,                              // type
         initiatorEndpoint,                                  // local
         clusterId,                                          // clusterId
         currentTargetInfoEndpoint,                          // remote
         0,                                                  // identifier
         emberAfNetworkIndexFromEndpoint(initiatorEndpoint), // networkIndex
        };
      MEMCOPY(entry.identifier,
              currentTargetResponseIeeeAddr,
              EUI64_SIZE);

      status = emberSetBinding(tableIndex, &entry);
      emberSetBindingRemoteNodeId(tableIndex, currentTargetInfoNodeId);
      break;
    }

    ++ tableIndex;
  }
  
  return status;
}

static void cleanupAndStop(EmberStatus status)
{
  debugPrintln("%p: Stop. Status: 0x%X, Mask: 0x%X",
               emAfFindAndBindPluginName,
               status,
               initiatorMask);

  emberAfPluginFindAndBindInitiatorCompleteCallback(status);

  initiatorMaskClean();
}
